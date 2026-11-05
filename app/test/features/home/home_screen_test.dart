import 'package:dicrates/features/home/data/backend_health.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import '../../helpers/pump_app.dart';

void main() {
  Future<void> pumpWithSystemLocale(WidgetTester tester, Locale locale) async {
    tester.platformDispatcher.localesTestValue = [locale];
    addTearDown(tester.platformDispatcher.clearLocalesTestValue);
    await tester.pumpWidget(buildTestApp());
    await tester.pumpAndSettle();
  }

  testWidgets('shows the English headline for an English system locale', (
    tester,
  ) async {
    await pumpWithSystemLocale(tester, const Locale('en', 'US'));

    expect(find.text('Welcome to Dicrates'), findsOneWidget);
  });

  testWidgets('shows the German headline for a German system locale', (
    tester,
  ) async {
    await pumpWithSystemLocale(tester, const Locale('de', 'DE'));

    expect(find.text('Willkommen bei Dicrates'), findsOneWidget);
  });

  testWidgets('falls back to English for an unsupported system locale', (
    tester,
  ) async {
    await pumpWithSystemLocale(tester, const Locale('fr', 'FR'));

    expect(find.text('Welcome to Dicrates'), findsOneWidget);
  });

  testWidgets('shows the connected status', (tester) async {
    await tester.pumpWidget(buildTestApp(locale: const Locale('en')));
    await tester.pumpAndSettle();

    expect(find.text('Connected to the server'), findsOneWidget);
    expect(find.text('Try again'), findsNothing);
  });

  testWidgets('shows the unreachable status with a retry button', (
    tester,
  ) async {
    await tester.pumpWidget(
      buildTestApp(
        health: const BackendHealth.unreachable(),
        locale: const Locale('en'),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Server not reachable'), findsOneWidget);
    expect(find.text('Try again'), findsOneWidget);
  });

  testWidgets('shows German status texts', (tester) async {
    await tester.pumpWidget(
      buildTestApp(
        health: const BackendHealth.unreachable(),
        locale: const Locale('de'),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Server nicht erreichbar'), findsOneWidget);
    expect(find.text('Erneut versuchen'), findsOneWidget);
  });

  testWidgets('does not overflow with large system text', (tester) async {
    tester.platformDispatcher.textScaleFactorTestValue = 2.0;
    addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);

    await tester.pumpWidget(
      buildTestApp(
        health: const BackendHealth.unreachable(),
        locale: const Locale('de'),
      ),
    );
    await tester.pumpAndSettle();

    expect(tester.takeException(), isNull);
    expect(find.text('Server nicht erreichbar'), findsOneWidget);
  });
}
