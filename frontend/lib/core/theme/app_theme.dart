import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  // Docker Desktop-inspired blue color palette
  static const Color primaryBlue = Color(0xFF0DB7ED); // Docker blue
  static const Color darkBlue = Color(0xFF066DA5);
  static const Color deepBlue = Color(0xFF003F5C);
  static const Color lightBlue = Color(0xFF5BC0DE);
  static const Color paleBlue = Color(0xFFE7F6FC);
  
  // Accent colors
  static const Color accentOrange = Color(0xFFFF9500);
  static const Color successGreen = Color(0xFF1DB954); // Spotify green
  static const Color errorRed = Color(0xFFFF3B30);
  static const Color warningYellow = Color(0xFFFFCC00);
  
  // Spotify-inspired dark theme colors
  static const Color spotifyBlack = Color(0xFF121212);
  static const Color spotifyDarkGray = Color(0xFF181818);
  static const Color spotifyGray = Color(0xFF282828);
  static const Color spotifyLightGray = Color(0xFFB3B3B3);
  
  // Light theme colors
  static const Color darkGray = Color(0xFF1E1E1E);
  static const Color mediumGray = Color(0xFF6C757D);
  static const Color lightGray = Color(0xFFF8F9FA);
  static const Color white = Color(0xFFFFFFFF);

  static ThemeData lightTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    primaryColor: primaryBlue,
    scaffoldBackgroundColor: white,
    
    colorScheme: const ColorScheme.light(
      primary: primaryBlue,
      secondary: darkBlue,
      tertiary: lightBlue,
      surface: lightGray,
      error: errorRed,
      onPrimary: white,
      onSecondary: white,
      onSurface: darkGray,
      onError: white,
    ),
    
    textTheme: GoogleFonts.interTextTheme().copyWith(
      displayLarge: GoogleFonts.inter(
        fontSize: 32,
        fontWeight: FontWeight.bold,
        color: darkGray,
        letterSpacing: -0.5,
      ),
      displayMedium: GoogleFonts.inter(
        fontSize: 28,
        fontWeight: FontWeight.bold,
        color: darkGray,
        letterSpacing: -0.5,
      ),
      displaySmall: GoogleFonts.inter(
        fontSize: 24,
        fontWeight: FontWeight.bold,
        color: darkGray,
        letterSpacing: -0.5,
      ),
      headlineMedium: GoogleFonts.inter(
        fontSize: 20,
        fontWeight: FontWeight.bold,
        color: darkGray,
      ),
      titleLarge: GoogleFonts.inter(
        fontSize: 18,
        fontWeight: FontWeight.w600,
        color: darkGray,
      ),
      titleMedium: GoogleFonts.inter(
        fontSize: 16,
        fontWeight: FontWeight.w600,
        color: darkGray,
      ),
      bodyLarge: GoogleFonts.inter(
        fontSize: 16,
        fontWeight: FontWeight.normal,
        color: darkGray,
      ),
      bodyMedium: GoogleFonts.inter(
        fontSize: 14,
        fontWeight: FontWeight.normal,
        color: mediumGray,
      ),
      labelLarge: GoogleFonts.inter(
        fontSize: 14,
        fontWeight: FontWeight.w600,
        color: white,
      ),
    ),
    
    appBarTheme: AppBarTheme(
      backgroundColor: white,
      elevation: 0,
      centerTitle: false,
      iconTheme: const IconThemeData(color: darkGray),
      titleTextStyle: GoogleFonts.inter(
        fontSize: 20,
        fontWeight: FontWeight.bold,
        color: darkGray,
      ),
    ),
    
    cardTheme: const CardThemeData(
      color: lightGray,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.all(Radius.circular(8)),
      ),
    ),
    
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: primaryBlue,
        foregroundColor: white,
        elevation: 0,
        padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(500), // Spotify pill shape
        ),
        textStyle: GoogleFonts.inter(
          fontSize: 16,
          fontWeight: FontWeight.bold,
          letterSpacing: 0.5,
        ),
      ),
    ),
    
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: darkGray,
        side: const BorderSide(color: mediumGray, width: 1),
        padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(500),
        ),
        textStyle: GoogleFonts.inter(
          fontSize: 16,
          fontWeight: FontWeight.bold,
        ),
      ),
    ),
    
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: lightGray,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: BorderSide.none,
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: BorderSide.none,
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: const BorderSide(color: primaryBlue, width: 2),
      ),
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
    ),
    
    bottomNavigationBarTheme: const BottomNavigationBarThemeData(
      backgroundColor: white,
      selectedItemColor: primaryBlue,
      unselectedItemColor: mediumGray,
      type: BottomNavigationBarType.fixed,
      elevation: 0,
      showSelectedLabels: true,
      showUnselectedLabels: true,
    ),
  );

  static ThemeData darkTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    primaryColor: primaryBlue,
    scaffoldBackgroundColor: spotifyBlack,
    
    colorScheme: const ColorScheme.dark(
      primary: primaryBlue,
      secondary: lightBlue,
      tertiary: darkBlue,
      surface: spotifyGray,
      error: errorRed,
      onPrimary: white,
      onSecondary: spotifyBlack,
      onSurface: white,
      onError: white,
    ),
    
    textTheme: GoogleFonts.interTextTheme(ThemeData.dark().textTheme).copyWith(
      displayLarge: GoogleFonts.inter(
        fontSize: 32,
        fontWeight: FontWeight.bold,
        color: white,
        letterSpacing: -0.5,
      ),
      displayMedium: GoogleFonts.inter(
        fontSize: 28,
        fontWeight: FontWeight.bold,
        color: white,
        letterSpacing: -0.5,
      ),
      displaySmall: GoogleFonts.inter(
        fontSize: 24,
        fontWeight: FontWeight.bold,
        color: white,
        letterSpacing: -0.5,
      ),
      headlineMedium: GoogleFonts.inter(
        fontSize: 20,
        fontWeight: FontWeight.bold,
        color: white,
      ),
      titleLarge: GoogleFonts.inter(
        fontSize: 18,
        fontWeight: FontWeight.w600,
        color: white,
      ),
      titleMedium: GoogleFonts.inter(
        fontSize: 16,
        fontWeight: FontWeight.w600,
        color: white,
      ),
      bodyLarge: GoogleFonts.inter(
        fontSize: 16,
        fontWeight: FontWeight.normal,
        color: white,
      ),
      bodyMedium: GoogleFonts.inter(
        fontSize: 14,
        fontWeight: FontWeight.normal,
        color: spotifyLightGray,
      ),
      labelLarge: GoogleFonts.inter(
        fontSize: 14,
        fontWeight: FontWeight.w600,
        color: white,
      ),
    ),
    
    appBarTheme: AppBarTheme(
      backgroundColor: spotifyBlack,
      elevation: 0,
      centerTitle: false,
      iconTheme: const IconThemeData(color: white),
      titleTextStyle: GoogleFonts.inter(
        fontSize: 20,
        fontWeight: FontWeight.bold,
        color: white,
      ),
    ),
    
    cardTheme: const CardThemeData(
      color: spotifyGray,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.all(Radius.circular(8)),
      ),
    ),
    
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: primaryBlue,
        foregroundColor: white,
        elevation: 0,
        padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(500),
        ),
        textStyle: GoogleFonts.inter(
          fontSize: 16,
          fontWeight: FontWeight.bold,
          letterSpacing: 0.5,
        ),
      ),
    ),
    
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: white,
        side: const BorderSide(color: spotifyLightGray, width: 1),
        padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(500),
        ),
        textStyle: GoogleFonts.inter(
          fontSize: 16,
          fontWeight: FontWeight.bold,
        ),
      ),
    ),
    
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: spotifyGray,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: BorderSide.none,
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: BorderSide.none,
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: const BorderSide(color: primaryBlue, width: 2),
      ),
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
    ),
    
    bottomNavigationBarTheme: const BottomNavigationBarThemeData(
      backgroundColor: spotifyDarkGray,
      selectedItemColor: primaryBlue,
      unselectedItemColor: spotifyLightGray,
      type: BottomNavigationBarType.fixed,
      elevation: 0,
      showSelectedLabels: true,
      showUnselectedLabels: true,
    ),
  );
}
