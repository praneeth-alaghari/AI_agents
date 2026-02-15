import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../core/routes.dart'; // Will resolve later
import '../../core/theme.dart';

class AppDrawer extends StatelessWidget {
  const AppDrawer({super.key});

  @override
  Widget build(BuildContext context) {
    return Drawer(
      child: Column(
        children: [
          UserAccountsDrawerHeader(
            decoration: const BoxDecoration(
              gradient: AppTheme.headerGradient,
            ),
            accountName: const Text('My Agent AI', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            accountEmail: const Text('Personal Assistant', style: TextStyle(color: Colors.white70)),
            currentAccountPicture: CircleAvatar(
              backgroundColor: Colors.white,
              child: Icon(Icons.smart_toy, size: 40, color: AppTheme.primaryPurple),
            ),
          ),
          ListTile(
            leading: const Icon(Icons.dashboard),
            title: const Text('Dashboard'),
            onTap: () => context.go('/dashboard'),
          ),
          ListTile(
            leading: const Icon(Icons.email),
            title: const Text('Email Housekeeper'),
            onTap: () => context.go('/email'),
          ),
          ListTile(
            leading: const Icon(Icons.vpn_key),
            title: const Text('API Keys'),
            onTap: () => context.go('/api-keys'),
          ),
          const Divider(),
          const ListTile(
            leading: Icon(Icons.calendar_today, color: Colors.grey),
            title: Text('Calendar (Coming Soon)', style: TextStyle(color: Colors.grey)),
          ),
          const Spacer(),
          ListTile(
            leading: const Icon(Icons.logout, color: AppTheme.errorColor),
            title: const Text('Logout', style: TextStyle(color: AppTheme.errorColor)),
            onTap: () {
               // Implement logout
               context.go('/login');
            },
          ),
          const SizedBox(height: 20),
        ],
      ),
    );
  }
}
