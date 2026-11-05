import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/router/app_gate.dart';
import '../../../core/widgets/form_page.dart';
import '../../../l10n/app_localizations.dart';
import '../../onboarding/providers/onboarding_providers.dart';
import '../../onboarding/widgets/sign_out_action.dart';

/// Shown while the session and profile load, or when the backend is down.
class SplashScreen extends ConsumerWidget {
  const SplashScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context);
    final unreachable = ref.watch(appGateProvider) == AppGate.unreachable;

    return FormPage(
      title: l10n.appTitle,
      children: unreachable
          ? [
              ErrorMessage(l10n.backendStatusUnreachable),
              const SizedBox(height: 16),
              FilledButton(
                onPressed: () => ref.invalidate(meProvider),
                child: Text(l10n.retryButton),
              ),
              const SizedBox(height: 12),
              const SignOutButton(),
            ]
          : [
              const Center(child: CircularProgressIndicator()),
              const SizedBox(height: 12),
              Text(l10n.backendStatusChecking, textAlign: TextAlign.center),
            ],
    );
  }
}
