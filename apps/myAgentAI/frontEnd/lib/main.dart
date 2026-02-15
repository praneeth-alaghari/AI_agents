import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/routes.dart'; // To use the router
import 'core/theme.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  // Initialize other services if needed
  
  runApp(const ProviderScope(child: MyAgentApp()));
}

class MyAgentApp extends StatelessWidget {
  const MyAgentApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'myAgentAI',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      routerConfig: router,
    );
  }
}
