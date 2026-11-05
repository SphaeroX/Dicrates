import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Build-time configuration passed with `--dart-define`.
///
/// Only public values belong here; never the Supabase service role key.
@immutable
class AppConfig {
  const AppConfig({
    required this.apiBaseUrl,
    required this.supabaseUrl,
    required this.supabaseAnonKey,
    this.enableAppleSignIn = false,
  });

  /// Reads the values given via `--dart-define=NAME=value`.
  const AppConfig.fromEnvironment()
    : apiBaseUrl = const String.fromEnvironment(
        'API_BASE_URL',
        defaultValue: 'http://127.0.0.1:8000',
      ),
      supabaseUrl = const String.fromEnvironment('SUPABASE_URL'),
      supabaseAnonKey = const String.fromEnvironment('SUPABASE_ANON_KEY'),
      enableAppleSignIn = const bool.fromEnvironment('ENABLE_APPLE_SIGN_IN');

  final String apiBaseUrl;
  final String supabaseUrl;
  final String supabaseAnonKey;

  /// Sign in with Apple needs an Apple Developer account; off until then.
  final bool enableAppleSignIn;

  bool get hasSupabase => supabaseUrl.isNotEmpty && supabaseAnonKey.isNotEmpty;
}

final appConfigProvider = Provider<AppConfig>(
  (ref) => const AppConfig.fromEnvironment(),
);
