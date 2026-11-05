import 'package:flutter/foundation.dart';

enum QuestionFormat { scale, proposal, tradeoff }

@immutable
class QuestionSource {
  const QuestionSource({
    required this.id,
    required this.url,
    required this.title,
    required this.outlet,
    this.publishedOn,
  });

  factory QuestionSource.fromJson(Map<String, Object?> json) => QuestionSource(
    id: json['id']! as int,
    url: Uri.parse(json['url']! as String),
    title: json['title']! as String,
    outlet: json['outlet']! as String,
    publishedOn: switch (json['published_on']) {
      final String date => DateTime.parse(date),
      _ => null,
    },
  );

  final int id;
  final Uri url;
  final String title;
  final String outlet;
  final DateTime? publishedOn;
}

@immutable
class QuestionFact {
  const QuestionFact({required this.text, required this.sourceIds});

  factory QuestionFact.fromJson(Map<String, Object?> json) => QuestionFact(
    text: json['text']! as String,
    sourceIds: [
      for (final id in json['source_ids']! as List<Object?>) id! as int,
    ],
  );

  final String text;
  final List<int> sourceIds;
}

/// An approved debate question from `GET /questions`.
@immutable
class Question {
  const Question({
    required this.id,
    required this.language,
    required this.format,
    required this.text,
    required this.facts,
    required this.sources,
    required this.topicArea,
    this.optionA,
    this.optionB,
  });

  factory Question.fromJson(Map<String, Object?> json) => Question(
    id: json['id']! as String,
    language: json['language']! as String,
    format: QuestionFormat.values.byName(json['format']! as String),
    text: json['text']! as String,
    optionA: json['option_a'] as String?,
    optionB: json['option_b'] as String?,
    facts: [
      for (final fact in json['facts']! as List<Object?>)
        QuestionFact.fromJson(fact! as Map<String, Object?>),
    ],
    sources: [
      for (final source in json['sources']! as List<Object?>)
        QuestionSource.fromJson(source! as Map<String, Object?>),
    ],
    topicArea: json['topic_area']! as String,
  );

  final String id;
  final String language;
  final QuestionFormat format;
  final String text;
  final String? optionA;
  final String? optionB;
  final List<QuestionFact> facts;
  final List<QuestionSource> sources;
  final String topicArea;
}
