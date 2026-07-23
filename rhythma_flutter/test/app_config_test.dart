import 'package:flutter_test/flutter_test.dart';
import 'package:rhythma/config/app_config.dart';

void main() {
  test('default API base URL must use HTTPS for release builds', () {
    // The default value (used when --dart-define=API_BASE_URL is not passed)
    // must be HTTPS. Local development overrides via --dart-define are allowed
    // to use HTTP, but the shipped default must be secure.
    expect(
      AppConfig.apiBaseUrl.startsWith('https://'),
      isTrue,
      reason: 'The default API_BASE_URL must be HTTPS. '
          'Pass --dart-define=API_BASE_URL=http://... for local development.',
    );
  });
}
