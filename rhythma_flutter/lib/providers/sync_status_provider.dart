import 'package:flutter/material.dart';

/// Sync status for Issue #20 - Sync Status Indicator
enum SyncStatus {
  synced,      // All data synced with Firestore
  syncing,     // Currently syncing
  pending,     // Has pending changes waiting for connectivity
  offline,     // No internet connection
  error,       // Sync failed
}

/// Singleton provider for sync status - exposed for Issue #20 UI indicator
class SyncStatusProvider extends ChangeNotifier {
  static SyncStatusProvider? _instance;
  static SyncStatusProvider get instance => _instance!;
  static bool get hasInstance => _instance != null;

  SyncStatusProvider() {
    _instance = this;
  }

  SyncStatus _cycleStatus = SyncStatus.synced;
  SyncStatus _profileStatus = SyncStatus.synced;
  String? _cycleError;
  String? _profileError;
  DateTime? _lastSyncTime;

  SyncStatus get cycleStatus => _cycleStatus;
  SyncStatus get profileStatus => _profileStatus;
  String? get cycleError => _cycleError;
  String? get profileError => _profileError;
  DateTime? get lastSyncTime => _lastSyncTime;

  /// Overall status - synced only if both are synced
  SyncStatus get overallStatus {
    if (_cycleStatus == SyncStatus.syncing || _profileStatus == SyncStatus.syncing) {
      return SyncStatus.syncing;
    }
    if (_cycleStatus == SyncStatus.error || _profileStatus == SyncStatus.error) {
      return SyncStatus.error;
    }
    if (_cycleStatus == SyncStatus.pending || _profileStatus == SyncStatus.pending) {
      return SyncStatus.pending;
    }
    if (_cycleStatus == SyncStatus.offline || _profileStatus == SyncStatus.offline) {
      return SyncStatus.offline;
    }
    return SyncStatus.synced;
  }

  /// Called by FirestoreService to update status
  void updateStatus(SyncStatus status, String type, {String? error}) {
    switch (type) {
      case 'cycle':
        _cycleStatus = status;
        _cycleError = error;
        break;
      case 'profile':
        _profileStatus = status;
        _profileError = error;
        break;
    }
    if (status == SyncStatus.synced) {
      _lastSyncTime = DateTime.now();
    }
    notifyListeners();
  }

  /// Called when connectivity is lost
  void setOffline() {
    _cycleStatus = SyncStatus.offline;
    _profileStatus = SyncStatus.offline;
    notifyListeners();
  }

  /// Called when connectivity is restored
  void setOnline() {
    _cycleStatus = SyncStatus.pending;
    _profileStatus = SyncStatus.pending;
    notifyListeners();
  }
}