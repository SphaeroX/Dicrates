import 'package:dicrates/core/router/app_gate.dart';
import 'package:dicrates/core/router/app_router.dart';
import 'package:dicrates/features/onboarding/data/me.dart';
import 'package:flutter_test/flutter_test.dart';

Me me({String? pseudonym, bool consented = false}) => Me(
  id: 'user-1',
  pseudonym: pseudonym,
  language: 'en',
  hasValidConsent: consented,
);

void main() {
  group('gateFor', () {
    test('signed out', () {
      expect(
        gateFor(signedIn: false, me: null, ageConfirmed: null),
        AppGate.signedOut,
      );
    });

    test('profile still loading', () {
      expect(
        gateFor(signedIn: true, me: null, ageConfirmed: null),
        AppGate.loading,
      );
    });

    test('order is age, consent, pseudonym', () {
      expect(
        gateFor(signedIn: true, me: me(), ageConfirmed: null),
        AppGate.needsAgeConfirmation,
      );
      expect(
        gateFor(signedIn: true, me: me(), ageConfirmed: true),
        AppGate.needsConsent,
      );
      expect(
        gateFor(signedIn: true, me: me(consented: true), ageConfirmed: null),
        AppGate.needsPseudonym,
      );
      expect(
        gateFor(
          signedIn: true,
          me: me(consented: true, pseudonym: 'Owl'),
          ageConfirmed: null,
        ),
        AppGate.ready,
      );
    });

    test('under 18 is blocked', () {
      expect(
        gateFor(signedIn: true, me: me(), ageConfirmed: false),
        AppGate.underAge,
      );
    });

    test('pseudonym without consent still needs consent', () {
      expect(
        gateFor(signedIn: true, me: me(pseudonym: 'Owl'), ageConfirmed: true),
        AppGate.needsConsent,
      );
    });
  });

  group('redirectFor', () {
    test('signed-out users may use both login routes only', () {
      expect(redirectFor(AppGate.signedOut, AppRoutes.login), isNull);
      expect(redirectFor(AppGate.signedOut, AppRoutes.loginCode), isNull);
      expect(redirectFor(AppGate.signedOut, AppRoutes.home), AppRoutes.login);
      expect(
        redirectFor(AppGate.signedOut, AppRoutes.consent),
        AppRoutes.login,
      );
    });

    test('onboarding steps cannot be skipped', () {
      expect(
        redirectFor(AppGate.needsConsent, AppRoutes.home),
        AppRoutes.consent,
      );
      expect(
        redirectFor(AppGate.needsAgeConfirmation, AppRoutes.consent),
        AppRoutes.age,
      );
      expect(redirectFor(AppGate.underAge, AppRoutes.home), AppRoutes.underAge);
    });

    test('ready users leave login and onboarding for home', () {
      expect(redirectFor(AppGate.ready, AppRoutes.login), AppRoutes.home);
      expect(redirectFor(AppGate.ready, AppRoutes.pseudonym), AppRoutes.home);
      expect(redirectFor(AppGate.ready, AppRoutes.splash), AppRoutes.home);
      expect(redirectFor(AppGate.ready, AppRoutes.home), isNull);
    });

    test('loading and unreachable show the splash screen', () {
      expect(redirectFor(AppGate.loading, AppRoutes.home), AppRoutes.splash);
      expect(
        redirectFor(AppGate.unreachable, AppRoutes.home),
        AppRoutes.splash,
      );
      expect(redirectFor(AppGate.loading, AppRoutes.splash), isNull);
    });
  });
}
