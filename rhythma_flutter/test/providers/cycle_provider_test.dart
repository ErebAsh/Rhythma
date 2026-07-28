import 'package:flutter_test/flutter_test.dart';
import 'package:rhythma/models/cycle_log.dart';
import 'package:rhythma/providers/cycle_provider.dart';
import 'package:rhythma/services/local_storage_service.dart';

void main() {
  setUp(() {
    LocalStorageService.isTesting = true;
    LocalStorageService.mockCycleLogs = [];
  });

  group('CycleProvider.phase Calculation Regression Tests (#130)', () {
    test('phase() calculates cycle phase from period start date across month boundaries', () async {
      // 1. Set period start date near the end of a month (e.g., Jan 28)
      final periodStartDate = DateTime(2026, 1, 28);
      
      LocalStorageService.mockCycleLogs = [
        CycleLog(
          date: periodStartDate,
          flow: 'heavy',
          symptoms: ['cramps'],
        ),
      ];

      final provider = CycleProvider();

      // 2. Test Day 3 of cycle (Jan 30 - Menstrual Phase)
      final day3 = DateTime(2026, 1, 30);
      expect(provider.getPhaseForDate(day3), equals('menstrual'));

      // 3. Test Month Boundary Crossing: Day 10 of cycle (Feb 6 - Follicular Phase)
      // If code improperly checked calendar day of month (6), it would fail or return wrong phase.
      final day10 = DateTime(2026, 2, 6);
      expect(provider.getPhaseForDate(day10), equals('follicular'));

      // 4. Test Day 15 of cycle (Feb 11 - Ovulatory Phase)
      final day15 = DateTime(2026, 2, 11);
      expect(provider.getPhaseForDate(day15), equals('ovulatory'));

      // 5. Test Day 22 of cycle (Feb 18 - Luteal Phase)
      final day22 = DateTime(2026, 2, 18);
      expect(provider.getPhaseForDate(day22), equals('luteal'));
    });
  });
}