import 'package:dio/dio.dart';
import '../../core/api_client.dart';
import '../../core/constants.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final apiKeysServiceProvider = Provider((ref) => ApiKeysService(ref.read(dioProvider)));

class ApiKeysService {
  final Dio _dio;

  ApiKeysService(this._dio);

  Future<void> saveKey(String serviceName, String key) async {
    try {
      await _dio.post(AppConstants.apiKeysEndpoint, data: {
        'service_name': serviceName,
        'api_key': key,
      });
    } on DioException catch (e) {
      throw Exception(e.response?.data['message'] ?? 'Failed to save key');
    }
  }

  Future<List<dynamic>> getKeys() async {
    try {
      final response = await _dio.get(AppConstants.apiKeysEndpoint);
      return response.data['data'] as List;
    } on DioException catch (e) {
      throw Exception(e.response?.data['message'] ?? 'Failed to fetch keys');
    }
  }
}
