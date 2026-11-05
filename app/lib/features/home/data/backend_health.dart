import 'package:flutter/foundation.dart';

enum BackendHealthStatus { connected, unreachable }

/// Result of the backend health check (`GET /health`).
@immutable
class BackendHealth {
  const BackendHealth.connected({required String this.version})
    : status = BackendHealthStatus.connected;

  const BackendHealth.unreachable()
    : status = BackendHealthStatus.unreachable,
      version = null;

  final BackendHealthStatus status;
  final String? version;

  bool get isConnected => status == BackendHealthStatus.connected;

  @override
  bool operator ==(Object other) =>
      other is BackendHealth &&
      other.status == status &&
      other.version == version;

  @override
  int get hashCode => Object.hash(status, version);

  @override
  String toString() => 'BackendHealth($status, version: $version)';
}
