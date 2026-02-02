import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'core/theme/app_theme.dart';
import 'core/services/api_service.dart';
import 'core/services/theme_service.dart';
import 'providers/song_provider.dart';
import 'providers/practice_provider.dart';
import 'providers/user_provider.dart';
import 'screens/home/home_screen.dart';

void main() {
  runApp(const TansenApp());
}

class TansenApp extends StatelessWidget {
  const TansenApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        Provider<ApiService>(
          create: (_) => ApiService(),
        ),
        ChangeNotifierProvider<ThemeService>(
          create: (_) => ThemeService(),
        ),
        ChangeNotifierProvider<SongProvider>(
          create: (context) => SongProvider(
            apiService: context.read<ApiService>(),
          )..fetchSongs(),
        ),
        ChangeNotifierProvider<PracticeProvider>(
          create: (_) => PracticeProvider()..fetchPracticeStats(),
        ),
        ChangeNotifierProvider<UserProvider>(
          create: (_) => UserProvider(),
        ),
      ],
      child: Consumer<ThemeService>(
        builder: (context, themeService, _) {
          return MaterialApp(
            title: 'Tansen',
            debugShowCheckedModeBanner: false,
            theme: AppTheme.lightTheme,
            darkTheme: AppTheme.darkTheme,
            themeMode: themeService.themeMode,
            home: const HomeScreen(),
          );
        },
      ),
    );
  }
}
