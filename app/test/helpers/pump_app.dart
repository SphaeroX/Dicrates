import 'package:dicrates/app.dart';
import 'package:dicrates/features/home/data/backend_health.dart';
import 'package:dicrates/features/home/providers/backend_health_provider.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_riverpod/misc.dart' show Override;

/// Builds the full app with fake providers, for widget and golden tests.
Widget buildTestApp({
  BackendHealth health = const BackendHealth.connected(version: '0.1.0'),
  ThemeMode themeMode = ThemeMode.light,
  Locale? locale,
  List<Override> overrides = const [],
}) {
  return ProviderScope(
    overrides: [
      backendHealthProvider.overrideWith((ref) async => health),
      ...overrides,
    ],
    child: DicratesApp(themeMode: themeMode, locale: locale),
  );
}
