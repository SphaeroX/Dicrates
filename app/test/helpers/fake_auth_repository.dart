import 'dart:async';

import 'package:dicrates/features/auth/data/auth_repository.dart';
import 'package:dicrates/features/auth/data/auth_session.dart';

/// In-memory [AuthRepository]. The valid email code is [validCode].
class FakeAuthRepository implements AuthRepository {
  FakeAuthRepository({this._session});

  static const validCode = '123456';
  static const testSession = AuthSession(
    userId: '00000000-0000-4000-8000-000000000001',
    accessToken: 'fake-access-token',
  );

  final _controller = StreamController<AuthSession?>.broadcast();
  AuthSession? _session;
  final List<String> codesSentTo = [];
  int googleSignIns = 0;
  int signOuts = 0;
  AuthFailure? nextFailure;

  void _emit(AuthSession? session) {
    _session = session;
    _controller.add(session);
  }

  void _throwIfFailing() {
    final failure = nextFailure;
    if (failure != null) {
      nextFailure = null;
      throw failure;
    }
  }

  @override
  AuthSession? get currentSession => _session;

  @override
  Stream<AuthSession?> sessionChanges() async* {
    yield _session;
    yield* _controller.stream;
  }

  @override
  Future<void> sendEmailCode(String email) async {
    _throwIfFailing();
    codesSentTo.add(email);
  }

  @override
  Future<void> verifyEmailCode({
    required String email,
    required String code,
  }) async {
    _throwIfFailing();
    if (code != validCode) {
      throw const AuthFailure(AuthFailureKind.invalidCode);
    }
    _emit(testSession);
  }

  @override
  Future<void> signInWithGoogle() async {
    _throwIfFailing();
    googleSignIns++;
    _emit(testSession);
  }

  @override
  Future<void> signInWithApple() async {
    _throwIfFailing();
    _emit(testSession);
  }

  @override
  Future<void> signOut() async {
    signOuts++;
    _emit(null);
  }
}
