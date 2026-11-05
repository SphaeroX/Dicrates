import '../../../l10n/app_localizations.dart';

/// Localized name of a topic area slug from the backend.
String topicAreaName(AppLocalizations l10n, String slug) => switch (slug) {
  'politics' => l10n.topicArea_politics,
  'economy' => l10n.topicArea_economy,
  'society' => l10n.topicArea_society,
  'environment' => l10n.topicArea_environment,
  'technology' => l10n.topicArea_technology,
  'sports' => l10n.topicArea_sports,
  'culture' => l10n.topicArea_culture,
  'education' => l10n.topicArea_education,
  'health' => l10n.topicArea_health,
  _ => l10n.topicAreaOther,
};
