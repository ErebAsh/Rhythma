import 'package:flutter/material.dart';
import 'package:rhythma/l10n/app_localizations.dart';
import '../config/theme.dart';
import '../utils/date_utils.dart';

class CycleProvider extends ChangeNotifier {
  final DateTime _today = DateTime.now();

  late DateTime _selectedDate;
  late DateTime _displayedMonth;

  // Mock logged days
  final Set<String> _loggedDays = {};

  CycleProvider() {
    _selectedDate = DateTime(_today.year, _today.month, _today.day);
    _displayedMonth = DateTime(_today.year, _today.month);

    // Add some mock logged days for visual testing
    _loggedDays.add(RhythmaDateUtils.toDateKey(DateTime(_today.year, _today.month, _today.day - 1)));
    _loggedDays.add(RhythmaDateUtils.toDateKey(DateTime(_today.year, _today.month, _today.day - 3)));
    _loggedDays.add(RhythmaDateUtils.toDateKey(DateTime(_today.year, _today.month, _today.day + 2)));
  }

  DateTime get selectedDate => _selectedDate;
  DateTime get displayedMonth => _displayedMonth;

  void selectDate(DateTime date) {
    if (_selectedDate != date) {
      _selectedDate = date;
      notifyListeners();
    }
  }

  void setDisplayedMonth(DateTime month) {
    if (_displayedMonth.year != month.year || _displayedMonth.month != month.month) {
      _displayedMonth = DateTime(month.year, month.month);
      notifyListeners();
    }
  }

  void jumpToToday() {
    _displayedMonth = DateTime(_today.year, _today.month);
    _selectedDate = DateTime(_today.year, _today.month, _today.day);
    notifyListeners();
  }

  bool hasLogsForDate(DateTime date) {
    return _loggedDays.contains(RhythmaDateUtils.toDateKey(date));
  }

  void toggleLogForDate(DateTime date) {
    final key = RhythmaDateUtils.toDateKey(date);
    if (_loggedDays.contains(key)) {
      _loggedDays.remove(key);
    } else {
      _loggedDays.add(key);
    }
    notifyListeners();
  }

  void refreshLogs() {
    notifyListeners();
  }

  // Phase logic
  String phase(DateTime date, AppLocalizations l10n) {
    final day = date.day;
    if (day <= 5) return l10n.cyclePhasePeriod;
    if (day <= 13) return l10n.cyclePhaseFollicular;
    if (day <= 16) return l10n.cyclePhaseOvulation;
    return l10n.cyclePhaseLuteal;
  }

  Color phaseColor(DateTime date) {
    final day = date.day;
    if (day <= 5) return RhythmaColors.rose;
    if (day <= 13) return RhythmaColors.primary;
    if (day <= 16) return RhythmaColors.teal;
    return RhythmaColors.coral;
  }
}
