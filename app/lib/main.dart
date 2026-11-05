import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'app.dart';
import 'core/config/app_config.dart';
import 'features/auth/data/supabase_auth_repository.dart';
import 'features/auth/providers/auth_providers.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  const config = AppConfig.fromEnvironment();

  final overrides = [
    if (config.hasSupabase)
      authRepositoryProvider.overrideWithValue(
        SupabaseAuthRepository(
          (await Supabase.initialize(
            url: config.supabaseUrl,
            publishableKey: config.supabaseAnonKey,
          )).client.auth,
        ),
      ),
  ];

  runApp(ProviderScope(overrides: overrides, child: const DicratesApp()));
}
