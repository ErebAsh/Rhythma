import 'package:flutter_test/flutter_test.dart';
import 'package:rhythma/services/export_service.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('ExportService Tests', () {
    test('buildExportJson creates valid JSON export string', () {
      final jsonString = ExportService.buildExportJson();
      expect(jsonString, isNotEmpty);
      expect(jsonString, contains('export_date'));
      expect(jsonString, contains('profile'));
    });
  });
}
