import 'dart:convert';

import 'package:dicrates/core/api/api_client.dart';
import 'package:flutter_test/flutter_test.dart';

import '../../helpers/fake_backend.dart';

void main() {
  late FakeBackend backend;
  late ApiClient client;
  String? token;

  setUp(() {
    backend = FakeBackend();
    token = 'fake-access-token';
    client = ApiClient(
      httpClient: backend.client,
      baseUrl: Uri.parse('http://api.test'),
      accessToken: () async => token,
    );
  });

  test('getMe sends the bearer token and parses the profile', () async {
    final me = await client.getMe();

    expect(
      backend.requests.single.headers['Authorization'],
      'Bearer fake-access-token',
    );
    expect(me.id, FakeBackend.userId);
    expect(me.pseudonym, isNull);
    expect(me.hasValidConsent, isFalse);
    expect(me.onboardingComplete, isFalse);
  });

  test('getMe without a session throws an unauthorized ApiException', () async {
    token = null;

    expect(
      client.getMe(),
      throwsA(isA<ApiException>().having((e) => e.statusCode, 'status', 401)),
    );
  });

  test('giveConsent posts version and age confirmation', () async {
    await client.giveConsent(consentVersion: '1');

    expect(backend.consentBodies.single, {
      'consent_version': '1',
      'age_confirmed': true,
    });
    expect((await client.getMe()).hasValidConsent, isTrue);
  });

  test('updateMe sends only the given fields', () async {
    final me = await client.updateMe(pseudonym: 'Owl');

    expect(jsonDecode(backend.requests.last.body), {'pseudonym': 'Owl'});
    expect(me.pseudonym, 'Owl');
  });

  test('a rejected update throws with the status code', () async {
    expect(
      client.updateMe(pseudonym: 'x'),
      throwsA(isA<ApiException>().having((e) => e.statusCode, 'status', 422)),
    );
  });

  test('network errors become ApiException without status', () async {
    backend.reachable = false;

    expect(
      client.getMe(),
      throwsA(isA<ApiException>().having((e) => e.statusCode, 'status', null)),
    );
  });
}
