import 'package:alchemist/alchemist.dart';
import 'package:dicrates/features/auth/providers/auth_providers.dart';
import 'package:dicrates/features/auth/widgets/code_screen.dart';
import 'package:dicrates/features/auth/widgets/login_screen.dart';
import 'package:dicrates/features/onboarding/widgets/age_screen.dart';
import 'package:dicrates/features/onboarding/widgets/consent_screen.dart';
import 'package:dicrates/features/onboarding/widgets/pseudonym_screen.dart';
import 'package:dicrates/features/onboarding/widgets/under_age_screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/misc.dart' show Override;
import 'package:flutter_test/flutter_test.dart';

import '../helpers/screen_app.dart';
import 'screen_sizes.dart';

class _DemoEmail extends LoginEmail {
  @override
  String? build() => 'owl@example.test';
}

void main() {
  final screens = <String, (Widget, List<Override>)>{
    'login': (const LoginScreen(), const []),
    'login_code': (
      const CodeScreen(),
      [loginEmailProvider.overrideWith(_DemoEmail.new)],
    ),
    'onboarding_age': (const AgeScreen(), const []),
    'onboarding_under_age': (const UnderAgeScreen(), const []),
    'onboarding_consent': (const ConsentScreen(), const []),
    'onboarding_pseudonym': (const PseudonymScreen(), const []),
  };

  group('sign-in and onboarding screens', () {
    for (final MapEntry(key: screenName, value: (screen, overrides))
        in screens.entries) {
      for (final (themeMode, screenSize) in goldenVariants) {
        final name = '${screenName}_${variantName(themeMode, screenSize)}';
        goldenTest(
          'renders $name',
          fileName: name,
          constraints: BoxConstraints.tight(screenSize.size),
          builder: () => buildScreenApp(
            screen,
            themeMode: themeMode,
            overrides: overrides,
          ),
        );
      }
    }
  });
}
