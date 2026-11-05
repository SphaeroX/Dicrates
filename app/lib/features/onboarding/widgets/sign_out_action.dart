import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../l10n/app_localizations.dart';
import '../../auth/providers/auth_providers.dart';

/// App bar action that signs the user out.
class SignOutAction extends ConsumerWidget {
  const SignOutAction({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return IconButton(
      tooltip: AppLocalizations.of(context).signOutButton,
      icon: const Icon(Icons.logout),
      onPressed: () => ref.read(authRepositoryProvider).signOut(),
    );
  }
}

/// Full-width sign-out button for dead ends (under 18, no consent).
class SignOutButton extends ConsumerWidget {
  const SignOutButton({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return OutlinedButton(
      onPressed: () => ref.read(authRepositoryProvider).signOut(),
      child: Text(AppLocalizations.of(context).signOutButton),
    );
  }
}
