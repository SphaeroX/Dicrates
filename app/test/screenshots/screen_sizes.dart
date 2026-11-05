import 'package:flutter/material.dart';

/// Logical screen sizes used for screen goldens.
enum ScreenSize {
  phone(Size(390, 844)),
  tablet(Size(834, 1194));

  const ScreenSize(this.size);

  final Size size;
}

/// All theme/size combinations a screen golden is rendered in.
const goldenVariants = [
  (ThemeMode.light, ScreenSize.phone),
  (ThemeMode.dark, ScreenSize.phone),
  (ThemeMode.light, ScreenSize.tablet),
  (ThemeMode.dark, ScreenSize.tablet),
];

String variantName(ThemeMode themeMode, ScreenSize screenSize) =>
    '${themeMode.name}_${screenSize.name}';
