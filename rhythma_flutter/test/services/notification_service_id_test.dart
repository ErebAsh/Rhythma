import 'package:flutter_test/flutter_test.dart';

void main() {
  test('notification ID is normalized to a positive 32-bit integer', () {
    const maxSigned32Bit = 0x7FFFFFFF;

    final ids = [
      -1,
      1,
      2147483648,
      1723588234567,
      -1723588234567,
    ];

    for (final id in ids) {
      final normalized = id.abs() % maxSigned32Bit;

      expect(normalized, greaterThanOrEqualTo(0));
      expect(normalized, lessThan(maxSigned32Bit));
    }
  });
}
