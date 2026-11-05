import 'package:dicrates/core/router/app_router.dart';
import 'package:dicrates/features/questions/data/question.dart';
import 'package:dicrates/features/rooms/data/invite_code.dart';
import 'package:dicrates/features/rooms/providers/share_provider.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';

import '../../helpers/demo_questions.dart';
import '../../helpers/fake_backend.dart';
import '../../helpers/pump_app.dart';

void main() {
  late FakeBackend backend;
  late List<String> shared;

  setUp(() {
    backend = onboardedBackend();
    shared = [];
    backend.roomsApi.questions.addAll([
      demoQuestionJson(),
      demoQuestionJson(
        id: '22222222-2222-4222-8222-222222222222',
        topicArea: 'environment',
        text: 'Should Exampleville plant a tree for every newborn child?',
      ),
      demoQuestionJson(
        id: '33333333-3333-4333-8333-333333333333',
        language: 'de',
        text: 'Soll Beispielstadt den Marktplatz autofrei machen?',
      ),
    ]);
  });

  Future<void> pumpApp(
    WidgetTester tester, {
    Locale locale = const Locale('en'),
  }) async {
    await tester.pumpWidget(
      buildTestApp(
        backend: backend,
        locale: locale,
        overrides: [
          shareTextProvider.overrideWithValue((text) async => shared.add(text)),
        ],
      ),
    );
    await tester.pumpAndSettle();
  }

  Future<void> tapText(WidgetTester tester, String text) async {
    await tester.ensureVisible(find.text(text).last);
    await tester.tap(find.text(text).last);
    await tester.pumpAndSettle();
  }

  GoRouter routerOf(WidgetTester tester) =>
      ProviderScope.containerOf(tester.element(find.byType(MaterialApp)))
          .read(routerProvider);

  testWidgets('home shows the empty room list with both actions', (
    tester,
  ) async {
    await pumpApp(tester);

    expect(find.text('My rooms'), findsOneWidget);
    expect(find.textContaining('You are not in a room yet'), findsOneWidget);
    expect(find.text('Create room'), findsOneWidget);
    expect(find.text('Join with code'), findsOneWidget);
  });

  testWidgets('create a room, invite, wait for members and start', (
    tester,
  ) async {
    await pumpApp(tester);

    await tapText(tester, 'Create room');
    expect(find.text('New room'), findsOneWidget);
    expect(backend.roomsApi.requestedQuestionLanguages.last, 'en');
    expect(
      find.text('Soll Beispielstadt den Marktplatz autofrei machen?'),
      findsNothing,
    );

    await tester.tap(find.widgetWithText(ChoiceChip, 'Environment'));
    await tester.pumpAndSettle();
    expect(
      find.text(
        'Should the town of Exampleville introduce a car-free market square?',
      ),
      findsNothing,
    );
    await tester.tap(find.widgetWithText(ChoiceChip, 'All topics'));
    await tester.pumpAndSettle();
    await tapText(
      tester,
      'Should the town of Exampleville introduce a car-free market square?',
    );
    expect(
      find.text('Facts'),
      findsOneWidget,
    ); // question card of the selection
    await tapText(tester, '6 hours');
    await tapText(tester, 'Create room and invite');

    expect(find.text('K7M2QX'), findsOneWidget);
    expect(
      find.text('1 of 6 members joined (at least 3 needed)'),
      findsOneWidget,
    );
    expect(
      find.text('You can start as soon as 3 members have joined.'),
      findsOneWidget,
    );
    final roomId = backend.roomsApi.mine.single;
    expect(backend.roomsApi.rooms[roomId]!['round_duration_hours'], 6);

    await tapText(tester, 'Share invite');
    expect(shared.single, contains('K7M2QX'));
    expect(
      shared.single,
      contains('io.github.sphaerox.dicrates://open/join/K7M2QX'),
    );

    backend.roomsApi.addMembers(roomId, 2);
    await tester.tap(find.byTooltip('Refresh'));
    await tester.pumpAndSettle();
    expect(
      find.text('3 of 6 members joined (at least 3 needed)'),
      findsOneWidget,
    );

    await tapText(tester, 'Start debate');
    expect(
      find.text('The debate has started. Round 1 is open.'),
      findsOneWidget,
    );
  });

  testWidgets('join with a code', (tester) async {
    backend.roomsApi.addForeignRoom(code: 'PQR678');
    await pumpApp(tester);

    await tapText(tester, 'Join with code');
    await tester.enterText(find.byType(TextFormField), 'pqr');
    await tapText(tester, 'Join');
    expect(
      find.text('Please enter the 6-character code you received.'),
      findsOneWidget,
    );

    await tester.enterText(find.byType(TextFormField), 'ZZZ999');
    await tapText(tester, 'Join');
    expect(find.text('No open room with this code.'), findsOneWidget);

    await tester.enterText(find.byType(TextFormField), 'pqr-678');
    await tapText(tester, 'Join');
    expect(
      find.text('Waiting for the creator to start the debate.'),
      findsOneWidget,
    );
    expect(find.text('Start debate'), findsNothing);
    expect(
      find.text('3 of 6 members joined (at least 3 needed)'),
      findsOneWidget,
    );
  });

  testWidgets('full and started rooms give clear errors', (tester) async {
    backend.roomsApi
      ..addForeignRoom(code: 'FKQR66', members: 6)
      ..addForeignRoom(code: 'GQNE77', status: 'R2_OPEN');
    await pumpApp(tester);
    await tapText(tester, 'Join with code');

    await tester.enterText(find.byType(TextFormField), 'FKQR66');
    await tapText(tester, 'Join');
    expect(find.text('This room is already full (6 members).'), findsOneWidget);

    await tester.enterText(find.byType(TextFormField), 'GQNE77');
    await tapText(tester, 'Join');
    expect(find.text('This debate has already started.'), findsOneWidget);
  });

  testWidgets('an invite deep link opens the join screen with the code', (
    tester,
  ) async {
    await pumpApp(tester);

    routerOf(tester).go(
      routeForDeepLink(
        Uri.parse('io.github.sphaerox.dicrates://open/join/K7M2QX'),
      )!,
    );
    await tester.pumpAndSettle();

    expect(find.text('Join a room'), findsOneWidget);
    expect(find.text('K7M2QX'), findsOneWidget);
  });

  testWidgets('home lists running and finished rooms', (tester) async {
    final running = backend.roomsApi.addForeignRoom(
      code: 'RUN234',
      status: 'R2_OPEN',
      members: 4,
    );
    final done = backend.roomsApi.addForeignRoom(
      code: 'END234',
      status: 'FINISHED',
      members: 3,
    );
    backend.roomsApi.mine.addAll([running, done]);
    await pumpApp(tester);

    expect(find.text('Running'), findsOneWidget);
    expect(find.text('Finished'), findsWidgets);
    expect(find.text('Debate running'), findsOneWidget);
    expect(find.text('4 members'), findsOneWidget);
  });

  testWidgets('members can leave a forming room', (tester) async {
    final id = backend.roomsApi.addForeignRoom(code: 'PQR678');
    await pumpApp(tester);
    await tapText(tester, 'Join with code');
    await tester.enterText(find.byType(TextFormField), 'PQR678');
    await tapText(tester, 'Join');

    await tapText(tester, 'Leave room');

    expect(backend.roomsApi.mine, isNot(contains(id)));
    expect(find.text('My rooms'), findsOneWidget);
  });

  testWidgets('German UI asks for German questions', (tester) async {
    await pumpApp(tester, locale: const Locale('de'));

    await tapText(tester, 'Raum erstellen');

    expect(backend.roomsApi.requestedQuestionLanguages.last, 'de');
    expect(
      find.text('Soll Beispielstadt den Marktplatz autofrei machen?'),
      findsOneWidget,
    );
  });

  group('invite codes', () {
    test('normalize like the backend', () {
      expect(normalizeInviteCode(' k7m-2qx '), 'K7M2QX');
      expect(normalizeInviteCode('K7M2Q0'), isNull); // 0 is not in the alphabet
      expect(normalizeInviteCode('K7M'), isNull);
    });

    test('links round-trip', () {
      final link = inviteLink('K7M2QX');

      expect(link.toString(), 'io.github.sphaerox.dicrates://open/join/K7M2QX');
      expect(routeForDeepLink(link), '/rooms/join?code=K7M2QX');
      expect(routeForDeepLink(Uri.parse('https://example.test/x')), isNull);
    });
  });

  test('demo question is a scale question', () {
    expect(demoQuestion().format, QuestionFormat.scale);
  });
}
