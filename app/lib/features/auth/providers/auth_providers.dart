import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/auth_repository.dart';
import '../data/auth_session.dart';

/// Overridden in `main.dart` with the Supabase implementation and in tests
/// with a fake.
final authRepositoryProvider = Provider<AuthRepository>(
  (ref) => const UnconfiguredAuthRepository(),
);

final authSessionProvider = StreamProvider<AuthSession?>(
  (ref) => ref.watch(authRepositoryProvider).sessionChanges(),
);

/// Email address entered on the login screen, kept in memory only (never in
/// the route, never persisted) until the code is verified.
final loginEmailProvider = NotifierProvider<LoginEmail, String?>(
  LoginEmail.new,
);

class LoginEmail extends Notifier<String?> {
  @override
  String? build() => null;

  void set(String? email) => state = email;
}
