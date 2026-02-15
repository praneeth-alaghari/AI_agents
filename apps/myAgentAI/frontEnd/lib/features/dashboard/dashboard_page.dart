import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../shared/widgets/app_drawer.dart';
import '../../shared/widgets/stat_card.dart';
import '../../features/email_housekeeper/email_provider.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class DashboardPage extends ConsumerWidget {
  const DashboardPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final emailState = ref.watch(emailProvider);
    
    return Scaffold(
      appBar: AppBar(title: const Text('Dashboard')),
      drawer: const AppDrawer(),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Motivational Quote
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                gradient: const LinearGradient(colors: [Color(0xFF8E2DE2), Color(0xFF4A00E0)]),
                borderRadius: BorderRadius.circular(16),
                boxShadow: const [BoxShadow(color: Colors.black26, blurRadius: 8, offset: Offset(0, 4))],
              ),
              child: const Column(
                children: [
                   Text(
                    '"Small consistent improvements create powerful systems."',
                    style: TextStyle(color: Colors.white, fontSize: 18, fontStyle: FontStyle.italic),
                    textAlign: TextAlign.center,
                  ),
                   SizedBox(height: 8),
                   Text(
                    '- James Clear',
                    style: TextStyle(color: Colors.white70, fontSize: 12),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 32),
            const Text('Your AI Assistant Status', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            
            GridView.count(
              crossAxisCount: 2,
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              crossAxisSpacing: 16,
              mainAxisSpacing: 16,
              childAspectRatio: 1.3,
              children: [
                StatCard(
                  title: 'Total Emails',
                  value: (emailState.stats != null) ? '${emailState.stats!['total_processed_24h'] ?? 0}' : 'Loading...',
                  icon: Icons.mark_email_read,
                  baseColor: Colors.purple,
                ),
                StatCard(
                  title: 'Auto Mode',
                  value: emailState.isAutoMode ? 'ON' : 'OFF',
                  icon: emailState.isAutoMode ? Icons.flash_on : Icons.flash_off,
                  baseColor: emailState.isAutoMode ? Colors.green : Colors.grey,
                ),
                StatCard(
                  title: 'Last Run',
                  value: (emailState.stats != null && emailState.stats!['last_run'] != null)
                      ? _formatTimestamp(emailState.stats!['last_run'])
                      : 'Never',
                  icon: Icons.history,
                  baseColor: Colors.blue,
                ),
                const StatCard(
                  title: 'System Health',
                  value: 'Stable',
                  icon: Icons.check_circle_outline,
                  baseColor: Colors.teal,
                ),
              ],
            ),

            const SizedBox(height: 32),
            const Text('Quick Actions', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            
            Row(
              children: [
                Expanded(
                  child: _ActionCard(
                    title: 'Email Housekeeper',
                    icon: Icons.email,
                    color: Colors.blue,
                    onTap: () => context.push('/email'),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _ActionCard(
                    title: 'API Keys',
                    icon: Icons.vpn_key,
                    color: Colors.orange,
                    onTap: () => context.push('/api-keys'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  String _formatTimestamp(String ts) {
    try {
      final dt = DateTime.parse(ts);
      return '${dt.hour}:${dt.minute.toString().padLeft(2, '0')}';
    } catch (_) {
      return 'Unknown';
    }
  }
}

class _ActionCard extends StatelessWidget {
  final String title;
  final IconData icon;
  final Color color;
  final VoidCallback onTap;

  const _ActionCard({
    required this.title, 
    required this.icon, 
    required this.color, 
    required this.onTap
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: color.withOpacity(0.2), 
              blurRadius: 8, 
              offset: const Offset(0, 4)
            )
          ],
        ),
        child: Column(
          children: [
            CircleAvatar(
              backgroundColor: color.withOpacity(0.1), 
              child: Icon(icon, color: color)
            ),
            const SizedBox(height: 12),
            Text(
              title, 
              style: const TextStyle(fontWeight: FontWeight.bold), 
              textAlign: TextAlign.center
            ),
          ],
        ),
      ),
    );
  }
}
