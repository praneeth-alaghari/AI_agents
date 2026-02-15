import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/api_client.dart';
import 'email_service.dart';

// State models
class EmailState {
  final bool isLoading;
  final bool isAutoMode;
  final Map<String, dynamic>? stats;
  final List<dynamic> reviewList;
  final String? error;

  const EmailState({
    this.isLoading = false,
    this.isAutoMode = false,
    this.stats,
    this.reviewList = const [],
    this.error,
  });

  EmailState copyWith({
    bool? isLoading,
    bool? isAutoMode,
    Map<String, dynamic>? stats,
    List<dynamic>? reviewList,
    String? error,
  }) {
    return EmailState(
      isLoading: isLoading ?? this.isLoading,
      isAutoMode: isAutoMode ?? this.isAutoMode,
      stats: stats ?? this.stats,
      reviewList: reviewList ?? this.reviewList,
      error: error,
    );
  }
}

// Notifier
class EmailNotifier extends StateNotifier<EmailState> {
  final EmailService _service;

  EmailNotifier(this._service) : super(const EmailState()) {
    refreshData();
  }

  Future<void> refreshData() async {
    // Only set loading if we don't present data, or use a separate refreshing flag
    // For now, let's keep it simple: strict loading state
    state = state.copyWith(isLoading: true, error: null);
    try {
      final stats = await _service.getStats();
      final reviews = await _service.getReviewList();
      state = state.copyWith(
        isLoading: false,
        stats: stats,
        reviewList: reviews,
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  void toggleAutoMode(bool value) {
    state = state.copyWith(isAutoMode: value);
  }

  Future<void> runHousekeeper() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      await _service.runHousekeeper(autoMode: state.isAutoMode);
      // Wait for backend to process
      await Future.delayed(const Duration(seconds: 1)); 
      await refreshData();
    } catch (e) {
        state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> submitFeedback(int emailId, String action) async {
    // Optimistic update could be done here, but safe to refresh for now
    try {
      await _service.submitFeedback(emailId, action);
      // Remove from local list immediately for better UX
      final currentList = List.from(state.reviewList);
      currentList.removeWhere((email) => email['id'] == emailId);
      state = state.copyWith(reviewList: currentList);
      
      // Refresh background stats
      final stats = await _service.getStats();
      state = state.copyWith(stats: stats);
      
    } catch (e) {
      state = state.copyWith(error: e.toString());
    }
  }
}

final emailProvider = StateNotifierProvider<EmailNotifier, EmailState>((ref) {
  final service = ref.read(emailServiceProvider);
  return EmailNotifier(service);
});
