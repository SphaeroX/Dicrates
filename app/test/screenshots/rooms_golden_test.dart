import 'package:alchemist/alchemist.dart';
import 'package:dicrates/features/rooms/data/room.dart';
import 'package:dicrates/features/rooms/providers/room_providers.dart';
import 'package:dicrates/features/rooms/widgets/create_room_screen.dart';
import 'package:dicrates/features/rooms/widgets/join_room_screen.dart';
import 'package:dicrates/features/rooms/widgets/room_screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/misc.dart' show Override;
import 'package:flutter_test/flutter_test.dart';

import '../helpers/demo_questions.dart';
import '../helpers/pump_app.dart';
import '../helpers/screen_app.dart';
import 'screen_sizes.dart';

Room demoRoom({
  String status = 'FORMING',
  int members = 2,
  bool isCreator = true,
}) => Room.fromJson({
  'id': 'room-1',
  'status': status,
  'language': 'en',
  'question': demoQuestionJson(),
  'round_duration_hours': 24,
  'invite_code': 'K7M2QX',
  'member_count': members,
  'min_members': 3,
  'max_members': 6,
  'is_creator': isCreator,
  'created_at': '2026-11-05T12:00:00Z',
  'started_at': null,
});

void main() {
  final questions = [demoQuestion(), demoQuestion(topicArea: 'environment')];
  final roomScreens = <String, (Widget, List<Override>)>{
    'create_room': (
      const CreateRoomScreen(),
      [questionsProvider.overrideWith((ref, filter) async => questions)],
    ),
    'join_room': (const JoinRoomScreen(initialCode: 'K7M2QX'), const []),
    'lobby_creator_waiting': (
      const RoomScreen(roomId: 'room-1'),
      [roomProvider.overrideWith((ref, id) async => demoRoom())],
    ),
    'lobby_creator_ready': (
      const RoomScreen(roomId: 'room-1'),
      [roomProvider.overrideWith((ref, id) async => demoRoom(members: 4))],
    ),
    'lobby_member': (
      const RoomScreen(roomId: 'room-1'),
      [
        roomProvider.overrideWith(
          (ref, id) async => demoRoom(members: 3, isCreator: false),
        ),
      ],
    ),
  };

  group('room screens', () {
    for (final MapEntry(key: screenName, value: (screen, overrides))
        in roomScreens.entries) {
      for (final (themeMode, screenSize) in goldenVariants) {
        final name = '${screenName}_${variantName(themeMode, screenSize)}';
        goldenTest(
          'renders $name',
          fileName: name,
          constraints: BoxConstraints.tight(screenSize.size),
          builder: () => buildScreenApp(
            screen,
            themeMode: themeMode,
            overrides: overrides,
          ),
        );
      }
    }

    for (final (themeMode, screenSize) in goldenVariants) {
      final name = 'home_with_rooms_${variantName(themeMode, screenSize)}';
      goldenTest(
        'renders $name',
        fileName: name,
        constraints: BoxConstraints.tight(screenSize.size),
        builder: () {
          final backend = onboardedBackend();
          backend.roomsApi.questions.add(demoQuestionJson());
          final running = backend.roomsApi.addForeignRoom(
            code: 'RUN234',
            status: 'R2_OPEN',
            members: 4,
          );
          final forming = backend.roomsApi.addForeignRoom(code: 'K7M2QX');
          final done = backend.roomsApi.addForeignRoom(
            code: 'END234',
            status: 'FINISHED',
            members: 5,
          );
          backend.roomsApi.mine.addAll([done, running, forming]);
          return buildTestApp(
            backend: backend,
            themeMode: themeMode,
            locale: const Locale('en'),
          );
        },
      );
    }
  });
}
