import 'package:dicrates/app.dart';
import 'package:dicrates/core/api/api_client.dart';
import 'package:dicrates/core/api/api_client_provider.dart';
import 'package:dicrates/features/auth/providers/auth_providers.dart';
import 'package:dicrates/features/home/data/backend_health.dart';
import 'package:dicrates/features/home/providers/backend_health_provider.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_riverpod/misc.dart' show Override;

import 'fake_auth_repository.dart';
import 'fake_backend.dart';

/// A signed-in user who finished onboarding.
FakeBackend onboardedBackend() =>
    FakeBackend(pseudonym: 'Quiet Owl', consentVersion: '1');

/// Builds the full app with fake auth, a fake backend and fake providers,
/// for widget and golden tests. Defaults: signed in and onboarded.
Widget buildTestApp({
  BackendHealth health = const BackendHealth.connected(version: '0.1.0'),
  ThemeMode themeMode = ThemeMode.light,
  Locale? locale,
  FakeAuthRepository? auth,
  FakeBackend? backend,
  List<Override> overrides = const [],
}) {
  final authRepository =
      auth ?? FakeAuthRepository(session: FakeAuthRepository.testSession);
  final fakeBackend = backend ?? onboardedBackend();
  return ProviderScope(
    overrides: [
      authRepositoryProvider.overrideWithValue(authRepository),
      apiClientProvider.overrideWithValue(
        ApiClient(
          httpClient: fakeBackend.client,
          baseUrl: Uri.parse('http://api.test'),
          accessToken: () async => authRepository.currentSession?.accessToken,
        ),
      ),
      backendHealthProvider.overrideWith((ref) async => health),
      ...overrides,
    ],
    child: DicratesApp(themeMode: themeMode, locale: locale),
  );
}
