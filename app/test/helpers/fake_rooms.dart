part of 'fake_backend.dart';

/// In-memory `/questions` and `/rooms` endpoints for the signed-in test user.
class FakeRooms {
  FakeRooms(this._json);

  final http.Response Function(Object body, {int status}) _json;

  /// Approved questions served by `GET /questions` (JSON as the API returns it).
  final List<Map<String, Object?>> questions = [];

  /// Rooms by id; `members` counts everyone, `mine` marks the test user's rooms.
  final Map<String, Map<String, Object?>> rooms = {};
  final Set<String> mine = {};
  final List<String> requestedQuestionLanguages = [];
  int _nextId = 1;

  /// Simulates other people joining a room.
  void addMembers(String roomId, int count) {
    final room = rooms[roomId]!;
    room['member_count'] = (room['member_count']! as int) + count;
  }

  /// A room someone else created, joinable with [code].
  String addForeignRoom({
    required String code,
    String status = 'FORMING',
    int members = 2,
  }) {
    final id = _newId();
    rooms[id] = _room(id, code: code, status: status, members: members)
      ..['is_creator'] = false;
    return id;
  }

  String _newId() =>
      '00000000-0000-4000-8000-${(_nextId++).toString().padLeft(12, '0')}';

  Map<String, Object?> _room(
    String id, {
    required String code,
    String status = 'FORMING',
    int members = 1,
    String? questionId,
  }) {
    final question = questions.firstWhere(
      (q) => q['id'] == questionId,
      orElse: () => questions.isEmpty ? <String, Object?>{} : questions.first,
    );
    return {
      'id': id,
      'status': status,
      'language': question['language'] ?? 'en',
      'question': question.isEmpty ? null : question,
      'round_duration_hours': 24,
      'invite_code': code,
      'member_count': members,
      'min_members': 3,
      'max_members': 6,
      'is_creator': true,
      'created_at': '2026-11-05T12:00:00Z',
      'started_at': status == 'FORMING' ? null : '2026-11-05T13:00:00Z',
    };
  }

  http.Response? handle(http.Request request) {
    final path = request.url.path;
    final segments = request.url.pathSegments;
    switch ((request.method, path)) {
      case ('GET', '/questions'):
        final language = request.url.queryParameters['language'];
        final topic = request.url.queryParameters['topic_area'];
        requestedQuestionLanguages.add(language ?? '');
        return _json([
          for (final q in questions)
            if (q['language'] == language &&
                (topic == null || q['topic_area'] == topic))
              q,
        ]);
      case ('GET', '/rooms'):
        return _json([for (final id in mine.toList().reversed) rooms[id]!]);
      case ('POST', '/rooms'):
        final body = jsonDecode(request.body) as Map<String, Object?>;
        final id = _newId();
        rooms[id] = _room(
          id,
          code: 'K7M2QX',
          questionId: body['question_id'] as String?,
        )..['round_duration_hours'] = body['round_duration_hours'];
        mine.add(id);
        return _json(rooms[id]!, status: 201);
      case ('POST', '/rooms/join'):
        final code = ((jsonDecode(request.body) as Map)['code'] as String)
            .toUpperCase();
        final entry = rooms.entries.where(
          (e) => e.value['invite_code'] == code,
        );
        if (entry.isEmpty) {
          return _json({'detail': 'room_not_found'}, status: 404);
        }
        final room = entry.first;
        if (mine.contains(room.key)) return _json(room.value);
        if (room.value['status'] != 'FORMING') {
          return _json({'detail': 'room_already_started'}, status: 409);
        }
        if ((room.value['member_count']! as int) >= 6) {
          return _json({'detail': 'room_full'}, status: 409);
        }
        addMembers(room.key, 1);
        mine.add(room.key);
        return _json(room.value);
    }
    if (segments.length >= 2 && segments.first == 'rooms') {
      final room = rooms[segments[1]];
      if (room == null || !mine.contains(segments[1])) {
        return _json({'detail': 'room_not_found'}, status: 404);
      }
      final action = segments.length == 3 ? segments[2] : null;
      switch ((request.method, action)) {
        case ('GET', null):
          return _json(room);
        case ('POST', 'start'):
          if (room['is_creator'] != true) {
            return _json({'detail': 'not_creator'}, status: 403);
          }
          if ((room['member_count']! as int) < 3) {
            return _json({'detail': 'too_few_members'}, status: 409);
          }
          room
            ..['status'] = 'R1_OPEN'
            ..['started_at'] = '2026-11-05T13:00:00Z';
          return _json(room);
        case ('POST', 'leave'):
          if (room['is_creator'] == true) {
            room['status'] = 'ABORTED';
          } else {
            mine.remove(segments[1]);
            addMembers(segments[1], -1);
          }
          return http.Response('', 204);
      }
    }
    return null;
  }
}
