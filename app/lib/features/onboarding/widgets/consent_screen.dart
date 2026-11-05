import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/api_client_provider.dart';
import '../../../core/widgets/form_page.dart';
import '../../../l10n/app_localizations.dart';
import '../data/pseudonym_rules.dart';
import '../providers/onboarding_providers.dart';
import 'sign_out_action.dart';

class ConsentScreen extends ConsumerStatefulWidget {
  const ConsentScreen({super.key});

  @override
  ConsumerState<ConsentScreen> createState() => _ConsentScreenState();
}

class _ConsentScreenState extends ConsumerState<ConsentScreen> {
  bool _busy = false;
  bool _declined = false;
  bool _failed = false;

  Future<void> _agree() async {
    setState(() {
      _busy = true;
      _failed = false;
      _declined = false;
    });
    try {
      await ref
          .read(apiClientProvider)
          .giveConsent(consentVersion: currentConsentVersion);
      ref.invalidate(meProvider);
    } on ApiException {
      if (mounted) setState(() => _failed = true);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final textTheme = Theme.of(context).textTheme;

    return FormPage(
      title: l10n.consentTitle,
      actions: const [SignOutAction()],
      children: [
        Text(l10n.consentBodyV1, style: textTheme.bodyLarge),
        const SizedBox(height: 16),
        SelectableText(
          l10n.consentPrivacyPolicy(privacyPolicyUrl),
          style: textTheme.bodyMedium,
        ),
        const SizedBox(height: 24),
        FilledButton(
          onPressed: _busy ? null : _agree,
          child: Text(l10n.consentAgreeButton),
        ),
        const SizedBox(height: 12),
        OutlinedButton(
          onPressed: _busy ? null : () => setState(() => _declined = true),
          child: Text(l10n.consentDeclineButton),
        ),
        if (_failed) ...[
          const SizedBox(height: 16),
          ErrorMessage(l10n.genericError),
        ],
        if (_declined) ...[
          const SizedBox(height: 24),
          Semantics(
            liveRegion: true,
            child: Text(l10n.consentDeclinedInfo, textAlign: TextAlign.center),
          ),
          const SizedBox(height: 12),
          const SignOutButton(),
        ],
      ],
    );
  }
}
