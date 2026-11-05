import 'dart:async';
import 'dart:io';

import 'package:alchemist/alchemist.dart';

/// Golden strategy (see docs/testing.md → App screenshots):
///
/// * Platform goldens with real text are rendered only on Windows (the main
///   development machine) and written to `app/screenshots/` for the README
///   gallery and mockups. Other platforms render fonts slightly differently,
///   so they skip these.
/// * CI goldens (text drawn as blocks, no shadows) are platform independent,
///   stored next to the tests in `test/screenshots/goldens/ci/` and verified
///   everywhere, including the Linux CI.
Future<void> testExecutable(FutureOr<void> Function() testMain) async {
  final runningInCi = Platform.environment.containsKey('CI');

  return AlchemistConfig.runWithConfig(
    config: AlchemistConfig(
      platformGoldensConfig: PlatformGoldensConfig(
        enabled: !runningInCi,
        platforms: {HostPlatform.windows},
        filePathResolver: (fileName, environmentName) =>
            '../../screenshots/$fileName.png',
      ),
      ciGoldensConfig: CiGoldensConfig(
        filePathResolver: (fileName, environmentName) =>
            'goldens/ci/$fileName.png',
      ),
    ),
    run: testMain,
  );
}
