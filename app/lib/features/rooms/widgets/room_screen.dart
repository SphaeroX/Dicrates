import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/api_client_provider.dart';
import '../../../core/router/app_router.dart';
import '../../../core/widgets/form_page.dart';
import '../../../l10n/app_localizations.dart';
import '../../questions/widgets/question_card.dart';
import '../data/invite_code.dart';
import '../data/room.dart';
import '../providers/room_providers.dart';
import '../providers/share_provider.dart';
import 'room_status_text.dart';

/// Lobby while the room forms; later the entry point to the rounds.
class RoomScreen extends ConsumerWidget {
  const RoomScreen({super.key, required this.roomId});

  final String roomId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context);
    final room = ref.watch(roomProvider(roomId));

    return FormPage(
      title: l10n.lobbyTitle,
      actions: [
        IconButton(
          tooltip: l10n.refreshButton,
          icon: const Icon(Icons.refresh),
          onPressed: () => ref.invalidate(roomProvider(roomId)),
        ),
      ],
      children: [
        room.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (_, _) => ErrorMessage(l10n.roomNotFound),
          data: (room) => _RoomBody(room: room),
        ),
      ],
    );
  }
}

class _RoomBody extends ConsumerStatefulWidget {
  const _RoomBody({required this.room});

  final Room room;

  @override
  ConsumerState<_RoomBody> createState() => _RoomBodyState();
}

class _RoomBodyState extends ConsumerState<_RoomBody> {
  bool _busy = false;
  bool _failed = false;

  Future<void> _run(Future<void> Function(ApiClient api) action) async {
    setState(() {
      _busy = true;
      _failed = false;
    });
    try {
      await action(ref.read(apiClientProvider));
    } on ApiException {
      if (mounted) setState(() => _failed = true);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final theme = Theme.of(context);
    final room = widget.room;
    final question = room.question;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          roomStatusText(l10n, room),
          style: theme.textTheme.titleMedium,
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 8),
        Semantics(
          liveRegion: true,
          child: Text(
            l10n.lobbyMembers(
              room.memberCount,
              room.maxMembers,
              room.minMembers,
            ),
            textAlign: TextAlign.center,
          ),
        ),
        if (room.phase == RoomPhase.forming) ...[
          const SizedBox(height: 16),
          _Invite(code: room.inviteCode),
          const SizedBox(height: 16),
          if (room.isCreator) ...[
            FilledButton(
              onPressed: _busy || !room.canStart
                  ? null
                  : () => _run((api) async {
                      await api.startRoom(room.id);
                      ref
                        ..invalidate(roomProvider(room.id))
                        ..invalidate(roomsProvider);
                    }),
              child: Text(l10n.startRoomButton),
            ),
            if (!room.canStart) ...[
              const SizedBox(height: 8),
              Text(
                l10n.startRoomNeedsMembers(room.minMembers),
                textAlign: TextAlign.center,
              ),
            ],
          ] else
            Text(l10n.waitingForCreator, textAlign: TextAlign.center),
          const SizedBox(height: 12),
          OutlinedButton(
            onPressed: _busy
                ? null
                : () => _run((api) async {
                    await api.leaveRoom(room.id);
                    ref.invalidate(roomsProvider);
                    if (context.mounted) context.go(AppRoutes.home);
                  }),
            child: Text(
              room.isCreator ? l10n.dissolveRoomButton : l10n.leaveRoomButton,
            ),
          ),
        ] else if (room.phase == RoomPhase.running) ...[
          const SizedBox(height: 16),
          Text(l10n.roomStartedInfo, textAlign: TextAlign.center),
        ],
        if (_failed) ...[
          const SizedBox(height: 16),
          ErrorMessage(l10n.genericError),
        ],
        if (question != null) QuestionCard(question: question),
      ],
    );
  }
}

class _Invite extends ConsumerWidget {
  const _Invite({required this.code});

  final String code;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context);
    final theme = Theme.of(context);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Semantics(
              header: true,
              child: Text(
                l10n.lobbyInviteHeading,
                style: theme.textTheme.titleMedium,
              ),
            ),
            const SizedBox(height: 8),
            Text(l10n.lobbyInviteExplanation),
            const SizedBox(height: 12),
            SelectableText(
              code,
              textAlign: TextAlign.center,
              style: theme.textTheme.displaySmall?.copyWith(letterSpacing: 6),
            ),
            const SizedBox(height: 12),
            Wrap(
              alignment: WrapAlignment.center,
              spacing: 12,
              runSpacing: 8,
              children: [
                FilledButton.tonalIcon(
                  onPressed: () => ref.read(shareTextProvider)(
                    l10n.shareInviteText(code, inviteLink(code).toString()),
                  ),
                  icon: const Icon(Icons.share),
                  label: Text(l10n.shareInviteButton),
                ),
                OutlinedButton.icon(
                  onPressed: () async {
                    final messenger = ScaffoldMessenger.maybeOf(context);
                    await Clipboard.setData(ClipboardData(text: code));
                    messenger?.showSnackBar(
                      SnackBar(content: Text(l10n.codeCopied)),
                    );
                  },
                  icon: const Icon(Icons.copy),
                  label: Text(l10n.copyCodeButton),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
