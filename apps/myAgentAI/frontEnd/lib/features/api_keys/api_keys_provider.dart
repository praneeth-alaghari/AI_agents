import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'api_keys_service.dart';

final apiKeysStateProvider = StateNotifierProvider<ApiKeysNotifier, AsyncValue<List<dynamic>>>((ref) {
  return ApiKeysNotifier(ref.read(apiKeysServiceProvider));
});

class ApiKeysNotifier extends StateNotifier<AsyncValue<List<dynamic>>> {
  final ApiKeysService _service;

  ApiKeysNotifier(this._service) : super(const AsyncValue.loading()) {
    fetchKeys();
  }

  Future<void> fetchKeys() async {
    try {
      final keys = await _service.getKeys();
      state = AsyncValue.data(keys);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> saveKey(String service, String key) async {
    // state = const AsyncValue.loading();
    try {
      await _service.saveKey(service, key);
      await fetchKeys(); // Refresh list
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }
}
