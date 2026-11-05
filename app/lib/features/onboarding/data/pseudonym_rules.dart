/// Same rules as the backend (`dicrates/profiles/models.py`).
const pseudonymMinLength = 3;
const pseudonymMaxLength = 24;

/// Version of the consent text (ARB `consentBodyV1`); must match
/// `CURRENT_CONSENT_VERSION` in the backend.
const currentConsentVersion = '1';

/// Placeholder until the privacy policy is published (Task 25).
const privacyPolicyUrl = 'https://sphaerox.github.io/Dicrates/privacy/';

enum PseudonymError { tooShort, tooLong, invalidCharacters }

final _pattern = RegExp(
  r'^[\p{L}\p{N}](?:[\p{L}\p{N}\p{M}_ \-]*[\p{L}\p{N}\p{M}])?$',
  unicode: true,
);

PseudonymError? validatePseudonym(String value) {
  final trimmed = value.trim();
  if (trimmed.length < pseudonymMinLength) return PseudonymError.tooShort;
  if (trimmed.length > pseudonymMaxLength) return PseudonymError.tooLong;
  if (!_pattern.hasMatch(trimmed) || trimmed.contains('  ')) {
    return PseudonymError.invalidCharacters;
  }
  return null;
}
