import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'email_provider.dart';
import '../../shared/widgets/stat_card.dart';
import '../../shared/widgets/email_card.dart';
import '../../shared/widgets/primary_button.dart';
import '../../shared/widgets/toggle_section.dart';

class EmailHousekeeperPage extends ConsumerWidget {
  const EmailHousekeeperPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final emailState = ref.watch(emailProvider);
    final notifier = ref.read(emailProvider.notifier);

    return Scaffold(
      appBar: AppBar(title: const Text('Email Housekeeper')),
      body: RefreshIndicator(
        onRefresh: () async => notifier.refreshData(),
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Top Section: Control Panel
              Card(
                elevation: 4,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text('Auto Mode', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                          Switch(
                            value: emailState.isAutoMode,
                            onChanged: (val) => notifier.toggleAutoMode(val),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      PrimaryButton(
                        text: 'Run Housekeeper',
                        isLoading: emailState.isLoading,
                        onPressed: () async {
                          await notifier.runHousekeeper();
                          // ignore: use_build_context_synchronously
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Processing complete! Stats updated.')),
                          );
                        },
                        icon: Icons.play_arrow_rounded,
                      ),
                      if (emailState.stats != null && emailState.stats!['last_run'] != null) ...[
                        const SizedBox(height: 8),
                        Text(
                          'Last Run: ${emailState.stats!['last_run']}',
                          style: const TextStyle(color: Colors.grey, fontSize: 12),
                        ),
                      ],
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 24),
              const Text('Today\'s Stats', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
              const SizedBox(height: 16),
              
              // Stats Grid
              // Stats Grid
              if (emailState.error != null)
                Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    children: [
                       const Icon(Icons.error_outline, color: Colors.red, size: 48),
                       const SizedBox(height: 8),
                       Text('Error loading stats: ${emailState.error}', textAlign: TextAlign.center, style: const TextStyle(color: Colors.red)),
                       const SizedBox(height: 8),
                       TextButton(
                         onPressed: () => notifier.refreshData(), 
                         child: const Text('Retry')
                       )
                    ],
                  ),
                )
              else if (emailState.stats != null)
                GridView.count(
                  crossAxisCount: 2,
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  crossAxisSpacing: 16,
                  mainAxisSpacing: 16,
                  childAspectRatio: 1.5,
                  children: [
                    StatCard(
                      title: 'Processed',
                      value: '${emailState.stats!['total_processed_24h'] ?? 0}',
                      icon: Icons.email,
                      baseColor: Colors.blue,
                    ),
                    StatCard(
                      title: 'Needs Review',
                      value: '${emailState.stats!['needs_review_count'] ?? 0}',
                      icon: Icons.rate_review,
                      baseColor: Colors.orange,
                    ),
                    StatCard(
                      title: 'Deleted',
                      value: '${emailState.stats!['deleted_count'] ?? 0}',
                      icon: Icons.delete,
                      baseColor: Colors.red,
                    ),
                    StatCard(
                      title: 'Kept',
                      value: '${emailState.stats!['kept_count'] ?? 0}',
                      icon: Icons.check_circle,
                      baseColor: Colors.green,
                    ),
                  ],
                )
              else
                const Padding(
                   padding: EdgeInsets.all(32.0),
                   child: Center(child: CircularProgressIndicator()),
                 ),

              const SizedBox(height: 32),
              const Text('Needs Review', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
              const SizedBox(height: 16),

              // Review List
              if (emailState.reviewList.isEmpty)
                const Center(child: Padding(
                  padding: EdgeInsets.all(32.0),
                  child: Text('All caught up! No emails to review.', style: TextStyle(color: Colors.grey)),
                ))
              else
                ListView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: emailState.reviewList.length,
                  itemBuilder: (context, index) {
                    final email = emailState.reviewList[index];
                    return EmailCard(
                      sender: email['sender'] ?? 'Unknown',
                      subject: email['subject'] ?? 'No Subject',
                      snippet: email['snippet'] ?? '',
                      priority: email['priority'] ?? 3,
                      confidence: (email['final_score'] ?? 0.0).toDouble(),
                      suggestedAction: email['suggested_action'] ?? 'Unknown',
                      onKeep: () {
                         notifier.submitFeedback(email['id'], 'keep');
                         ScaffoldMessenger.of(context).showSnackBar(
                           const SnackBar(content: Text('Marked as keep. Learning...')),
                         );
                      },
                      onDelete: () {
                        notifier.submitFeedback(email['id'], 'delete');
                        ScaffoldMessenger.of(context).showSnackBar(
                           const SnackBar(content: Text('Marked as delete. Learning...')),
                         );
                      },
                    );
                  },
                ),
                
              const SizedBox(height: 50),
            ],
          ),
        ),
      ),
    );
  }
}
