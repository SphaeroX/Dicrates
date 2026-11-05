import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;

import '../../features/auth/providers/auth_providers.dart';
import '../config/app_config.dart';
import 'api_client.dart';

final apiClientProvider = Provider<ApiClient>((ref) {
  final config = ref.watch(appConfigProvider);
  final client = ApiClient(
    httpClient: http.Client(),
    baseUrl: Uri.parse(config.apiBaseUrl),
    accessToken: () async =>
        ref.read(authRepositoryProvider).currentSession?.accessToken,
  );
  ref.onDispose(client.close);
  return client;
});
