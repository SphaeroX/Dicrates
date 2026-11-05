import 'dart:async';
import 'dart:io';

import 'package:supabase_flutter/supabase_flutter.dart' as supabase;

import 'auth_repository.dart';
import 'auth_session.dart';

/// Deep link the OAuth providers redirect to (custom scheme, no domain needed).
/// Must be listed in Supabase Auth `additional_redirect_urls`.
const authRedirectUrl = 'io.github.sphaerox.dicrates://login-callback';

class SupabaseAuthRepository implements AuthRepository {
  SupabaseAuthRepository(this._auth);

  final supabase.GoTrueClient _auth;

  static AuthSession? _toSession(supabase.Session? session) => session == null
      ? null
      : AuthSession(userId: session.user.id, accessToken: session.accessToken);

  @override
  AuthSession? get currentSession => _toSession(_auth.currentSession);

  @override
  Stream<AuthSession?> sessionChanges() async* {
    yield currentSession;
    yield* _auth.onAuthStateChange.map((state) => _toSession(state.session));
  }

  Future<T> _guard<T>(Future<T> Function() action) async {
    try {
      return await action();
    } on supabase.AuthException catch (error) {
      final code = error.code;
      if (code == 'otp_expired' ||
          code == 'invalid_credentials' ||
          error.statusCode == '403') {
        throw const AuthFailure(AuthFailureKind.invalidCode);
      }
      throw const AuthFailure(AuthFailureKind.unknown);
    } on SocketException {
      throw const AuthFailure(AuthFailureKind.network);
    } on TimeoutException {
      throw const AuthFailure(AuthFailureKind.network);
    }
  }

  @override
  Future<void> sendEmailCode(String email) =>
      _guard(() => _auth.signInWithOtp(email: email, shouldCreateUser: true));

  @override
  Future<void> verifyEmailCode({
    required String email,
    required String code,
  }) => _guard(
    () => _auth.verifyOTP(
      email: email,
      token: code,
      type: supabase.OtpType.email,
    ),
  );

  @override
  Future<void> signInWithGoogle() => _guard(
    () => _auth.signInWithOAuth(
      supabase.OAuthProvider.google,
      redirectTo: authRedirectUrl,
    ),
  );

  @override
  Future<void> signInWithApple() => _guard(
    () => _auth.signInWithOAuth(
      supabase.OAuthProvider.apple,
      redirectTo: authRedirectUrl,
    ),
  );

  @override
  Future<void> signOut() => _guard(_auth.signOut);
}
