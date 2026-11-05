import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:share_plus/share_plus.dart';

typedef ShareText = Future<void> Function(String text);

/// Opens the system share sheet; overridden in tests.
final shareTextProvider = Provider<ShareText>(
  (ref) => (text) async {
    await SharePlus.instance.share(ShareParams(text: text));
  },
);
