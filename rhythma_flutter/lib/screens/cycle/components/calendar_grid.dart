import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../config/theme.dart';
import '../../../config/constants.dart';
import '../../../utils/date_utils.dart';
import '../../../providers/cycle_provider.dart';
import '../../../services/local_storage_service.dart';
import 'log_entry_sheet.dart';

class CalendarGrid extends StatefulWidget {
  final PageController pageController;
  final int initialPageOffset;

  const CalendarGrid({
    super.key,
    required this.pageController,
    required this.initialPageOffset,
  });

  @override
  State<CalendarGrid> createState() => _CalendarGridState();
}

class _CalendarGridState extends State<CalendarGrid> {
  DateTime _monthForIndex(int index) {
    final now = DateTime.now();
    return DateTime(now.year, now.month + (index - widget.initialPageOffset));
  }

  @override
  Widget build(BuildContext context) {
    final cycleProvider = context.watch<CycleProvider>();

    // Calculate cell width based on screen size, similar to before
    final cellWidth = (MediaQuery.of(context).size.width - RhythmaDimens.pageHorizontal * 2 - 32) / 7;

    return SizedBox(
      height: RhythmaDimens.calendarPageViewHeight,
      child: PageView.builder(
        controller: widget.pageController,
        onPageChanged: (index) {
          final month = _monthForIndex(index);
          // Only update if it's different to avoid loops
          if (cycleProvider.displayedMonth.year != month.year ||
              cycleProvider.displayedMonth.month != month.month) {
            // We use read to avoid calling setState during build/scroll
            context.read<CycleProvider>().setDisplayedMonth(month);
          }
        },
        itemBuilder: (context, index) {
          final monthDate = _monthForIndex(index);
          final monthDays = DateTime(monthDate.year, monthDate.month + 1, 0).day;
          final firstWeekday = DateTime(monthDate.year, monthDate.month, 1).weekday % 7;
          
          final today = DateTime.now();

          return Wrap(
            children: [
              // Empty cells for the leading gap
              ...List.generate(
                firstWeekday,
                (_) => SizedBox(width: cellWidth, height: RhythmaDimens.calendarCellHeight),
              ),
              // Actual days
              ...List.generate(monthDays, (i) {
                final day = i + 1;
                final currentDate = DateTime(monthDate.year, monthDate.month, day);
                final phaseColor = cycleProvider.phaseColor(currentDate);
                
          final isSelected = RhythmaDateUtils.isSameDay(cycleProvider.selectedDate, currentDate);
                 final isToday = RhythmaDateUtils.isToday(currentDate);
                
                final hasLog = cycleProvider.hasLogsForDate(currentDate);

                return GestureDetector(
                  onTap: () {
                    context.read<CycleProvider>().selectDate(currentDate);

                    final existingLog = LocalStorageService.getLogForDate(currentDate);

                    LogEntrySheet.show(
                      context,
                      currentDate,
                      existingLog: existingLog,
                    ).then((_) {
                      if (context.mounted) {
                        context.read<CycleProvider>().refreshLogs();
                      }
                    });
                  },
                  child: SizedBox(
                    width: cellWidth,
                    height: RhythmaDimens.calendarCellHeight,
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        AnimatedContainer(
                          duration: const Duration(milliseconds: 180),
                          width: RhythmaDimens.calendarDaySize,
                          height: RhythmaDimens.calendarDaySize,
                          decoration: BoxDecoration(
                            color: isSelected
                                ? phaseColor
                                : phaseColor.withValues(alpha: 0.14),
                            borderRadius: BorderRadius.circular(10),
                            border: isToday && !isSelected
                                ? Border.all(color: phaseColor, width: 1.4)
                                : null,
                          ),
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text(
                                '$day',
                                style: TextStyle(
                                  fontSize: 13,
                                  fontWeight: isToday && !isSelected
                                      ? FontWeight.w800
                                      : FontWeight.w600,
                                  color: isSelected
                                      ? Colors.white
                                      : RhythmaColors.foreground,
                                ),
                              ),
                              // Marker for logged symptoms
                              if (hasLog)
                                Container(
                                  margin: const EdgeInsets.only(top: 1),
                                  width: 4,
                                  height: 4,
                                  decoration: BoxDecoration(
                                    shape: BoxShape.circle,
                                    color: isSelected ? Colors.white : phaseColor,
                                  ),
                                ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              }),
            ],
          );
        },
      ),
    );
  }
}
