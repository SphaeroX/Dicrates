import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_client_provider.dart';
import '../data/backend_health.dart';

/// Health of the backend; `ref.invalidate(backendHealthProvider)` re-checks.
final backendHealthProvider = FutureProvider.autoDispose<BackendHealth>(
  (ref) => ref.watch(apiClientProvider).fetchHealth(),
);
