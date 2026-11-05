import 'package:flutter/foundation.dart';

/// The caller's profile from `GET /me`.
@immutable
class Me {
  const Me({
    required this.id,
    required this.pseudonym,
    required this.language,
    required this.hasValidConsent,
  });

  factory Me.fromJson(Map<String, Object?> json) => Me(
    id: json['id']! as String,
    pseudonym: json['pseudonym'] as String?,
    language: json['language']! as String,
    hasValidConsent: json['consent'] != null,
  );

  final String id;
  final String? pseudonym;
  final String language;

  /// The backend only returns a consent that is current and includes the
  /// 18+ confirmation.
  final bool hasValidConsent;

  bool get onboardingComplete => hasValidConsent && pseudonym != null;
}
