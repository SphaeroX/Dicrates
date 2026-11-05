import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/config/app_config.dart';
import '../../../core/router/app_router.dart';
import '../../../core/widgets/form_page.dart';
import '../../../l10n/app_localizations.dart';
import '../data/auth_repository.dart';
import '../providers/auth_providers.dart';
import 'auth_failure_text.dart';

final _emailPattern = RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$');

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  late final _email = TextEditingController(text: ref.read(loginEmailProvider));
  bool _busy = false;
  AuthFailure? _failure;

  @override
  void dispose() {
    _email.dispose();
    super.dispose();
  }

  Future<void> _run(Future<void> Function() action) async {
    setState(() {
      _busy = true;
      _failure = null;
    });
    try {
      await action();
    } on AuthFailure catch (failure) {
      if (mounted) setState(() => _failure = failure);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _sendCode() async {
    if (!_formKey.currentState!.validate()) return;
    final email = _email.text.trim();
    await _run(() async {
      await ref.read(authRepositoryProvider).sendEmailCode(email);
      ref.read(loginEmailProvider.notifier).set(email);
      if (mounted) await context.push(AppRoutes.loginCode);
    });
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final auth = ref.read(authRepositoryProvider);
    final appleEnabled = ref.watch(appConfigProvider).enableAppleSignIn;
    final failure = _failure;

    return FormPage(
      title: l10n.loginTitle,
      children: [
        Text(l10n.loginIntro, style: Theme.of(context).textTheme.bodyLarge),
        const SizedBox(height: 24),
        Form(
          key: _formKey,
          child: TextFormField(
            controller: _email,
            enabled: !_busy,
            keyboardType: TextInputType.emailAddress,
            autofillHints: const [AutofillHints.email],
            textInputAction: TextInputAction.send,
            onFieldSubmitted: (_) => _sendCode(),
            decoration: InputDecoration(
              labelText: l10n.emailLabel,
              border: const OutlineInputBorder(),
            ),
            validator: (value) => _emailPattern.hasMatch(value?.trim() ?? '')
                ? null
                : l10n.emailInvalid,
          ),
        ),
        const SizedBox(height: 16),
        FilledButton(
          onPressed: _busy ? null : _sendCode,
          child: Text(l10n.sendCodeButton),
        ),
        if (failure != null) ...[
          const SizedBox(height: 16),
          ErrorMessage(authFailureText(l10n, failure)),
        ],
        const SizedBox(height: 24),
        Row(
          children: [
            const Expanded(child: Divider()),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12),
              child: Text(l10n.orDivider),
            ),
            const Expanded(child: Divider()),
          ],
        ),
        const SizedBox(height: 24),
        OutlinedButton.icon(
          onPressed: _busy ? null : () => _run(auth.signInWithGoogle),
          icon: const Icon(Icons.account_circle_outlined),
          label: Text(l10n.continueWithGoogle),
        ),
        if (appleEnabled) ...[
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: _busy ? null : () => _run(auth.signInWithApple),
            icon: const Icon(Icons.apple),
            label: Text(l10n.continueWithApple),
          ),
        ],
      ],
    );
  }
}
