import '../../../l10n/app_localizations.dart';
import '../data/auth_repository.dart';

String authFailureText(AppLocalizations l10n, AuthFailure failure) =>
    switch (failure.kind) {
      AuthFailureKind.invalidCode => l10n.authErrorInvalidCode,
      AuthFailureKind.network => l10n.authErrorNetwork,
      AuthFailureKind.notConfigured => l10n.authErrorNotConfigured,
      AuthFailureKind.unknown => l10n.authErrorUnknown,
    };
