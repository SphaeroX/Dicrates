import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../../l10n/app_localizations.dart';
import '../data/question.dart';
import '../providers/link_opener_provider.dart';
import 'topic_area_name.dart';

/// A debate question with its fact box and sources. Reused by room creation
/// and every round screen.
class QuestionCard extends StatelessWidget {
  const QuestionCard({super.key, required this.question});

  final Question question;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final theme = Theme.of(context);

    return Card(
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Align(
              alignment: AlignmentDirectional.centerStart,
              child: Chip(label: Text(topicAreaName(l10n, question.topicArea))),
            ),
            const SizedBox(height: 12),
            Semantics(
              header: true,
              child: Text(question.text, style: theme.textTheme.headlineSmall),
            ),
            const SizedBox(height: 8),
            Text(switch (question.format) {
              QuestionFormat.scale => l10n.questionFormatScale,
              QuestionFormat.proposal => l10n.questionFormatProposal,
              QuestionFormat.tradeoff => l10n.questionFormatTradeoff,
            }, style: theme.textTheme.bodyMedium),
            if (question.format == QuestionFormat.tradeoff) ...[
              const SizedBox(height: 16),
              _Option(label: l10n.optionALabel, text: question.optionA ?? ''),
              const SizedBox(height: 8),
              _Option(label: l10n.optionBLabel, text: question.optionB ?? ''),
            ],
            const SizedBox(height: 24),
            _FactBox(facts: question.facts),
            const SizedBox(height: 24),
            _SourceList(sources: question.sources),
          ],
        ),
      ),
    );
  }
}

class _Option extends StatelessWidget {
  const _Option({required this.label, required this.text});

  final String label;
  final String text;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return DecoratedBox(
      decoration: BoxDecoration(
        color: theme.colorScheme.secondaryContainer,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: MergeSemantics(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: theme.textTheme.labelLarge?.copyWith(
                  color: theme.colorScheme.onSecondaryContainer,
                ),
              ),
              Text(
                text,
                style: theme.textTheme.bodyLarge?.copyWith(
                  color: theme.colorScheme.onSecondaryContainer,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _FactBox extends StatelessWidget {
  const _FactBox({required this.facts});

  final List<QuestionFact> facts;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final theme = Theme.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Semantics(
          header: true,
          child: Text(l10n.factBoxTitle, style: theme.textTheme.titleMedium),
        ),
        const SizedBox(height: 8),
        for (final fact in facts)
          Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: MergeSemantics(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(fact.text, style: theme.textTheme.bodyLarge),
                  Text(
                    l10n.factSourceRefs(fact.sourceIds.join(', ')),
                    style: theme.textTheme.bodySmall,
                  ),
                ],
              ),
            ),
          ),
      ],
    );
  }
}

class _SourceList extends ConsumerWidget {
  const _SourceList({required this.sources});

  final List<QuestionSource> sources;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context);
    final theme = Theme.of(context);
    final locale = Localizations.localeOf(context).toLanguageTag();

    Future<void> open(Uri url) async {
      final messenger = ScaffoldMessenger.maybeOf(context);
      final opened = await ref.read(linkOpenerProvider)(url);
      if (!opened) {
        messenger?.showSnackBar(SnackBar(content: Text(l10n.sourceOpenFailed)));
      }
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Semantics(
          header: true,
          child: Text(l10n.sourcesTitle, style: theme.textTheme.titleMedium),
        ),
        for (final source in sources)
          Semantics(
            link: true,
            button: false,
            excludeSemantics: true,
            label: l10n.sourceLinkLabel(source.id, source.title, source.outlet),
            onTap: () => open(source.url),
            child: InkWell(
              onTap: () => open(source.url),
              child: Padding(
                padding: const EdgeInsets.symmetric(vertical: 10),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SizedBox(
                      width: 28,
                      child: Text(
                        '${source.id}',
                        style: theme.textTheme.bodyMedium,
                      ),
                    ),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            source.title,
                            style: theme.textTheme.bodyLarge?.copyWith(
                              color: theme.colorScheme.primary,
                              decoration: TextDecoration.underline,
                            ),
                          ),
                          Text(
                            [
                              source.outlet,
                              if (source.publishedOn case final date?)
                                DateFormat.yMMMd(locale).format(date),
                            ].join(' · '),
                            style: theme.textTheme.bodySmall,
                          ),
                        ],
                      ),
                    ),
                    Icon(
                      Icons.open_in_new,
                      size: 18,
                      color: theme.colorScheme.primary,
                    ),
                  ],
                ),
              ),
            ),
          ),
      ],
    );
  }
}
