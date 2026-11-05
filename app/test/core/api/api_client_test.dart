import 'dart:convert';
import 'dart:io';

import 'package:dicrates/core/api/api_client.dart';
import 'package:dicrates/features/home/data/backend_health.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

void main() {
  ApiClient clientReturning(
    MockClientHandler handler, {
    String base = 'http://api.test',
  }) => ApiClient(httpClient: MockClient(handler), baseUrl: Uri.parse(base));

  test('parses a healthy response', () async {
    late Uri requested;
    final client = clientReturning((request) async {
      requested = request.url;
      return http.Response(
        jsonEncode({'status': 'ok', 'version': '0.1.0'}),
        200,
      );
    });

    final health = await client.fetchHealth();

    expect(requested.toString(), 'http://api.test/health');
    expect(health, const BackendHealth.connected(version: '0.1.0'));
  });

  test('keeps a base path when building the health URL', () async {
    late Uri requested;
    final client = clientReturning((request) async {
      requested = request.url;
      return http.Response(jsonEncode({'status': 'ok', 'version': '1'}), 200);
    }, base: 'https://example.test/api');

    await client.fetchHealth();

    expect(requested.toString(), 'https://example.test/api/health');
  });

  test('treats a non-200 status as unreachable', () async {
    final client = clientReturning((_) async => http.Response('oops', 503));

    expect(await client.fetchHealth(), const BackendHealth.unreachable());
  });

  test('treats malformed JSON as unreachable', () async {
    final client = clientReturning((_) async => http.Response('not json', 200));

    expect(await client.fetchHealth(), const BackendHealth.unreachable());
  });

  test('treats a network error as unreachable', () async {
    final client = clientReturning(
      (_) async => throw const SocketException('offline'),
    );

    expect(await client.fetchHealth(), const BackendHealth.unreachable());
  });
}
