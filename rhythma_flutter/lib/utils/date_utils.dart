/// Shared date utility helpers to reduce repeated date comparison logic
/// across the app.
class RhythmaDateUtils {
  RhythmaDateUtils._();

  /// Returns an ISO-8601 date string (yyyy-MM-dd) for [date].
  static String toDateKey(DateTime date) =>
      '${date.year.toString().padLeft(4, '0')}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';

  /// Returns true if [a] and [b] represent the same calendar day.
  static bool isSameDay(DateTime a, DateTime b) =>
      a.year == b.year && a.month == b.month && a.day == b.day;

  /// Returns true if [date] is today.
  static bool isToday(DateTime date) => isSameDay(date, DateTime.now());

  /// Returns true if [date] falls in the same year+month as [month].
  static bool isSameMonth(DateTime date, DateTime month) =>
      date.year == month.year && date.month == month.month;

  /// Returns the number of days in the given [month].
  static int daysInMonth(DateTime month) =>
      DateTime(month.year, month.month + 1, 0).day;
}
