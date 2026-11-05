import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_client_provider.dart';
import '../../auth/providers/auth_providers.dart';
import '../data/me.dart';

/// The caller's profile; `null` while signed out. Re-fetched with
/// `ref.invalidate(meProvider)` after onboarding steps.
final meProvider = FutureProvider<Me?>((ref) async {
  final session = await ref.watch(authSessionProvider.future);
  if (session == null) return null;
  return ref.watch(apiClientProvider).getMe();
}, retry: (retryCount, error) => null);

/// Answer of the age question in this session: `null` unanswered, `true` 18+,
/// `false` under 18. Resets on sign-in/out. Stored in the backend together
/// with the consent.
final ageConfirmationProvider = NotifierProvider<AgeConfirmation, bool?>(
  AgeConfirmation.new,
);

class AgeConfirmation extends Notifier<bool?> {
  @override
  bool? build() {
    ref.watch(authSessionProvider.select((session) => session.value?.userId));
    return null;
  }

  void answer({required bool isAdult}) => state = isAdult;
}
