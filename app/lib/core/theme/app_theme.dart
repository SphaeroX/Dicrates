import 'package:flutter/material.dart';

/// Light and dark themes. Material 3 tonal palettes from one seed keep text
/// and container colors at WCAG 2.1 AA contrast; text sizes follow the system
/// text scale (never fixed with `textScaler: TextScaler.noScaling`).
abstract final class AppTheme {
  static const seedColor = Color(0xFF2B5C8A);

  /// Bundled font, so goldens and devices render the same glyphs.
  static const fontFamily = 'Roboto';

  static ThemeData light() => _build(Brightness.light);

  static ThemeData dark() => _build(Brightness.dark);

  static ThemeData _build(Brightness brightness) {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: seedColor,
      brightness: brightness,
    );
    return ThemeData(
      colorScheme: colorScheme,
      fontFamily: fontFamily,
      materialTapTargetSize: MaterialTapTargetSize.padded,
      visualDensity: VisualDensity.standard,
    );
  }
}
