import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../features/auth/providers/auth_providers.dart';
import '../../features/onboarding/data/me.dart';
import '../../features/onboarding/providers/onboarding_providers.dart';

/// Where the user stands between sign-in and the game.
enum AppGate {
  loading,
  unreachable,
  signedOut,
  needsAgeConfirmation,
  underAge,
  needsConsent,
  needsPseudonym,
  ready,
}

/// Onboarding order: age confirmation, consent, pseudonym.
AppGate gateFor({
  required bool signedIn,
  required Me? me,
  required bool? ageConfirmed,
}) {
  if (!signedIn) return AppGate.signedOut;
  if (me == null) return AppGate.loading;
  if (!me.hasValidConsent) {
    return switch (ageConfirmed) {
      null => AppGate.needsAgeConfirmation,
      false => AppGate.underAge,
      true => AppGate.needsConsent,
    };
  }
  if (me.pseudonym == null) return AppGate.needsPseudonym;
  return AppGate.ready;
}

final appGateProvider = Provider<AppGate>((ref) {
  final session = ref.watch(authSessionProvider);
  if (session.isLoading && !session.hasValue) return AppGate.loading;
  if (session.value == null) return AppGate.signedOut;

  final me = ref.watch(meProvider);
  if (me.hasError && !me.isLoading) return AppGate.unreachable;
  return gateFor(
    signedIn: true,
    me: me.isLoading ? null : me.value,
    ageConfirmed: ref.watch(ageConfirmationProvider),
  );
});
