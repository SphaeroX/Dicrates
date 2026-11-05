import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import '../../features/home/data/backend_health.dart';
import '../../features/onboarding/data/me.dart';

/// A failed backend call. [statusCode] is `null` for network errors.
class ApiException implements Exception {
  const ApiException(this.statusCode);

  final int? statusCode;

  bool get isNetworkError => statusCode == null;

  @override
  String toString() => 'ApiException($statusCode)';
}

typedef AccessTokenGetter = Future<String?> Function();

/// HTTP client for the Dicrates backend. All game data goes through here.
class ApiClient {
  ApiClient({
    required this._httpClient,
    required Uri baseUrl,
    AccessTokenGetter? accessToken,
    this.timeout = const Duration(seconds: 10),
  }) : _baseUrl = _withTrailingSlash(baseUrl),
       _accessToken = accessToken ?? _noToken;

  final http.Client _httpClient;
  final Uri _baseUrl;
  final AccessTokenGetter _accessToken;
  final Duration timeout;

  static Future<String?> _noToken() async => null;

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

  Future<Me> getMe() async => Me.fromJson(await _send('GET', 'me'));

  /// Changes only the given fields of the caller's profile.
  Future<Me> updateMe({String? pseudonym, String? language}) async {
    final body = {'pseudonym': ?pseudonym, 'language': ?language};
    return Me.fromJson(await _send('PATCH', 'me', body: body));
  }

  /// Stores the explicit consent together with the 18+ confirmation.
  Future<void> giveConsent({required String consentVersion}) async {
    await _send(
      'POST',
      'me/consent',
      body: {'consent_version': consentVersion, 'age_confirmed': true},
    );
  }

  Future<Map<String, Object?>> _send(
    String method,
    String path, {
    Map<String, Object?>? body,
  }) async {
    final token = await _accessToken();
    if (token == null) throw const ApiException(401);
    final request = http.Request(method, _endpoint(path))
      ..headers['Authorization'] = 'Bearer $token'
      ..headers['Accept'] = 'application/json';
    if (body != null) {
      request
        ..headers['Content-Type'] = 'application/json'
        ..body = jsonEncode(body);
    }
    final http.Response response;
    try {
      response = await http.Response.fromStream(
        await _httpClient.send(request).timeout(timeout),
      );
    } on Exception {
      throw const ApiException(null);
    }
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw ApiException(response.statusCode);
    }
    final decoded = jsonDecode(utf8.decode(response.bodyBytes));
    return decoded is Map<String, Object?> ? decoded : const {};
  }

  void close() => _httpClient.close();
}
