import 'package:flutter/foundation.dart';

import '../../questions/data/question.dart';

enum RoomPhase { forming, running, finished, aborted }

/// A room as its members see it (`/rooms`): counts only, never who is in it.
@immutable
class Room {
  const Room({
    required this.id,
    required this.status,
    required this.language,
    required this.question,
    required this.roundDurationHours,
    required this.inviteCode,
    required this.memberCount,
    required this.minMembers,
    required this.maxMembers,
    required this.isCreator,
  });

  factory Room.fromJson(Map<String, Object?> json) => Room(
    id: json['id']! as String,
    status: json['status']! as String,
    language: json['language']! as String,
    question: switch (json['question']) {
      final Map<String, Object?> question => Question.fromJson(question),
      _ => null,
    },
    roundDurationHours: json['round_duration_hours']! as int,
    inviteCode: json['invite_code']! as String,
    memberCount: json['member_count']! as int,
    minMembers: json['min_members']! as int,
    maxMembers: json['max_members']! as int,
    isCreator: json['is_creator']! as bool,
  );

  final String id;

  /// Backend state machine value, e.g. `FORMING`, `R1_OPEN`, `FINISHED`.
  final String status;
  final String language;
  final Question? question;
  final int roundDurationHours;
  final String inviteCode;
  final int memberCount;
  final int minMembers;
  final int maxMembers;
  final bool isCreator;

  RoomPhase get phase => switch (status) {
    'FORMING' => RoomPhase.forming,
    'FINISHED' || 'ARCHIVED' => RoomPhase.finished,
    'ABORTED' => RoomPhase.aborted,
    _ => RoomPhase.running,
  };

  bool get isOver => phase == RoomPhase.finished || phase == RoomPhase.aborted;

  bool get canStart =>
      isCreator && phase == RoomPhase.forming && memberCount >= minMembers;
}

/// Round durations offered when creating a room (backend accepts the same).
const roundDurationsHours = [1, 6, 12, 24, 48];
const defaultRoundDurationHours = 24;
