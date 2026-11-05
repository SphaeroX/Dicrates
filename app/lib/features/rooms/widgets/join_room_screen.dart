import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/api_client_provider.dart';
import '../../../core/router/app_router.dart';
import '../../../core/widgets/form_page.dart';
import '../../../l10n/app_localizations.dart';
import '../data/invite_code.dart';
import '../providers/room_providers.dart';

class JoinRoomScreen extends ConsumerStatefulWidget {
  const JoinRoomScreen({super.key, this.initialCode});

  /// Prefilled from an invite link.
  final String? initialCode;

  @override
  ConsumerState<JoinRoomScreen> createState() => _JoinRoomScreenState();
}

class _JoinRoomScreenState extends ConsumerState<JoinRoomScreen> {
  final _formKey = GlobalKey<FormState>();
  late final _code = TextEditingController(text: widget.initialCode ?? '');
  bool _busy = false;
  String? _error;

  @override
  void dispose() {
    _code.dispose();
    super.dispose();
  }

  String _errorText(AppLocalizations l10n, ApiException error) =>
      switch (error.detail) {
        'room_not_found' => l10n.joinErrorNotFound,
        'room_full' => l10n.joinErrorFull,
        'room_already_started' => l10n.joinErrorStarted,
        _ => l10n.genericError,
      };

  Future<void> _join(AppLocalizations l10n) async {
    if (!_formKey.currentState!.validate()) return;
    final code = normalizeInviteCode(_code.text)!;
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      final room = await ref.read(apiClientProvider).joinRoom(code);
      ref.invalidate(roomsProvider);
      if (mounted) context.pushReplacement(AppRoutes.room(room.id));
    } on ApiException catch (error) {
      if (mounted) setState(() => _error = _errorText(l10n, error));
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final error = _error;

    return FormPage(
      title: l10n.joinRoomTitle,
      children: [
        Form(
          key: _formKey,
          child: TextFormField(
            controller: _code,
            enabled: !_busy,
            textCapitalization: TextCapitalization.characters,
            autocorrect: false,
            enableSuggestions: false,
            textInputAction: TextInputAction.go,
            onFieldSubmitted: (_) => _join(l10n),
            style: Theme.of(context).textTheme.headlineSmall,
            decoration: InputDecoration(
              labelText: l10n.inviteCodeLabel,
              hintText: l10n.inviteCodeHint,
              border: const OutlineInputBorder(),
            ),
            validator: (value) => normalizeInviteCode(value ?? '') == null
                ? l10n.inviteCodeInvalid
                : null,
          ),
        ),
        const SizedBox(height: 16),
        FilledButton(
          onPressed: _busy ? null : () => _join(l10n),
          child: Text(l10n.joinRoomSubmit),
        ),
        if (error != null) ...[const SizedBox(height: 16), ErrorMessage(error)],
      ],
    );
  }
}
