import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../features/auth/widgets/code_screen.dart';
import '../../features/auth/widgets/login_screen.dart';
import '../../features/home/widgets/home_screen.dart';
import '../../features/onboarding/widgets/age_screen.dart';
import '../../features/onboarding/widgets/consent_screen.dart';
import '../../features/onboarding/widgets/pseudonym_screen.dart';
import '../../features/onboarding/widgets/under_age_screen.dart';
import '../../features/splash/widgets/splash_screen.dart';
import 'app_gate.dart';

abstract final class AppRoutes {
  static const home = '/';
  static const splash = '/splash';
  static const login = '/login';
  static const loginCode = '/login/code';
  static const age = '/onboarding/age';
  static const underAge = '/onboarding/under-age';
  static const consent = '/onboarding/consent';
  static const pseudonym = '/onboarding/pseudonym';
}

const _gateRoutes = {
  AppRoutes.splash,
  AppRoutes.login,
  AppRoutes.loginCode,
  AppRoutes.age,
  AppRoutes.underAge,
  AppRoutes.consent,
  AppRoutes.pseudonym,
};

/// Route the user must be on for [gate], or `null` to stay on [location].
String? redirectFor(AppGate gate, String location) {
  final target = switch (gate) {
    AppGate.loading || AppGate.unreachable => AppRoutes.splash,
    AppGate.signedOut =>
      location == AppRoutes.login || location == AppRoutes.loginCode
          ? location
          : AppRoutes.login,
    AppGate.needsAgeConfirmation => AppRoutes.age,
    AppGate.underAge => AppRoutes.underAge,
    AppGate.needsConsent => AppRoutes.consent,
    AppGate.needsPseudonym => AppRoutes.pseudonym,
    AppGate.ready => _gateRoutes.contains(location) ? AppRoutes.home : location,
  };
  return target == location ? null : target;
}

final routerProvider = Provider<GoRouter>((ref) {
  final gate = ValueNotifier<AppGate>(ref.read(appGateProvider));
  ref.listen(appGateProvider, (_, next) => gate.value = next);

  final router = GoRouter(
    initialLocation: AppRoutes.splash,
    refreshListenable: gate,
    redirect: (context, state) =>
        redirectFor(gate.value, state.matchedLocation),
    routes: [
      GoRoute(path: AppRoutes.home, builder: (_, _) => const HomeScreen()),
      GoRoute(path: AppRoutes.splash, builder: (_, _) => const SplashScreen()),
      GoRoute(path: AppRoutes.login, builder: (_, _) => const LoginScreen()),
      GoRoute(path: AppRoutes.loginCode, builder: (_, _) => const CodeScreen()),
      GoRoute(path: AppRoutes.age, builder: (_, _) => const AgeScreen()),
      GoRoute(
        path: AppRoutes.underAge,
        builder: (_, _) => const UnderAgeScreen(),
      ),
      GoRoute(
        path: AppRoutes.consent,
        builder: (_, _) => const ConsentScreen(),
      ),
      GoRoute(
        path: AppRoutes.pseudonym,
        builder: (_, _) => const PseudonymScreen(),
      ),
    ],
  );
  ref.onDispose(() {
    router.dispose();
    gate.dispose();
  });
  return router;
});
