import 'package:dicrates/app.dart';
import 'package:dicrates/core/theme/app_theme.dart';
import 'package:dicrates/features/auth/providers/auth_providers.dart';
import 'package:dicrates/l10n/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_riverpod/misc.dart' show Override;

import 'fake_auth_repository.dart';

/// Renders a single screen with the app theme and localizations, without the
/// router, for golden tests of screens that are hard to reach by navigation.
Widget buildScreenApp(
  Widget screen, {
  ThemeMode themeMode = ThemeMode.light,
  Locale locale = const Locale('en'),
  List<Override> overrides = const [],
}) {
  return ProviderScope(
    overrides: [
      authRepositoryProvider.overrideWithValue(
        FakeAuthRepository(session: FakeAuthRepository.testSession),
      ),
      ...overrides,
    ],
    child: MaterialApp(
      theme: AppTheme.light(),
      darkTheme: AppTheme.dark(),
      themeMode: themeMode,
      locale: locale,
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: supportedAppLocales,
      debugShowCheckedModeBanner: false,
      home: screen,
    ),
  );
}
