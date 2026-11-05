import 'package:dicrates/features/auth/data/auth_repository.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import '../../helpers/fake_auth_repository.dart';
import '../../helpers/fake_backend.dart';
import '../../helpers/pump_app.dart';

void main() {
  late FakeAuthRepository auth;
  late FakeBackend backend;

  Future<void> pumpApp(WidgetTester tester) async {
    await tester.pumpWidget(
      buildTestApp(auth: auth, backend: backend, locale: const Locale('en')),
    );
    await tester.pumpAndSettle();
  }

  Future<void> tapText(WidgetTester tester, String text) async {
    await tester.ensureVisible(find.text(text));
    await tester.tap(find.text(text));
    await tester.pumpAndSettle();
  }

  group('signed out', () {
    setUp(() {
      auth = FakeAuthRepository();
      backend = FakeBackend();
    });

    testWidgets('starts on the login screen', (tester) async {
      await pumpApp(tester);

      expect(find.text('Sign in'), findsWidgets);
      expect(find.text('Welcome to Dicrates'), findsNothing);
    });

    testWidgets('rejects an invalid email address', (tester) async {
      await pumpApp(tester);

      await tester.enterText(find.byType(TextFormField), 'not-an-email');
      await tapText(tester, 'Send code');

      expect(find.text('Please enter a valid email address.'), findsOneWidget);
      expect(auth.codesSentTo, isEmpty);
    });

    testWidgets('email code sign-in leads into onboarding', (tester) async {
      await pumpApp(tester);

      await tester.enterText(find.byType(TextFormField), 'owl@example.test');
      await tapText(tester, 'Send code');
      expect(auth.codesSentTo, ['owl@example.test']);
      expect(find.text('Enter code'), findsOneWidget);

      await tester.enterText(find.byType(TextFormField), '000000');
      await tapText(tester, 'Sign in');
      expect(find.text('This code is wrong or has expired.'), findsOneWidget);

      await tester.enterText(
        find.byType(TextFormField),
        FakeAuthRepository.validCode,
      );
      await tapText(tester, 'Sign in');

      expect(find.text('How old are you?'), findsOneWidget);
    });

    testWidgets('code field validates the format', (tester) async {
      await pumpApp(tester);
      await tester.enterText(find.byType(TextFormField), 'owl@example.test');
      await tapText(tester, 'Send code');

      await tester.enterText(find.byType(TextFormField), '12');
      await tapText(tester, 'Sign in');

      expect(find.text('The code has 6 digits.'), findsOneWidget);
    });

    testWidgets('Google sign-in leads into onboarding', (tester) async {
      await pumpApp(tester);

      await tapText(tester, 'Continue with Google');

      expect(auth.googleSignIns, 1);
      expect(find.text('How old are you?'), findsOneWidget);
    });

    testWidgets('Apple sign-in is hidden while disabled', (tester) async {
      await pumpApp(tester);

      expect(find.text('Continue with Apple'), findsNothing);
    });

    testWidgets('shows a network error when sending fails', (tester) async {
      await pumpApp(tester);
      auth.nextFailure = const AuthFailure(AuthFailureKind.network);

      await tester.enterText(find.byType(TextFormField), 'owl@example.test');
      await tapText(tester, 'Send code');

      expect(find.text('No connection. Please try again.'), findsOneWidget);
      expect(find.text('Enter code'), findsNothing);
    });
  });

  group('signed in without onboarding', () {
    setUp(() {
      auth = FakeAuthRepository(session: FakeAuthRepository.testSession);
      backend = FakeBackend();
    });

    testWidgets('full onboarding: age, consent, pseudonym, home', (
      tester,
    ) async {
      await pumpApp(tester);
      expect(find.text('How old are you?'), findsOneWidget);

      await tapText(tester, 'Yes, I am 18 or older');
      expect(find.text('Your consent'), findsOneWidget);

      await tapText(tester, 'I agree');
      expect(backend.consentBodies.single, {
        'consent_version': '1',
        'age_confirmed': true,
      });
      expect(find.text('Choose a pseudonym'), findsOneWidget);

      await tester.enterText(find.byType(TextFormField), 'Quiet Owl');
      await tapText(tester, 'Save and continue');

      expect(backend.pseudonym, 'Quiet Owl');
      expect(backend.language, 'en');
      expect(find.text('Welcome to Dicrates'), findsOneWidget);
    });

    testWidgets('under 18 cannot continue and never consents', (tester) async {
      await pumpApp(tester);

      await tapText(tester, 'No, I am under 18');

      expect(
        find.text('You need to be at least 18 to use Dicrates.'),
        findsOneWidget,
      );
      expect(backend.consentBodies, isEmpty);

      await tapText(tester, 'Sign out');
      expect(auth.signOuts, 1);
      expect(find.text('Send code'), findsOneWidget);
    });

    testWidgets('declining consent does not lead into the game', (
      tester,
    ) async {
      await pumpApp(tester);
      await tapText(tester, 'Yes, I am 18 or older');

      await tapText(tester, 'I do not agree');

      expect(
        find.textContaining('Without your consent you cannot take part'),
        findsOneWidget,
      );
      expect(find.text('Welcome to Dicrates'), findsNothing);
      expect(backend.consentBodies, isEmpty);
    });

    testWidgets('pseudonym is validated before saving', (tester) async {
      backend.consentVersion = FakeBackend.currentConsentVersion;
      await pumpApp(tester);
      expect(find.text('Choose a pseudonym'), findsOneWidget);

      await tester.enterText(find.byType(TextFormField), 'ab');
      await tapText(tester, 'Save and continue');
      expect(find.text('At least 3 characters, please.'), findsOneWidget);

      await tester.enterText(find.byType(TextFormField), 'Owl<3');
      await tapText(tester, 'Save and continue');
      expect(
        find.text('Use letters, digits, single spaces, - and _ only.'),
        findsOneWidget,
      );
      expect(backend.pseudonym, isNull);
    });

    testWidgets('German UI saves German as profile language', (tester) async {
      backend.consentVersion = FakeBackend.currentConsentVersion;
      await tester.pumpWidget(
        buildTestApp(auth: auth, backend: backend, locale: const Locale('de')),
      );
      await tester.pumpAndSettle();

      await tester.enterText(find.byType(TextFormField), 'Stille Eule');
      await tapText(tester, 'Speichern und weiter');

      expect(backend.language, 'de');
      expect(find.text('Willkommen bei Dicrates'), findsOneWidget);
    });

    testWidgets('unreachable backend shows retry on the splash screen', (
      tester,
    ) async {
      backend.reachable = false;
      await pumpApp(tester);

      expect(find.text('Server not reachable'), findsOneWidget);

      backend
        ..reachable = true
        ..consentVersion = FakeBackend.currentConsentVersion
        ..pseudonym = 'Owl';
      await tapText(tester, 'Try again');

      expect(find.text('Welcome to Dicrates'), findsOneWidget);
    });
  });

  group('onboarded', () {
    setUp(() {
      auth = FakeAuthRepository(session: FakeAuthRepository.testSession);
      backend = onboardedBackend();
    });

    testWidgets('goes straight to home and can sign out', (tester) async {
      await pumpApp(tester);
      expect(find.text('Welcome to Dicrates'), findsOneWidget);

      await tester.tap(find.byTooltip('Sign out'));
      await tester.pumpAndSettle();

      expect(auth.signOuts, 1);
      expect(find.text('Send code'), findsOneWidget);
    });
  });
}
