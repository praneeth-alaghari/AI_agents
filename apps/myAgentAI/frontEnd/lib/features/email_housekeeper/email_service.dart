import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/api_client.dart';
import '../../core/constants.dart';

// Provider
final emailServiceProvider = Provider((ref) => EmailService(ref.read(dioProvider)));

class EmailService {
  final Dio _dio;

  EmailService(this._dio);

  Future<Map<String, dynamic>> runHousekeeper({bool autoMode = false}) async {
    try {
      final response = await _dio.post(AppConstants.emailRunEndpoint, data: {
        'auto_mode': autoMode,
        'max_emails': 20, // Default batch size
      });
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> getStats() async {
    try {
      final response = await _dio.get(AppConstants.emailStatsEndpoint);
      return response.data['data'];
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<List<dynamic>> getReviewList() async {
    try {
      final response = await _dio.get(AppConstants.emailReviewEndpoint);
      return response.data['data'] as List;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<void> submitFeedback(int emailId, String action) async {
    try {
      await _dio.post(AppConstants.emailFeedbackEndpoint, data: {
        'email_record_id': emailId,
        'user_action': action,
      });
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  String _handleError(DioException e) {
    if (e.response != null && e.response!.data != null) {
      return e.response!.data['message'] ?? 'An error occurred';
    }
    return 'Connection error. Please check your internet.';
  }
}
