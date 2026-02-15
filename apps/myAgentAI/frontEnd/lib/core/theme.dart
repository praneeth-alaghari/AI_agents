import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  // Colors
  static const primaryBlue = Color(0xFF6C63FF);
  static const primaryPurple = Color(0xFF9C27B0);
  static const backgroundStart = Color(0xFFF3F4F6);
  static const backgroundEnd = Color(0xFFE5E7EB);
  static const cardColor = Colors.white;
  static const errorColor = Color(0xFFE53935);
  static const successColor = Color(0xFF43A047);
  static const warningColor = Color(0xFFFFA000);
  static const fontColor = Color(0xFF1F2937);

  static final ThemeData lightTheme = ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(
      seedColor: primaryBlue,
      brightness: Brightness.light,
    ),
    scaffoldBackgroundColor: backgroundStart,
    textTheme: GoogleFonts.interTextTheme().apply(
      bodyColor: fontColor,
      displayColor: fontColor,
    ),
    cardTheme: CardThemeData(
      color: cardColor,
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      shadowColor: Colors.black12,
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: Colors.transparent,
      elevation: 0,
      centerTitle: true,
      titleTextStyle: TextStyle(
        color: fontColor,
        fontSize: 20,
        fontWeight: FontWeight.bold,
      ),
      iconTheme: IconThemeData(color: fontColor),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: primaryBlue,
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        elevation: 4,
      ),
    ),
  );
  
  // Custom Gradients
  static const LinearGradient headerGradient = LinearGradient(
    colors: [primaryBlue, primaryPurple],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
}
