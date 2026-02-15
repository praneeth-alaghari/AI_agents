import 'package:flutter/material.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/api_client.dart';
import '../../core/constants.dart';
import '../../core/theme.dart';
import '../../shared/widgets/primary_button.dart';

class LoginPage extends ConsumerStatefulWidget {
  const LoginPage({super.key});

  @override
  ConsumerState<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends ConsumerState<LoginPage> with SingleTickerProviderStateMixin {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;
  late AnimationController _animController;
  late Animation<double> _fadeAnim;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(vsync: this, duration: const Duration(milliseconds: 800));
    _fadeAnim = CurvedAnimation(parent: _animController, curve: Curves.easeIn);
    _animController.forward();
  }

  @override
  void dispose() {
    _animController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _login() async {
    setState(() => _isLoading = true);
    final dio = ref.read(dioProvider);
    final storage = ref.read(secureStorageProvider);

    try {
      final response = await dio.post(AppConstants.loginEndpoint, data: {
        'email': _emailController.text, // "user@example.com"
        'password': _passwordController.text, // "password"
      });
      
      final token = response.data['data']['token']['access_token'];
      await storage.write(key: AppConstants.authTokenKey, value: token);
      
      if (mounted) context.go('/dashboard');
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
           SnackBar(content: Text('Login Failed: ${e.toString()}'), backgroundColor: AppTheme.errorColor),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        padding: const EdgeInsets.all(24),
        decoration: const BoxDecoration(
          gradient: AppTheme.headerGradient,
        ),
        child: Center(
          child: FadeTransition(
            opacity: _fadeAnim,
            child: Card(
              elevation: 8,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
              child: Padding(
                padding: const EdgeInsets.all(32),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.smart_toy, size: 64, color: AppTheme.primaryBlue),
                    const SizedBox(height: 16),
                    const Text('Welcome Back', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    const Text('Sign in to continue', style: TextStyle(color: Colors.grey)),
                    const SizedBox(height: 32),
                    
                    TextFormField(
                      controller: _emailController,
                      decoration: const InputDecoration(labelText: 'Email', prefixIcon: Icon(Icons.email)),
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _passwordController,
                      decoration: const InputDecoration(labelText: 'Password', prefixIcon: Icon(Icons.lock)),
                      obscureText: true,
                    ),
                    const SizedBox(height: 32),
                    
                    PrimaryButton(
                      text: 'Login',
                      isLoading: _isLoading,
                      onPressed: _login,
                    ),
                    const SizedBox(height: 16),
                    TextButton(
                      onPressed: _showSignUpDialog,
                      child: const Text('Create Account'),
                    ),
                    TextButton(
                      onPressed: _loginAsGuest,
                      child: const Text('Continue as Guest', style: TextStyle(color: Colors.grey)),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  void _showSignUpDialog() {
    final usernameController = TextEditingController();
    final emailController = TextEditingController();
    final passwordController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Create Account'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: usernameController,
              decoration: const InputDecoration(labelText: 'Username', prefixIcon: Icon(Icons.person)),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: emailController,
              decoration: const InputDecoration(labelText: 'Email', prefixIcon: Icon(Icons.email)),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: passwordController,
              decoration: const InputDecoration(labelText: 'Password', prefixIcon: Icon(Icons.lock)),
              obscureText: true,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(context); // Close dialog first
              setState(() => _isLoading = true);
              
              final dio = ref.read(dioProvider);
              final storage = ref.read(secureStorageProvider);

              try {
                final response = await dio.post(AppConstants.registerEndpoint, data: {
                  'username': usernameController.text,
                  'email': emailController.text,
                  'password': passwordController.text,
                });
                
                final token = response.data['data']['token']['access_token'];
                await storage.write(key: AppConstants.authTokenKey, value: token);
                
                if (mounted) {
                   ScaffoldMessenger.of(context).showSnackBar(
                     const SnackBar(content: Text('Account Created! Welcome!'), backgroundColor: AppTheme.successColor),
                   );
                   context.go('/dashboard');
                }
              } catch (e) {
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                     SnackBar(content: Text('Registration Failed: $e'), backgroundColor: AppTheme.errorColor),
                  );
                }
              } finally {
                if (mounted) setState(() => _isLoading = false);
              }
            },
            child: const Text('Register'),
          ),
        ],
      ),
    );
  }

  Future<void> _loginAsGuest() async {
    setState(() => _isLoading = true);
    final dio = ref.read(dioProvider);
    final storage = ref.read(secureStorageProvider);

    try {
      Response response;
      try {
        // Try login first
         response = await dio.post(AppConstants.loginEndpoint, data: {
          'email': 'guest@example.com',
          'password': 'guestpassword123'
        });
      } catch (e) {
        // If login fails (likely 401), try register
         print('Guest login failed, trying to register new guest account...');
         response = await dio.post(AppConstants.registerEndpoint, data: {
          'email': 'guest@example.com',
          'username': 'Guest User',
          'password': 'guestpassword123'
        });
      }

      final token = response.data['data']['token']['access_token'];
      await storage.write(key: AppConstants.authTokenKey, value: token);
      
      if (mounted) {
         ScaffoldMessenger.of(context).showSnackBar(
           const SnackBar(content: Text('Logged in as Guest'), backgroundColor: Colors.green),
         );
         context.go('/dashboard');
      }

    } catch (e) {
       if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Guest Login Failed: $e'), backgroundColor: Colors.red),
          );
       }
    } finally {
       if (mounted) setState(() => _isLoading = false);
    }
  }
}
