import 'package:alchemist/alchemist.dart';
import 'package:dicrates/features/questions/data/question.dart';
import 'package:dicrates/features/questions/widgets/question_card.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/demo_questions.dart';
import '../helpers/screen_app.dart';
import 'screen_sizes.dart';

void main() {
  group('question card', () {
    for (final format in QuestionFormat.values) {
      for (final (themeMode, screenSize) in goldenVariants) {
        final name =
            'question_card_${format.name}_${variantName(themeMode, screenSize)}';
        goldenTest(
          'renders $name',
          fileName: name,
          constraints: BoxConstraints.tight(screenSize.size),
          builder: () => buildScreenApp(
            Scaffold(
              body: SafeArea(
                child: SingleChildScrollView(
                  child: QuestionCard(question: demoQuestion(format: format)),
                ),
              ),
            ),
            themeMode: themeMode,
          ),
        );
      }
    }
  });
}
