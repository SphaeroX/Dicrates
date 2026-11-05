import 'auth_session.dart';

enum AuthFailureKind { invalidCode, network, notConfigured, unknown }

class AuthFailure implements Exception {
  const AuthFailure(this.kind);

  final AuthFailureKind kind;

  @override
  String toString() => 'AuthFailure($kind)';
}

/// Sign-in operations. Implemented with Supabase Auth in production and by a
/// fake in tests. Methods throw [AuthFailure].
abstract interface class AuthRepository {
  AuthSession? get currentSession;

  /// Emits the current session first, then every change.
  Stream<AuthSession?> sessionChanges();

  /// Emails a one-time 6-digit code (creates the account if needed).
  Future<void> sendEmailCode(String email);

  Future<void> verifyEmailCode({required String email, required String code});

  Future<void> signInWithGoogle();

  /// Prepared, but hidden while `ENABLE_APPLE_SIGN_IN` is false.
  Future<void> signInWithApple();

  Future<void> signOut();
}

/// Used when the build has no Supabase configuration (`--dart-define`).
class UnconfiguredAuthRepository implements AuthRepository {
  const UnconfiguredAuthRepository();

  static const _failure = AuthFailure(AuthFailureKind.notConfigured);

  @override
  AuthSession? get currentSession => null;

  @override
  Stream<AuthSession?> sessionChanges() => Stream.value(null);

  @override
  Future<void> sendEmailCode(String email) async => throw _failure;

  @override
  Future<void> verifyEmailCode({
    required String email,
    required String code,
  }) async => throw _failure;

  @override
  Future<void> signInWithGoogle() async => throw _failure;

  @override
  Future<void> signInWithApple() async => throw _failure;

  @override
  Future<void> signOut() async {}
}
