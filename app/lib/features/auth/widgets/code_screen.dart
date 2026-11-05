import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/router/app_router.dart';
import '../../../core/widgets/form_page.dart';
import '../../../l10n/app_localizations.dart';
import '../data/auth_repository.dart';
import '../providers/auth_providers.dart';
import 'auth_failure_text.dart';

final _codePattern = RegExp(r'^\d{6}$');

class CodeScreen extends ConsumerStatefulWidget {
  const CodeScreen({super.key});

  @override
  ConsumerState<CodeScreen> createState() => _CodeScreenState();
}

class _CodeScreenState extends ConsumerState<CodeScreen> {
  final _formKey = GlobalKey<FormState>();
  final _code = TextEditingController();
  bool _busy = false;
  AuthFailure? _failure;

  @override
  void dispose() {
    _code.dispose();
    super.dispose();
  }

  void _back() {
    if (context.canPop()) {
      context.pop();
    } else {
      context.go(AppRoutes.login);
    }
  }

  Future<void> _verify(String email) async {
    if (!_formKey.currentState!.validate()) return;
    setState(() {
      _busy = true;
      _failure = null;
    });
    try {
      await ref
          .read(authRepositoryProvider)
          .verifyEmailCode(email: email, code: _code.text.trim());
      ref.read(loginEmailProvider.notifier).set(null);
    } on AuthFailure catch (failure) {
      if (mounted) setState(() => _failure = failure);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final email = ref.watch(loginEmailProvider);
    final failure = _failure;

    return FormPage(
      title: l10n.codeTitle,
      children: [
        if (email != null) ...[
          Text(
            l10n.codeIntro(email),
            style: Theme.of(context).textTheme.bodyLarge,
          ),
          const SizedBox(height: 24),
          Form(
            key: _formKey,
            child: TextFormField(
              controller: _code,
              enabled: !_busy,
              keyboardType: TextInputType.number,
              autofillHints: const [AutofillHints.oneTimeCode],
              inputFormatters: [
                FilteringTextInputFormatter.digitsOnly,
                LengthLimitingTextInputFormatter(6),
              ],
              textInputAction: TextInputAction.done,
              onFieldSubmitted: (_) => _verify(email),
              decoration: InputDecoration(
                labelText: l10n.codeLabel,
                border: const OutlineInputBorder(),
              ),
              validator: (value) => _codePattern.hasMatch(value?.trim() ?? '')
                  ? null
                  : l10n.codeInvalidFormat,
            ),
          ),
          const SizedBox(height: 16),
          FilledButton(
            onPressed: _busy ? null : () => _verify(email),
            child: Text(l10n.verifyCodeButton),
          ),
          if (failure != null) ...[
            const SizedBox(height: 16),
            ErrorMessage(authFailureText(l10n, failure)),
          ],
          const SizedBox(height: 8),
        ],
        TextButton(
          onPressed: _busy ? null : _back,
          child: Text(l10n.useDifferentEmail),
        ),
      ],
    );
  }
}
