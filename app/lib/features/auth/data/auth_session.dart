import 'package:flutter/foundation.dart';

/// The signed-in user as far as the app needs to know it. No email here:
/// the app never needs to show or send it after sign-in.
@immutable
class AuthSession {
  const AuthSession({required this.userId, required this.accessToken});

  final String userId;
  final String accessToken;

  @override
  bool operator ==(Object other) =>
      other is AuthSession &&
      other.userId == userId &&
      other.accessToken == accessToken;

  @override
  int get hashCode => Object.hash(userId, accessToken);
}
