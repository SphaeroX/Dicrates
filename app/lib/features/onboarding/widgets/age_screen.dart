import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/widgets/form_page.dart';
import '../../../l10n/app_localizations.dart';
import '../providers/onboarding_providers.dart';
import 'sign_out_action.dart';

class AgeScreen extends ConsumerWidget {
  const AgeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context);
    final age = ref.read(ageConfirmationProvider.notifier);

    return FormPage(
      title: l10n.ageTitle,
      actions: const [SignOutAction()],
      children: [
        Text(l10n.ageQuestion, style: Theme.of(context).textTheme.bodyLarge),
        const SizedBox(height: 24),
        FilledButton(
          onPressed: () => age.answer(isAdult: true),
          child: Text(l10n.ageYes),
        ),
        const SizedBox(height: 12),
        OutlinedButton(
          onPressed: () => age.answer(isAdult: false),
          child: Text(l10n.ageNo),
        ),
      ],
    );
  }
}
