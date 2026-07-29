import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:rhythma/l10n/app_localizations_en.dart';
import 'package:rhythma/providers/cycle_provider.dart';
import 'package:rhythma/services/local_storage_service.dart';
import '../test_helpers/local_storage_fixture.dart';

void main() {
  late Directory tempDir;
  final l10n = AppLocalizationsEn();

  setUp(() async {
    tempDir = await setUpLocalStorage();
    await LocalStorageService.mergeProfile({'last_period': '2026-01-28'});
  });

  tearDown(() async {
    await tearDownLocalStorage(tempDir);
  });

  group('CycleProvider.phase Calculation Regression Tests (#130)', () {
    test('phase() calculates cycle phase from period start date across month boundaries', () async {
      final provider = CycleProvider();

      // Day 3 of cycle (Jan 30 - Menstrual Phase)
      final day3 = DateTime(2026, 1, 30);
      expect(provider.phase(day3, l10n), equals('Period'));

      // Month boundary: Day 10 of cycle (Feb 6 - Follicular Phase)
      final day10 = DateTime(2026, 2, 6);
      expect(provider.phase(day10, l10n), equals('Follicular'));

      // Day 15 of cycle (Feb 11 - Ovulatory Phase)
      final day15 = DateTime(2026, 2, 11);
      expect(provider.phase(day15, l10n), equals('Ovulation'));

      // Day 22 of cycle (Feb 18 - Luteal Phase)
      final day22 = DateTime(2026, 2, 18);
      expect(provider.phase(day22, l10n), equals('Luteal'));
    });
  });
}
