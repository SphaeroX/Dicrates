import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/api_client_provider.dart';
import '../../../core/router/app_router.dart';
import '../../../core/widgets/form_page.dart';
import '../../../l10n/app_localizations.dart';
import '../../questions/data/question.dart';
import '../../questions/widgets/question_card.dart';
import '../../questions/widgets/topic_area_name.dart';
import '../data/room.dart';
import '../providers/room_providers.dart';

const _topicAreas = [
  'politics',
  'economy',
  'society',
  'environment',
  'technology',
  'sports',
  'culture',
  'education',
  'health',
];

/// Room language = app language (the backend serves questions per language).
String roomLanguageOf(BuildContext context) =>
    Localizations.localeOf(context).languageCode == 'de' ? 'de' : 'en';

class CreateRoomScreen extends ConsumerStatefulWidget {
  const CreateRoomScreen({super.key});

  @override
  ConsumerState<CreateRoomScreen> createState() => _CreateRoomScreenState();
}

class _CreateRoomScreenState extends ConsumerState<CreateRoomScreen> {
  String? _topicArea;
  Question? _selected;
  int _hours = defaultRoundDurationHours;
  bool _busy = false;
  bool _failed = false;

  Future<void> _create() async {
    final question = _selected;
    if (question == null) return;
    setState(() {
      _busy = true;
      _failed = false;
    });
    try {
      final room = await ref
          .read(apiClientProvider)
          .createRoom(questionId: question.id, roundDurationHours: _hours);
      ref.invalidate(roomsProvider);
      if (mounted) context.pushReplacement(AppRoutes.room(room.id));
    } on ApiException {
      if (mounted) setState(() => _failed = true);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final textTheme = Theme.of(context).textTheme;
    final questions = ref.watch(
      questionsProvider((
        language: roomLanguageOf(context),
        topicArea: _topicArea,
      )),
    );
    final selected = _selected;

    return FormPage(
      title: l10n.createRoomTitle,
      children: [
        Semantics(
          header: true,
          child: Text(l10n.chooseQuestionHeading, style: textTheme.titleMedium),
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            ChoiceChip(
              label: Text(l10n.allTopicAreas),
              selected: _topicArea == null,
              onSelected: (_) => setState(() => _topicArea = null),
            ),
            for (final area in _topicAreas)
              ChoiceChip(
                label: Text(topicAreaName(l10n, area)),
                selected: _topicArea == area,
                onSelected: (_) => setState(() => _topicArea = area),
              ),
          ],
        ),
        const SizedBox(height: 12),
        questions.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (_, _) => ErrorMessage(l10n.questionsLoadFailed),
          data: (list) => list.isEmpty
              ? Text(l10n.noQuestionsAvailable, textAlign: TextAlign.center)
              : RadioGroup<String>(
                  groupValue: selected?.id,
                  onChanged: (id) => setState(
                    () => _selected = list.firstWhere((q) => q.id == id),
                  ),
                  child: Column(
                    children: [
                      for (final question in list)
                        RadioListTile<String>(
                          value: question.id,
                          title: Text(question.text),
                          subtitle: Text(
                            topicAreaName(l10n, question.topicArea),
                          ),
                        ),
                    ],
                  ),
                ),
        ),
        if (selected != null) QuestionCard(question: selected),
        const SizedBox(height: 16),
        Semantics(
          header: true,
          child: Text(l10n.roundDurationHeading, style: textTheme.titleMedium),
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            for (final hours in roundDurationsHours)
              ChoiceChip(
                label: Text(l10n.roundDurationHours(hours)),
                selected: _hours == hours,
                onSelected: (_) => setState(() => _hours = hours),
              ),
          ],
        ),
        const SizedBox(height: 8),
        Text(l10n.roundDurationHint, style: textTheme.bodySmall),
        const SizedBox(height: 24),
        FilledButton(
          onPressed: _busy || selected == null ? null : _create,
          child: Text(l10n.createRoomSubmit),
        ),
        if (_failed) ...[
          const SizedBox(height: 16),
          ErrorMessage(l10n.genericError),
        ],
      ],
    );
  }
}
