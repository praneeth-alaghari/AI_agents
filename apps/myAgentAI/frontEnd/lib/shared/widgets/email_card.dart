import 'package:flutter/material.dart';
import '../../core/theme.dart';

class EmailCard extends StatelessWidget {
  final String sender;
  final String subject;
  final String snippet;
  final int priority;
  final double confidence;
  final String suggestedAction;
  final VoidCallback onDelete;
  final VoidCallback onKeep;

  const EmailCard({
    super.key,
    required this.sender,
    required this.subject,
    required this.snippet,
    required this.priority,
    required this.confidence,
    required this.suggestedAction,
    required this.onDelete,
    required this.onKeep,
  });

  Color _getPriorityColor(int p) {
    if (p <= 2) return AppTheme.errorColor;
    if (p == 3) return AppTheme.warningColor;
    return AppTheme.successColor;
  }
  
  String _getPriorityLabel(int p) {
    const labels = {1: 'Critical', 2: 'High', 3: 'Medium', 4: 'Low', 5: 'Spam'};
    return labels[p] ?? 'Unknown';
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      elevation: 3,
      shadowColor: Colors.black12,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Head: Priority & Confidence
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                  decoration: BoxDecoration(
                    color: _getPriorityColor(priority).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    _getPriorityLabel(priority).toUpperCase(),
                    style: TextStyle(
                      color: _getPriorityColor(priority),
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ),
                Text(
                  '${(confidence * 100).toStringAsFixed(0)}% Confidence',
                  style: const TextStyle(
                    color: Colors.grey,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            
            // Body: Subject & Sender
            Text(
              subject,
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 16,
                color: AppTheme.fontColor,
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 4),
            Text(
              sender,
              style: const TextStyle(color: Colors.grey, fontSize: 13),
            ),
            const SizedBox(height: 8),
            Text(
              snippet,
              style: TextStyle(color: Colors.grey.shade700, fontSize: 14),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
            
            const Divider(height: 24),
            
            // Actions
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'AI Suggests: ${suggestedAction.replaceAll('_', ' ').toUpperCase()}',
                  style: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.primaryPurple,
                  ),
                ),
                Row(
                  children: [
                    OutlinedButton(
                      onPressed: onKeep,
                      style: OutlinedButton.styleFrom(
                        foregroundColor: AppTheme.successColor,
                        side: BorderSide(color: AppTheme.successColor),
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                      ),
                      child: const Text('Keep'),
                    ),
                    const SizedBox(width: 8),
                    ElevatedButton(
                      onPressed: onDelete,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppTheme.errorColor,
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                      ),
                      child: const Text('Delete'),
                    ),
                  ],
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
