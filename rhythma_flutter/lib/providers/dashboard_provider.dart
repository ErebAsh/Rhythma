import 'package:flutter/material.dart';
import 'package:rhythma/l10n/app_localizations.dart';
import '../services/api_client.dart';

class DashboardProvider extends ChangeNotifier {
  bool _loading = true;
  Map<String, dynamic> _userData = {};
  Map<String, dynamic> _cycleData = {};
  Map<String, dynamic> _insights = {};
  String _error = '';

  bool get loading => _loading;
  Map<String, dynamic> get userData => _userData;
  Map<String, dynamic> get cycleData => _cycleData;
  Map<String, dynamic> get insights => _insights;
  String get error => _error;

  DashboardProvider() {
    fetchDashboardData();
  }

  Future<void> fetchDashboardData() async {
    _loading = true;
    _error = '';
    notifyListeners();

    try {
      final dio = ApiClient.dio;
      final response = await dio.get('/dashboard');
      
      _userData = response.data['user'] ?? {};
      _cycleData = response.data['cycle'] ?? {};
      _insights = response.data['insights'] ?? {};
      
    } catch (e) {
      _error = _friendlyErrorMessage(e);
    } finally {
      _loading = false;
      notifyListeners();
    }
  }

  /// Converts a raw exception into a short, user-friendly message suitable
  /// for display in the UI without exposing internal error details.
  String _friendlyErrorMessage(Object error) {
    final msg = error.toString();
    if (msg.contains('SocketException') || msg.contains('TimeoutException')) {
      return 'network_error';
    }
    if (msg.contains('401') || msg.contains('403')) return 'auth_error';
    if (msg.contains('500')) return 'server_error';
    return 'generic_error';
  }

  /// Converts a machine-readable error key into a localized, user-friendly
  /// string. Keeps internal error codes out of the UI.
  String errorKeyToMessage(AppLocalizations l10n, String key) {
    switch (key) {
      case 'network_error':
        return l10n.homeErrorNetwork;
      case 'auth_error':
        return l10n.homeErrorAuth;
      case 'server_error':
        return l10n.homeErrorServer;
      default:
        return l10n.homeErrorGeneric;
    }
  }
}
