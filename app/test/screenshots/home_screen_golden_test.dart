import 'package:alchemist/alchemist.dart';
import 'package:dicrates/features/home/data/backend_health.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/pump_app.dart';
import 'screen_sizes.dart';

void main() {
  const states = {
    'connected': BackendHealth.connected(version: '0.1.0'),
    'unreachable': BackendHealth.unreachable(),
  };

  group('home screen', () {
    for (final MapEntry(key: stateName, value: health) in states.entries) {
      for (final (themeMode, screenSize) in goldenVariants) {
        final name = 'home_${stateName}_${variantName(themeMode, screenSize)}';
        goldenTest(
          'renders $name',
          fileName: name,
          constraints: BoxConstraints.tight(screenSize.size),
          builder: () => buildTestApp(
            health: health,
            themeMode: themeMode,
            locale: const Locale('en'),
          ),
        );
      }
    }
  });
}
