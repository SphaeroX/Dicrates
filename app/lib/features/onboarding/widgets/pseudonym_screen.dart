import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/api_client_provider.dart';
import '../../../core/widgets/form_page.dart';
import '../../../l10n/app_localizations.dart';
import '../data/pseudonym_rules.dart';
import '../providers/onboarding_providers.dart';
import 'sign_out_action.dart';

/// Profile languages the backend accepts.
const _profileLanguages = {'en', 'de'};

class PseudonymScreen extends ConsumerStatefulWidget {
  const PseudonymScreen({super.key});

  @override
  ConsumerState<PseudonymScreen> createState() => _PseudonymScreenState();
}

class _PseudonymScreenState extends ConsumerState<PseudonymScreen> {
  final _formKey = GlobalKey<FormState>();
  final _pseudonym = TextEditingController();
  bool _busy = false;
  bool _failed = false;

  @override
  void dispose() {
    _pseudonym.dispose();
    super.dispose();
  }

  String? _validate(AppLocalizations l10n, String? value) =>
      switch (validatePseudonym(value ?? '')) {
        null => null,
        PseudonymError.tooShort => l10n.pseudonymTooShort,
        PseudonymError.tooLong => l10n.pseudonymTooLong,
        PseudonymError.invalidCharacters => l10n.pseudonymInvalidCharacters,
      };

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    final languageCode = Localizations.localeOf(context).languageCode;
    setState(() {
      _busy = true;
      _failed = false;
    });
    try {
      await ref
          .read(apiClientProvider)
          .updateMe(
            pseudonym: _pseudonym.text.trim(),
            language: _profileLanguages.contains(languageCode)
                ? languageCode
                : null,
          );
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

    return FormPage(
      title: l10n.pseudonymTitle,
      actions: const [SignOutAction()],
      children: [
        Text(l10n.pseudonymIntro, style: Theme.of(context).textTheme.bodyLarge),
        const SizedBox(height: 24),
        Form(
          key: _formKey,
          child: TextFormField(
            controller: _pseudonym,
            enabled: !_busy,
            maxLength: pseudonymMaxLength,
            textInputAction: TextInputAction.done,
            onFieldSubmitted: (_) => _save(),
            decoration: InputDecoration(
              labelText: l10n.pseudonymLabel,
              border: const OutlineInputBorder(),
            ),
            validator: (value) => _validate(l10n, value),
          ),
        ),
        const SizedBox(height: 16),
        FilledButton(
          onPressed: _busy ? null : _save,
          child: Text(l10n.saveAndContinueButton),
        ),
        if (_failed) ...[
          const SizedBox(height: 16),
          ErrorMessage(l10n.genericError),
        ],
      ],
    );
  }
}
