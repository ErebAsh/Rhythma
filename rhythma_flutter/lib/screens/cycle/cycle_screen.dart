import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import 'package:rhythma/l10n/app_localizations.dart';
import '../../config/theme.dart';
import '../../components/shared.dart';
import '../../providers/theme_provider.dart';

class CycleScreen extends StatefulWidget {
  const CycleScreen({Key? key}) : super(key: key);

  @override
  State<CycleScreen> createState() => _CycleScreenState();
}

class _CycleScreenState extends State<CycleScreen> {
  DateTime _displayedMonth = DateTime(2025, 11);
  int _selectedDay = 14;
  final DateTime _today = DateTime(2025, 11, 14);

  int get _monthDays =>
      DateTime(_displayedMonth.year, _displayedMonth.month + 1, 0).day;

  // Weekday of the 1st of the displayed month, 0 = Sunday .. 6 = Saturday
  int get _firstWeekday =>
      DateTime(_displayedMonth.year, _displayedMonth.month, 1).weekday % 7;

  void _goToPreviousMonth() {
    setState(() {
      _displayedMonth = DateTime(_displayedMonth.year, _displayedMonth.month - 1);
      _selectedDay = 1;
    });
  }

  void _goToNextMonth() {
    setState(() {
      _displayedMonth = DateTime(_displayedMonth.year, _displayedMonth.month + 1);
      _selectedDay = 1;
    });
  }

  // Day → phase
  static String _phase(int day, AppLocalizations l10n) {
    if (day <= 5) return l10n.cyclePhasePeriod;
    if (day <= 13) return l10n.cyclePhaseFollicular;
    if (day <= 16) return l10n.cyclePhaseOvulation;
    return l10n.cyclePhaseLuteal;
  }

  static Color _phaseColor(int day) {
    if (day <= 5) return RhythmaColors.rose;
    if (day <= 13) return RhythmaColors.primary;
    if (day <= 16) return RhythmaColors.teal;
    return RhythmaColors.coral;
  }

  @override
  Widget build(BuildContext context) {
    context.watch<ThemeProvider>();
    final l10n = AppLocalizations.of(context)!;
    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(20, 0, 20, 100),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          _ScreenHeader(
            title: l10n.cycleTrackerTitle,
            subtitle: DateFormat('MMMM yyyy').format(_displayedMonth),
          ),

          // Calendar card
          GlassCard(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                // Month nav
                Row(
                  children: [
                    _CircleBtn(icon: Icons.chevron_left_rounded, onTap: _goToPreviousMonth),
                    Expanded(
                      child: Center(
                        child: Text(
                          DateFormat('MMMM yyyy').format(_displayedMonth),
                          style: TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.w700,
                            color: RhythmaColors.foreground,
                          ),
                        ),
                      ),
                    ),
                    _CircleBtn(
                        icon: Icons.chevron_right_rounded, onTap: _goToNextMonth),
                  ],
                ),
                const SizedBox(height: 14),

                // Weekday headers
                Row(
                  children: ['S', 'M', 'T', 'W', 'T', 'F', 'S']
                      .map((d) => Expanded(
                            child: Center(
                              child: Text(
                                d,
                                style: TextStyle(
                                  fontSize: 11,
                                  fontWeight: FontWeight.w600,
                                  color: RhythmaColors.mutedFg,
                                ),
                              ),
                            ),
                          ))
                      .toList(),
                ),
                const SizedBox(height: 8),

                // Days grid
                Wrap(
                  children: [
                    // empty cells for first weekday
                    ...List.generate(
                      _firstWeekday,
                      (_) => const SizedBox(
                          width: double.infinity / 7,
                          height: 44),
                    ),
                    ...List.generate(_monthDays, (i) {
                      final day = i + 1;
                      final phase = _phase(day, l10n);
                      final phaseColor = _phaseColor(day);
                      final isSelected = _selectedDay == day;
                      final isToday = _today.year == _displayedMonth.year &&
                          _today.month == _displayedMonth.month &&
                          _today.day == day;

                      return GestureDetector(
                        onTap: () => setState(() => _selectedDay = day),
                        child: SizedBox(
                          width: MediaQuery.of(context).size.width / 7 - 3,
                          height: 46,
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              AnimatedContainer(
                                duration: const Duration(milliseconds: 180),
                                width: 34,
                                height: 34,
                                decoration: BoxDecoration(
                                  color: isSelected
                                      ? phaseColor
                                      : phaseColor.withOpacity(0.14),
                                  borderRadius: BorderRadius.circular(10),
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
                                    Container(
                                      width: 4,
                                      height: 4,
                                      decoration: BoxDecoration(
                                        shape: BoxShape.circle,
                                        color: isSelected
                                            ? Colors.white
                                            : phaseColor,
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
                ),

                const SizedBox(height: 14),
                Container(height: 1, color: RhythmaColors.border),
                const SizedBox(height: 12),

                // Legend
                Wrap(
                  spacing: 14,
                  runSpacing: 6,
                  children: [
                    _Legend(l10n.cyclePhasePeriod, RhythmaColors.rose),
                    _Legend(l10n.cyclePhaseFollicular, RhythmaColors.primary),
                    _Legend(l10n.cyclePhaseOvulation, RhythmaColors.teal),
                    _Legend(l10n.cyclePhaseLuteal, RhythmaColors.coral),
                  ],
                ),
              ],
            ),
          ),

          const SizedBox(height: 18),

          // Log section
          Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: Text(
              '${l10n.logFor} ${DateFormat('MMM').format(_displayedMonth)} $_selectedDay · ${_phase(_selectedDay, l10n)}',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w700,
                color: RhythmaColors.foreground,
              ),
            ),
          ),
          _LogRow(
            icon: Icons.water_drop_outlined,
            label: l10n.homeLogFlow,
            options: [l10n.logNone, l10n.logLight, l10n.logMedium, l10n.logHeavy],
            color: RhythmaColors.rose,
          ),
          const SizedBox(height: 10),
          _LogRow(
            icon: Icons.sentiment_satisfied_alt_rounded,
            label: l10n.homeLogMood,
            options: const ['😊', '😐', '😔', '😤', '🥰'],
            color: RhythmaColors.coral,
          ),
          const SizedBox(height: 10),
          _LogRow(
            icon: Icons.bolt_rounded,
            label: l10n.logLabelEnergy,
            options: [l10n.logEnergyLow, l10n.logEnergyMid, l10n.logEnergyHigh],
            color: RhythmaColors.primary,
          ),
          const SizedBox(height: 10),
          _LogRow(
            icon: Icons.bedtime_outlined,
            label: l10n.homeLogSleep,
            options: [l10n.logSleep1, l10n.logSleep2, l10n.logSleep3, l10n.logSleep4],
            color: RhythmaColors.primary,
          ),
          const SizedBox(height: 10),
          _LogRow(
            icon: Icons.psychology_outlined,
            label: l10n.logLabelSymptoms,
            options: [l10n.logSympCramps, l10n.logSympHeadache, l10n.logSympBloating, l10n.logSympAcne],
            color: RhythmaColors.teal,
          ),
        ],
      ),
    );
  }
}

class _LogRow extends StatefulWidget {
  final IconData icon;
  final String label;
  final List<String> options;
  final Color color;

  const _LogRow({
    required this.icon,
    required this.label,
    required this.options,
    required this.color,
  });

  @override
  State<_LogRow> createState() => _LogRowState();
}

class _LogRowState extends State<_LogRow> {
  String? _selected;

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 34,
                height: 34,
                decoration: BoxDecoration(
                  color: widget.color.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(widget.icon, color: widget.color, size: 17),
              ),
              const SizedBox(width: 10),
              Text(
                widget.label,
                style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w600,
                  color: RhythmaColors.foreground,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: widget.options.map((opt) {
              final sel = _selected == opt;
              return GestureDetector(
                onTap: () => setState(
                    () => _selected = sel ? null : opt),
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 160),
                  padding: const EdgeInsets.symmetric(
                      horizontal: 14, vertical: 7),
                  decoration: BoxDecoration(
                    color: sel
                        ? widget.color
                        : RhythmaColors.surfaceMuted,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    opt,
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                      color: sel
                          ? Colors.white
                          : RhythmaColors.foreground,
                    ),
                  ),
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }
}

class _Legend extends StatelessWidget {
  final String label;
  final Color color;
  const _Legend(this.label, this.color);

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
            width: 8,
            height: 8,
            decoration:
                BoxDecoration(color: color, shape: BoxShape.circle)),
        const SizedBox(width: 5),
        Text(label,
            style: TextStyle(
                fontSize: 12,
                color: RhythmaColors.mutedFg,
                fontWeight: FontWeight.w500)),
      ],
    );
  }
}

class _CircleBtn extends StatelessWidget {
  final IconData icon;
  final VoidCallback onTap;
  const _CircleBtn({required this.icon, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 34,
        height: 34,
        decoration: BoxDecoration(
          color: RhythmaColors.surfaceMuted,
          borderRadius: BorderRadius.circular(17),
        ),
        child: Icon(icon, size: 18, color: RhythmaColors.foreground),
      ),
    );
  }
}

class _ScreenHeader extends StatelessWidget {
  final String title;
  final String? subtitle;
  const _ScreenHeader({required this.title, this.subtitle});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(2, 8, 2, 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title,
              style: TextStyle(
                fontSize: 26,
                fontWeight: FontWeight.w700,
                color: RhythmaColors.foreground,
              )),
          if (subtitle != null) ...[
            const SizedBox(height: 2),
            Text(subtitle!,
                style: TextStyle(
                    fontSize: 13, color: RhythmaColors.mutedFg)),
          ],
        ],
      ),
    );
  }
}