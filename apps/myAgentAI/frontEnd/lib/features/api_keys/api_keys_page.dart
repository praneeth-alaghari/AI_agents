import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'api_keys_provider.dart';
import '../../core/theme.dart';
import '../../shared/widgets/primary_button.dart';

class ApiKeysPage extends ConsumerStatefulWidget {
  const ApiKeysPage({super.key});

  @override
  ConsumerState<ApiKeysPage> createState() => _ApiKeysPageState();
}

class _ApiKeysPageState extends ConsumerState<ApiKeysPage> {
  final _formKey = GlobalKey<FormState>();
  final _openaiController = TextEditingController();
  final _gmailController = TextEditingController();
  bool _isLoading = false;

  @override
  void dispose() {
    _openaiController.dispose();
    _gmailController.dispose();
    super.dispose();
  }

  Future<void> _saveKeys() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);
    final notifier = ref.read(apiKeysStateProvider.notifier);

    try {
      if (_openaiController.text.isNotEmpty) {
        await notifier.saveKey('openai', _openaiController.text);
      }
      
      // Gmail is mandatory per UI prompt, but frontend form validation handles empty check.
      // If backend only accepts specific services, we send them.
      if (_gmailController.text.isNotEmpty) {
        await notifier.saveKey('gmail', _gmailController.text);
      }

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Keys saved successfully!')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: AppTheme.errorColor),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    // Watch current keys to show status
    final keysAsync = ref.watch(apiKeysStateProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('API Keys Management')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Configure your AI Services',
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              const Text(
                'Manage your personal API keys securely. Your Gmail key is encrypted and stored in your private vault.',
                style: TextStyle(color: Colors.grey),
              ),
              const SizedBox(height: 32),

              // OpenAI Key
              _buildKeyField(
                controller: _openaiController,
                label: 'OpenAI API Key',
                icon: Icons.smart_toy,
                hint: 'sk-...',
                isOptional: true,
                helperText: 'Optional. If not provided, system default key will be used.',
              ),
              const SizedBox(height: 24),

              // Gmail Key
              _buildKeyField(
                controller: _gmailController,
                label: 'Gmail API Key',
                icon: Icons.email,
                hint: 'ya29... or {"token": ...}',
                isOptional: false,
                helperText: 'Paste access token or full JSON for auto-refresh.',
              ),

              const SizedBox(height: 40),
              PrimaryButton(
                text: 'Save & Secure',
                onPressed: _saveKeys,
                isLoading: _isLoading,
                icon: Icons.lock,
              ),

              const SizedBox(height: 32),
              const Divider(),
              const SizedBox(height: 16),
              const Text('Active Keys Status', style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              
              keysAsync.when(
                data: (keys) => Column(
                  children: keys.map((k) => ListTile(
                    leading: const Icon(Icons.check_circle, color: AppTheme.successColor),
                    title: Text(k['service_name'].toString().toUpperCase()),
                    subtitle: Text('Active since: ${k['created_at']}'),
                  )).toList(),
                ),
                loading: () => const LinearProgressIndicator(),
                error: (err, _) => Text('Error loading keys: $err', style: const TextStyle(color: Colors.red)),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildKeyField({
    required TextEditingController controller,
    required String label,
    required IconData icon,
    required String hint,
    required bool isOptional,
    required String helperText,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        TextFormField(
          controller: controller,
          obscureText: true,
          decoration: InputDecoration(
            labelText: label,
            hintText: hint,
            prefixIcon: Icon(icon),
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
            filled: true,
            fillColor: Colors.white,
          ),
          validator: (value) {
            if (!isOptional && (value == null || value.isEmpty)) {
              return '$label is required';
            }
            return null;
          },
        ),
        const SizedBox(height: 6),
        Text(helperText, style: TextStyle(fontSize: 12, color: Colors.grey.shade600)),
      ],
    );
  }
}
