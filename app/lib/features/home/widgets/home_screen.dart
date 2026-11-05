import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../l10n/app_localizations.dart';
import '../data/backend_health.dart';
import '../providers/backend_health_provider.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context);
    final textTheme = Theme.of(context).textTheme;
    final health = ref.watch(backendHealthProvider);

    return Scaffold(
      appBar: AppBar(title: Text(l10n.appTitle)),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 560),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Semantics(
                    header: true,
                    child: Text(
                      l10n.homeHeadline,
                      style: textTheme.headlineMedium,
                      textAlign: TextAlign.center,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    l10n.homeTagline,
                    style: textTheme.bodyLarge,
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 32),
                  health.when(
                    data: (value) => _BackendStatus(
                      health: value,
                      onRetry: () => ref.invalidate(backendHealthProvider),
                    ),
                    loading: () => const _CheckingStatus(),
                    error: (_, _) => _BackendStatus(
                      health: const BackendHealth.unreachable(),
                      onRetry: () => ref.invalidate(backendHealthProvider),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _CheckingStatus extends StatelessWidget {
  const _CheckingStatus();

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    return Column(
      children: [
        const CircularProgressIndicator(),
        const SizedBox(height: 12),
        Text(l10n.backendStatusChecking, textAlign: TextAlign.center),
      ],
    );
  }
}

class _BackendStatus extends StatelessWidget {
  const _BackendStatus({required this.health, required this.onRetry});

  final BackendHealth health;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final colorScheme = Theme.of(context).colorScheme;
    final connected = health.isConnected;

    return Card(
      color: connected
          ? colorScheme.secondaryContainer
          : colorScheme.errorContainer,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  connected ? Icons.cloud_done_outlined : Icons.cloud_off,
                  color: connected
                      ? colorScheme.onSecondaryContainer
                      : colorScheme.onErrorContainer,
                ),
                const SizedBox(width: 12),
                Flexible(
                  child: Text(
                    connected
                        ? l10n.backendStatusConnected
                        : l10n.backendStatusUnreachable,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      color: connected
                          ? colorScheme.onSecondaryContainer
                          : colorScheme.onErrorContainer,
                    ),
                  ),
                ),
              ],
            ),
            if (!connected) ...[
              const SizedBox(height: 12),
              FilledButton.tonal(
                onPressed: onRetry,
                child: Text(l10n.retryButton),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
