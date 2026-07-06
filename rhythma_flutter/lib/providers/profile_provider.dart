import 'package:flutter/material.dart';
import '../services/local_storage_service.dart';

class ProfileProvider extends ChangeNotifier {
  Map<String, dynamic> _profile = {};

  ProfileProvider() {
    _loadProfile();
  }

  Map<String, dynamic> get profile => _profile;

  void _loadProfile() {
    _profile = LocalStorageService.getProfile() ?? {};
    notifyListeners();
  }

  Future<void> saveProfile(Map<String, dynamic> data) async {
    await LocalStorageService.saveProfile(data);
    _profile = data;
    notifyListeners();
  }

  Future<void> mergeProfile(Map<String, dynamic> updates) async {
    await LocalStorageService.mergeProfile(updates);
    _profile = LocalStorageService.getProfile() ?? {};
    notifyListeners();
  }
}
