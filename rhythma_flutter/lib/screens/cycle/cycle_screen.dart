import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import 'package:rhythma/l10n/app_localizations.dart';
import '../../config/theme.dart';
import '../../components/shared.dart';
import '../../providers/theme_provider.dart';
import '../../providers/cycle_provider.dart';
import 'components/calendar_grid.dart';

class CycleScreen extends StatefulWidget {
  const CycleScreen({super.key});

  @override
  State<CycleScreen> createState() => _CycleScreenState();
}

class _CycleScreenState extends State<CycleScreen> {
  static const int _initialPageOffset = 12000;
  late final PageController _pageController;

  @override
  void initState() {
    super.initState();
    _pageController = PageController(initialPage: _initialPageOffset);
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  void _goToPreviousMonth() {
    _pageController.previousPage(
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeInOut,
    );
  }

  void _goToNextMonth() {
    _pageController.nextPage(
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeInOut,
    );
  }

  void _jumpToToday() {
    context.read<CycleProvider>().jumpToToday();
    _pageController.animateToPage(
      _initialPageOffset,
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeInOut,
    );
  }

  @override
  Widget build(BuildContext context) {
    context.watch<ThemeProvider>();
    final cycleProvider = context.watch<CycleProvider>();
    final l10n = AppLocalizations.of(context)!;

    final displayedMonth = cycleProvider.displayedMonth;
    final selectedDate = cycleProvider.selectedDate;

    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(20, 0, 20, 100),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: _ScreenHeader(
                  title: l10n.cycleTrackerTitle,
                  subtitle: DateFormat('MMMM yyyy').format(displayedMonth),
                ),
              ),
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: TextButton.icon(
                  onPressed: _jumpToToday,
                  icon: const Icon(Icons.today_rounded, size: 16),
                  label: const Text('Today'),
                  style: TextButton.styleFrom(
                    foregroundColor: RhythmaColors.primary,
                  ),
                ),
              ),
            ],
          ),

          // Calendar card
          GlassCard(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                // Month nav
                Row(
                  children: [
                    _CircleBtn(
                        icon: Icons.chevron_left_rounded,
                        onTap: _goToPreviousMonth),
                    Expanded(
                      child: Center(
                        child: Text(
                          DateFormat('MMMM yyyy').format(displayedMonth),
                          style: TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.w700,
                            color: RhythmaColors.foreground,
                          ),
                        ),
                      ),
                    ),
                    _CircleBtn(
                        icon: Icons.chevron_right_rounded,
                        onTap: _goToNextMonth),
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

                // Days grid using the new CalendarGrid
                CalendarGrid(
                  pageController: _pageController,
                  initialPageOffset: _initialPageOffset,
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
              '${l10n.logFor} ${DateFormat('MMM').format(selectedDate)} ${selectedDate.day} · ${cycleProvider.phase(selectedDate, l10n)}',
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
            options: [
              l10n.logNone,
              l10n.logLight,
              l10n.logMedium,
              l10n.logHeavy
            ],
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
            options: [
              l10n.logSleep1,
              l10n.logSleep2,
              l10n.logSleep3,
              l10n.logSleep4
            ],
            color: RhythmaColors.primary,
          ),
          const SizedBox(height: 10),
          _LogRow(
            icon: Icons.psychology_outlined,
            label: l10n.logLabelSymptoms,
            options: [
              l10n.logSympCramps,
              l10n.logSympHeadache,
              l10n.logSympBloating,
              l10n.logSympAcne
            ],
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
                onTap: () {
                  setState(() => _selectedSelected(opt, sel));
                  // We simulate updating the logs when a symptom is toggled
                  context.read<CycleProvider>().toggleLogForDate(
                      context.read<CycleProvider>().selectedDate);
                },
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 160),
                  padding:
                      const EdgeInsets.symmetric(horizontal: 14, vertical: 7),
                  decoration: BoxDecoration(
                    color: sel ? widget.color : RhythmaColors.surfaceMuted,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    opt,
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                      color: sel ? Colors.white : RhythmaColors.foreground,
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

  void _selectedSelected(String opt, bool sel) {
    _selected = sel ? null : opt;
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
            decoration: BoxDecoration(color: color, shape: BoxShape.circle)),
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
                style: TextStyle(fontSize: 13, color: RhythmaColors.mutedFg)),
          ],
        ],
      ),
    );
  }
}
