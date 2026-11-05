import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

Set<String> _messageKeys(String path) {
  final json =
      jsonDecode(File(path).readAsStringSync()) as Map<String, Object?>;
  return json.keys.where((key) => !key.startsWith('@')).toSet();
}

void main() {
  test('every ARB file contains all keys of the English template', () {
    final templateKeys = _messageKeys('lib/l10n/app_en.arb');
    final arbFiles = Directory('lib/l10n')
        .listSync()
        .whereType<File>()
        .where((file) => file.path.endsWith('.arb'));

    expect(templateKeys, isNotEmpty);
    for (final file in arbFiles) {
      final missing = templateKeys.difference(_messageKeys(file.path));
      expect(missing, isEmpty, reason: '${file.path} is missing keys');
    }
  });

  test('German ARB file exists', () {
    expect(File('lib/l10n/app_de.arb').existsSync(), isTrue);
  });
}
