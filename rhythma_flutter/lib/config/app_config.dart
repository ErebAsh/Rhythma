import 'package:flutter/foundation.dart';

class AppConfig {
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue:
        kIsWeb ? 'http://localhost:8000/api/v1' : 'http://10.0.2.2:8000/api/v1',
  );
}