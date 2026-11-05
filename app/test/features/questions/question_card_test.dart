import 'package:dicrates/features/questions/data/question.dart';
import 'package:dicrates/features/questions/providers/link_opener_provider.dart';
import 'package:dicrates/features/questions/widgets/question_card.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import '../../helpers/demo_questions.dart';
import '../../helpers/screen_app.dart';

void main() {
  late List<Uri> opened;
  late bool openSucceeds;

  Future<void> pumpCard(
    WidgetTester tester,
    Question question, {
    Locale locale = const Locale('en'),
  }) async {
    await tester.pumpWidget(
      buildScreenApp(
        Scaffold(
          body: SingleChildScrollView(child: QuestionCard(question: question)),
        ),
        locale: locale,
        overrides: [
          linkOpenerProvider.overrideWithValue((uri) async {
            opened.add(uri);
            return openSucceeds;
          }),
        ],
      ),
    );
    await tester.pumpAndSettle();
  }

  setUp(() {
    opened = [];
    openSucceeds = true;
  });

  test('parses the API payload', () {
    final question = demoQuestion(format: QuestionFormat.tradeoff);

    expect(question.format, QuestionFormat.tradeoff);
    expect(question.optionA, 'A new swimming pool');
    expect(question.facts[1].sourceIds, [1, 2]);
    expect(question.sources.first.publishedOn, DateTime(2026, 10, 1));
    expect(question.sources.last.publishedOn, isNull);
  });

  testWidgets('scale question shows text, hint, facts and sources', (
    tester,
  ) async {
    await pumpCard(tester, demoQuestion());

    expect(
      find.text(
        'Should the town of Exampleville introduce a car-free market square?',
      ),
      findsOneWidget,
    );
    expect(find.text('Society'), findsOneWidget);
    expect(
      find.text(
        'Rate it from clearly against to clearly in favour, and explain why.',
      ),
      findsOneWidget,
    );
    expect(find.text('Facts'), findsOneWidget);
    expect(find.text('Sources: 1, 2'), findsOneWidget);
    expect(find.text('Option A'), findsNothing);
  });

  testWidgets('proposal question shows its hint', (tester) async {
    await pumpCard(tester, demoQuestion(format: QuestionFormat.proposal));

    expect(
      find.text('Make a concrete proposal and explain it.'),
      findsOneWidget,
    );
  });

  testWidgets('tradeoff question shows both options', (tester) async {
    await pumpCard(tester, demoQuestion(format: QuestionFormat.tradeoff));

    expect(find.text('Option A'), findsOneWidget);
    expect(find.text('A new swimming pool'), findsOneWidget);
    expect(find.text('Option B'), findsOneWidget);
    expect(find.text('Renovating the schools'), findsOneWidget);
  });

  testWidgets('source links have screen reader labels and open the URL', (
    tester,
  ) async {
    final semantics = tester.ensureSemantics();
    await pumpCard(tester, demoQuestion());

    final label = find.bySemanticsLabel(
      'Source 1: Traffic report 2026, Exampleville Gazette. '
      'Opens in your browser.',
    );
    expect(label, findsOneWidget);

    await tester.ensureVisible(label);
    await tester.tap(label);
    await tester.pumpAndSettle();

    expect(opened, [Uri.parse('https://example.test/traffic-report')]);
    semantics.dispose();
  });

  testWidgets('shows an error when a link cannot be opened', (tester) async {
    openSucceeds = false;
    await pumpCard(tester, demoQuestion());

    await tester.ensureVisible(find.text('Traffic report 2026'));
    await tester.tap(find.text('Traffic report 2026'));
    await tester.pumpAndSettle();

    expect(find.text('The link could not be opened.'), findsOneWidget);
  });

  testWidgets('unknown topic areas fall back to Other', (tester) async {
    await pumpCard(tester, demoQuestion(topicArea: 'astrology'));

    expect(find.text('Other'), findsOneWidget);
  });

  testWidgets('German labels', (tester) async {
    await pumpCard(
      tester,
      demoQuestion(format: QuestionFormat.tradeoff),
      locale: const Locale('de'),
    );

    expect(find.text('Fakten'), findsOneWidget);
    expect(find.text('Quellen'), findsOneWidget);
    expect(find.text('Gesellschaft'), findsOneWidget);
  });
}
