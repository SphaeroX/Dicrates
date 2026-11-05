import 'package:dicrates/features/questions/data/question.dart';

/// Invented demo questions for widget tests and screenshots.
Question demoQuestion({
  QuestionFormat format = QuestionFormat.scale,
  String topicArea = 'society',
}) => Question.fromJson(demoQuestionJson(format: format, topicArea: topicArea));

/// The same demo question as the API returns it.
Map<String, Object?> demoQuestionJson({
  QuestionFormat format = QuestionFormat.scale,
  String topicArea = 'society',
  String id = '11111111-1111-4111-8111-111111111111',
  String language = 'en',
  String? text,
}) {
  return {
    'id': id,
    'language': language,
    'format': format.name,
    'text':
        text ??
        switch (format) {
          QuestionFormat.scale => 'Should the town of Exampleville introduce a car-free market square?',
          QuestionFormat.proposal =>
            'How should Exampleville pay for its new tram line?',
          QuestionFormat.tradeoff =>
            "What should have priority in Exampleville's budget?",
        },
    'option_a': format == QuestionFormat.tradeoff
        ? 'A new swimming pool'
        : null,
    'option_b': format == QuestionFormat.tradeoff
        ? 'Renovating the schools'
        : null,
    'facts': [
      {
        'text': 'The square is crossed by about 4,000 cars per day.',
        'source_ids': [1],
      },
      {
        'text': 'Two neighbouring towns tried the same in 2025.',
        'source_ids': [1, 2],
      },
    ],
    'sources': [
      {
        'id': 1,
        'url': 'https://example.test/traffic-report',
        'title': 'Traffic report 2026',
        'outlet': 'Exampleville Gazette',
        'published_on': '2026-10-01',
      },
      {
        'id': 2,
        'url': 'https://example.test/neighbours',
        'title': 'What the neighbours did',
        'outlet': 'Regional Radio',
        'published_on': null,
      },
    ],
    'topic_area': topicArea,
  };
}
