class AppConfig {
  // Usage:
  // flutter run --dart-define=API_BASE_URL=http://your-ip:8000/api/v1
  // Default is Android emulator (10.0.2.2)
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000/api/v1',
  );
}