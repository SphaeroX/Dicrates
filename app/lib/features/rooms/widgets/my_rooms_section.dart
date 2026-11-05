import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/router/app_router.dart';
import '../../../core/widgets/form_page.dart';
import '../../../l10n/app_localizations.dart';
import '../data/room.dart';
import '../providers/room_providers.dart';
import 'room_status_text.dart';

/// "My rooms" on the start screen: actions, running and finished rooms.
class MyRoomsSection extends ConsumerWidget {
  const MyRoomsSection({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context);
    final textTheme = Theme.of(context).textTheme;
    final rooms = ref.watch(roomsProvider);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Semantics(
          header: true,
          child: Text(l10n.myRoomsTitle, style: textTheme.titleLarge),
        ),
        const SizedBox(height: 12),
        Wrap(
          spacing: 12,
          runSpacing: 12,
          children: [
            FilledButton.icon(
              onPressed: () => context.push(AppRoutes.createRoom),
              icon: const Icon(Icons.add),
              label: Text(l10n.createRoomButton),
            ),
            OutlinedButton.icon(
              onPressed: () => context.push(AppRoutes.joinRoom),
              icon: const Icon(Icons.login),
              label: Text(l10n.joinRoomButton),
            ),
          ],
        ),
        const SizedBox(height: 16),
        rooms.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (_, _) => ErrorMessage(l10n.roomsLoadFailed),
          data: (list) => _RoomList(rooms: list),
        ),
      ],
    );
  }
}

class _RoomList extends StatelessWidget {
  const _RoomList({required this.rooms});

  final List<Room> rooms;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    if (rooms.isEmpty) {
      return Text(l10n.roomsEmpty, textAlign: TextAlign.center);
    }
    final active = rooms.where((room) => !room.isOver).toList();
    final done = rooms.where((room) => room.isOver).toList();
    final textTheme = Theme.of(context).textTheme;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        for (final (heading, list) in [
          (l10n.roomsActiveHeading, active),
          (l10n.roomsDoneHeading, done),
        ])
          if (list.isNotEmpty) ...[
            Semantics(
              header: true,
              child: Text(heading, style: textTheme.titleMedium),
            ),
            for (final room in list) _RoomTile(room: room),
            const SizedBox(height: 8),
          ],
      ],
    );
  }
}

class _RoomTile extends StatelessWidget {
  const _RoomTile({required this.room});

  final Room room;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    return Card(
      child: ListTile(
        title: Text(room.question?.text ?? room.inviteCode),
        subtitle: Wrap(
          spacing: 12,
          children: [
            Text(roomStatusText(l10n, room)),
            Text(l10n.roomMemberCount(room.memberCount)),
          ],
        ),
        trailing: const Icon(Icons.chevron_right),
        onTap: () => context.push(AppRoutes.room(room.id)),
      ),
    );
  }
}
