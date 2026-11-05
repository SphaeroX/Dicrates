import 'package:dicrates/features/onboarding/data/pseudonym_rules.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('accepts valid pseudonyms', () {
    for (final value in [
      'Owl',
      'Quiet Owl',
      'Jörg-42',
      'night_fox',
      'Ünal',
      '  Owl  ',
    ]) {
      expect(validatePseudonym(value), isNull, reason: value);
    }
  });

  test('rejects too short and too long pseudonyms', () {
    expect(validatePseudonym('ab'), PseudonymError.tooShort);
    expect(validatePseudonym('   '), PseudonymError.tooShort);
    expect(validatePseudonym('x' * 25), PseudonymError.tooLong);
  });

  test('rejects invalid characters', () {
    for (final value in ['Owl<script>', '@admin', 'Owl  Fox', '_owl', 'owl-']) {
      expect(
        validatePseudonym(value),
        PseudonymError.invalidCharacters,
        reason: value,
      );
    }
  });
}
