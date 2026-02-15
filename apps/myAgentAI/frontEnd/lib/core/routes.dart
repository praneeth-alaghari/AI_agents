import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../../features/auth/login_page.dart';
import '../../features/dashboard/dashboard_page.dart';
import '../../features/email_housekeeper/email_housekeeper_page.dart';
import '../../features/api_keys/api_keys_page.dart';
import 'constants.dart';

final rootNavigatorKey = GlobalKey<NavigatorState>();

final router = GoRouter(
  navigatorKey: rootNavigatorKey,
  initialLocation: '/login', // Start at login
  routes: [
    GoRoute(
      path: '/login',
      builder: (context, state) => const LoginPage(),
    ),
    GoRoute(
      path: '/dashboard',
      builder: (context, state) => const DashboardPage(),
    ),
    GoRoute(
      path: '/email',
      builder: (context, state) => const EmailHousekeeperPage(),
    ),
    GoRoute(
      path: '/api-keys',
      builder: (context, state) => const ApiKeysPage(),
    ),
  ],
  redirect: (context, state) async {
    // Simple redirect logic
    final storage = const FlutterSecureStorage();
    final token = await storage.read(key: AppConstants.authTokenKey);
    final isLoggingIn = state.uri.toString() == '/login';
    
    if (token == null && !isLoggingIn) return '/login';
    if (token != null && isLoggingIn) return '/dashboard';
    
    return null;
  },
);
