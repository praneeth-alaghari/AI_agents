import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'constants.dart';

// Provider for Secure Storage
final secureStorageProvider = Provider((ref) => const FlutterSecureStorage());

// Provider for Dio
final dioProvider = Provider((ref) {
  final dio = Dio(BaseOptions(
    baseUrl: AppConstants.baseUrl,
    connectTimeout: const Duration(seconds: 15),
    receiveTimeout: const Duration(seconds: 30),
    headers: {'Content-Type': 'application/json'},
  ));

  final storage = ref.read(secureStorageProvider);

  dio.interceptors.add(InterceptorsWrapper(
    onRequest: (options, handler) async {
      print('🌐 [DIO] Request: ${options.method} ${options.uri}');
      // print('   Headers: ${options.headers}'); // Uncomment if needed
      if (options.data != null) print('   Data: ${options.data}');
      
      final token = await storage.read(key: AppConstants.authTokenKey);
      if (token != null && token != 'guest_token') {
        options.headers['Authorization'] = 'Bearer $token';
      }
      return handler.next(options);
    },
    onResponse: (response, handler) {
      print('✅ [DIO] Response: ${response.statusCode} from ${response.requestOptions.uri}');
      // print('   Data: ${response.data}'); // Uncomment for full verbosity
      return handler.next(response);
    },
    onError: (DioException e, handler) {
      print('🛑 [DIO] Error: ${e.message} on ${e.requestOptions.uri}');
      if (e.response != null) {
          print('   Status: ${e.response?.statusCode}');
          print('   Response: ${e.response?.data}');
      }
      return handler.next(e);
    },
  ));

  return dio;
});
