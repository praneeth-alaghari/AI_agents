import 'package:flutter/foundation.dart';

class AppConstants {
  static const String appName = 'myAgentAI';
  
  static String get baseUrl {
    if (kIsWeb) {
      return 'http://localhost:8000';
    } else if (defaultTargetPlatform == TargetPlatform.android) {
      return 'http://10.0.2.2:8000';
    }
    return 'http://localhost:8000';
  }
  
  // Storage Keys
  static const String authTokenKey = 'auth_token';
  static const String userKey = 'user_data';
  
  // Endpoints
  static const String loginEndpoint = '/auth/login';
  static const String registerEndpoint = '/auth/register';
  static const String apiKeysEndpoint = '/api-keys/';
  static const String emailRunEndpoint = '/email/run';
  static const String emailStatsEndpoint = '/email/stats';
  static const String emailReviewEndpoint = '/email/review';
  static const String emailFeedbackEndpoint = '/email/feedback';
}
