import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import '../../features/home/data/backend_health.dart';

/// HTTP client for the Dicrates backend. All game data goes through here.
class ApiClient {
  ApiClient({
    required this._httpClient,
    required Uri baseUrl,
    this.timeout = const Duration(seconds: 5),
  }) : _baseUrl = _withTrailingSlash(baseUrl);

  final http.Client _httpClient;
  final Uri _baseUrl;
  final Duration timeout;

  static Uri _withTrailingSlash(Uri uri) =>
      uri.path.endsWith('/') ? uri : uri.replace(path: '${uri.path}/');

  Uri _endpoint(String path) => _baseUrl.resolve(path);

  /// Checks whether the backend is reachable. Never throws.
  Future<BackendHealth> fetchHealth() async {
    try {
      final response = await _httpClient
          .get(_endpoint('health'))
          .timeout(timeout);
      if (response.statusCode != 200) {
        return const BackendHealth.unreachable();
      }
      final body = jsonDecode(response.body);
      if (body is Map<String, Object?> &&
          body['status'] == 'ok' &&
          body['version'] is String) {
        return BackendHealth.connected(version: body['version']! as String);
      }
      return const BackendHealth.unreachable();
    } on Exception {
      return const BackendHealth.unreachable();
    }
  }

  void close() => _httpClient.close();
}
