import 'package:flutter/material.dart';
import '../services/local_storage_service.dart';

class LocaleProvider extends ChangeNotifier {
  Locale _locale;

  LocaleProvider() : _locale = Locale(LocalStorageService.preferredLanguage);

  Locale get locale => _locale;

  void setLocale(Locale locale) {
    if (!['en', 'hi', 'ta', 'te', 'mr', 'kn', 'ml'].contains(locale.languageCode)) return;
    _locale = locale;
    LocalStorageService.setPreferredLanguage(locale.languageCode);
    notifyListeners();
  }
}
