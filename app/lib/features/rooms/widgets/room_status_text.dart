import '../../../l10n/app_localizations.dart';
import '../data/room.dart';

String roomStatusText(AppLocalizations l10n, Room room) => switch (room.phase) {
  RoomPhase.forming => l10n.roomStatusForming,
  RoomPhase.running => l10n.roomStatusRunning,
  RoomPhase.finished => l10n.roomStatusFinished,
  RoomPhase.aborted => l10n.roomStatusAborted,
};
