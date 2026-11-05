import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/router/app_router.dart';
import 'core/theme/app_theme.dart';
import 'l10n/app_localizations.dart';

/// English first: Flutter falls back to the first supported locale when the
/// system locale is not supported, and English is the base language.
final List<Locale> supportedAppLocales = [
  const Locale('en'),
  ...AppLocalizations.supportedLocales.where(
    (locale) => locale.languageCode != 'en',
  ),
];

class DicratesApp extends ConsumerWidget {
  const DicratesApp({
    super.key,
    this.themeMode = ThemeMode.system,
    this.locale,
  });

  final ThemeMode themeMode;

  /// Fixed locale for tests and screenshots; `null` follows the system.
  final Locale? locale;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MaterialApp.router(
      onGenerateTitle: (context) => AppLocalizations.of(context).appTitle,
      theme: AppTheme.light(),
      darkTheme: AppTheme.dark(),
      themeMode: themeMode,
      locale: locale,
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: supportedAppLocales,
      routerConfig: ref.watch(routerProvider),
      debugShowCheckedModeBanner: false,
    );
  }
}
