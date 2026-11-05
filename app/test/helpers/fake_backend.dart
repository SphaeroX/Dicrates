import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

/// Minimal in-memory version of the backend's `/health` and `/me` API.
class FakeBackend {
  FakeBackend({
    this.pseudonym,
    this.language = 'en',
    this.consentVersion,
    this.reachable = true,
  });

  static const currentConsentVersion = '1';
  static const userId = '00000000-0000-4000-8000-000000000001';

  String? pseudonym;
  String language;
  String? consentVersion;
  bool reachable;
  final List<http.Request> requests = [];
  final List<Map<String, Object?>> consentBodies = [];

  MockClient get client => MockClient(handle);

  bool get _consentValid => consentVersion == currentConsentVersion;

  Map<String, Object?> get _me => {
    'id': userId,
    'pseudonym': pseudonym,
    'language': language,
    'consent': _consentValid
        ? {
            'consent_version': consentVersion,
            'age_confirmed': true,
            'granted_at': '2026-11-05T12:00:00Z',
          }
        : null,
    'onboarding_complete': _consentValid && pseudonym != null,
    'current_consent_version': currentConsentVersion,
  };

  Future<http.Response> handle(http.Request request) async {
    requests.add(request);
    if (!reachable) {
      throw http.ClientException('offline');
    }
    if (request.url.path == '/health') {
      return _json({'status': 'ok', 'version': '0.1.0'});
    }
    if (request.headers['Authorization'] != 'Bearer fake-access-token') {
      return _json({'detail': 'Not authenticated'}, status: 401);
    }
    switch ((request.method, request.url.path)) {
      case ('GET', '/me'):
        return _json(_me);
      case ('PATCH', '/me'):
        final body = jsonDecode(request.body) as Map<String, Object?>;
        final newPseudonym = body['pseudonym'];
        if (newPseudonym is String) {
          if (newPseudonym.trim().length < 3) {
            return _json({'detail': 'invalid'}, status: 422);
          }
          pseudonym = newPseudonym.trim();
        }
        final newLanguage = body['language'];
        if (newLanguage is String) language = newLanguage;
        return _json(_me);
      case ('POST', '/me/consent'):
        final body = jsonDecode(request.body) as Map<String, Object?>;
        consentBodies.add(body);
        if (body['age_confirmed'] != true ||
            body['consent_version'] != currentConsentVersion) {
          return _json({'detail': 'invalid'}, status: 422);
        }
        consentVersion = body['consent_version']! as String;
        return _json({
          'consent_version': consentVersion,
          'age_confirmed': true,
          'granted_at': '2026-11-05T12:00:00Z',
        }, status: 201);
    }
    return _json({'detail': 'Not Found'}, status: 404);
  }

  static http.Response _json(Object body, {int status = 200}) => http.Response(
    jsonEncode(body),
    status,
    headers: {'content-type': 'application/json'},
  );
}
