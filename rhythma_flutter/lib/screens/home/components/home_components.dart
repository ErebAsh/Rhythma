import 'package:flutter/material.dart';
import 'package:rhythma/l10n/app_localizations.dart';
import '../../../config/theme.dart';
import '../../../config/constants.dart';
import '../../../components/shared.dart';
import '../../../components/charts.dart';
import '../../settings/language_screen.dart';
import '../../insights/insights_screen.dart';
import '../../../services/local_storage_service.dart';
import '../../cycle/components/log_entry_sheet.dart';

extension on Widget {
  Widget opacity(double value) => Opacity(opacity: value, child: this);
}

// ── Helpers ──────────────────────────────────────────────────────────────────

/// Displays a generic "Coming Soon" dialog for features in development.
void showComingSoonDialog(BuildContext context, String topic) {
  final l10n = AppLocalizations.of(context)!;
  showDialog(
    context: context,
    builder: (ctx) => AlertDialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(RhythmaDimens.radiusLarge)),
      title: Text(l10n.homeComingSoon,
          textAlign: TextAlign.center,
          style: TextStyle(color: RhythmaColors.primary)),
      content: Text(
        l10n.homeUnderDevelopment(topic),
        textAlign: TextAlign.center,
      ),
      actionsAlignment: MainAxisAlignment.center,
      actions: [
        ElevatedButton(
          style: ElevatedButton.styleFrom(
            backgroundColor: RhythmaColors.primary,
            foregroundColor: RhythmaColors.primaryFg,
          ),
          onPressed: () => Navigator.pop(ctx),
          child: Text(l10n.homeOk),
        ),
      ],
    ),
  );
}

// ── Header ───────────────────────────────────────────────────────────────────

/// The top section of the home screen, displaying a personalized greeting
/// and quick-action icons (Language, Privacy).
class HomeHeaderWidget extends StatelessWidget {
  final String userName;
  const HomeHeaderWidget({super.key, required this.userName});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Padding(
      padding: const EdgeInsets.fromLTRB(2, RhythmaDimens.gapSmall, 2, RhythmaDimens.gapLarge),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '${l10n.homeGreeting}, $userName',
                  style: TextStyle(
                    fontSize: 26,
                    fontWeight: FontWeight.w700,
                    color: RhythmaColors.foreground,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  l10n.homePhaseDesc,
                  style: TextStyle(
                    fontSize: 13,
                    color: RhythmaColors.mutedFg,
                  ),
                ),
              ],
            ),
          ),
          HeaderIcon(
            icon: Icons.language_rounded,
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const LanguageScreen()),
              );
            },
          ),
          const SizedBox(width: RhythmaDimens.gapSmall),
          HeaderIcon(
            icon: Icons.shield_outlined,
            onTap: () => showComingSoonDialog(context, l10n.homePrivacySecurity),
          ),
        ],
      ),
    );
  }
}

class HeaderIcon extends StatelessWidget {
  final IconData icon;
  final VoidCallback? onTap;
  const HeaderIcon({super.key, required this.icon, this.onTap});

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      padding: EdgeInsets.zero,
      borderRadius: RhythmaDimens.radiusLarge,
      onTap: onTap,
      child: SizedBox(
        width: RhythmaDimens.headerIconSize,
        height: RhythmaDimens.headerIconSize,
        child: Icon(icon, size: RhythmaDimens.iconLarge, color: RhythmaColors.foreground),
      ),
    );
  }
}

// ── Cycle Card ───────────────────────────────────────────────────────────────

/// A large glass-morphism card displaying the user's current cycle ring,
/// predictions for the next period, and key health metrics (MHS, CVI, Sleep).
class HomeCycleCardWidget extends StatelessWidget {
  final int nextPeriodDays;
  final int cycleDay;
  final int totalCycle;
  final dynamic mhs;
  final dynamic cvi;
  final dynamic sleepHours;

  const HomeCycleCardWidget({
    super.key,
    required this.nextPeriodDays,
    required this.cycleDay,
    required this.totalCycle,
    required this.mhs,
    required this.cvi,
    required this.sleepHours,
  });

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return GlassCard(
      child: Stack(
        children: [
          Positioned(
            right: -RhythmaDimens.radiusLarge,
            top: -RhythmaDimens.radiusLarge,
            child: Container(
              width: 140,
              height: 140,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RhythmaGradients.primary,
              ),
            ).opacity(0.22),
          ),
          Column(
            children: [
              Row(
                children: [
                  CycleRing(day: cycleDay, total: totalCycle, size: RhythmaDimens.cycleRingSize),
                  const SizedBox(width: RhythmaDimens.iconLarge),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          l10n.homeNextPeriod,
                          style: TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.w600,
                            color: RhythmaColors.mutedFg,
                            letterSpacing: 1,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Row(
                          crossAxisAlignment: CrossAxisAlignment.baseline,
                          textBaseline: TextBaseline.alphabetic,
                          children: [
                            Text(
                              '$nextPeriodDays',
                              style: TextStyle(
                                fontSize: 36,
                                fontWeight: FontWeight.w700,
                                color: RhythmaColors.foreground,
                                height: 1,
                              ),
                            ),
                            const SizedBox(width: 4),
                            Text(
                              l10n.homeDaysLabel,
                              style: TextStyle(
                                fontSize: 15,
                                color: RhythmaColors.mutedFg,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 6),
                        RichText(
                          text: TextSpan(
                            style: TextStyle(
                              fontSize: 13,
                              color: RhythmaColors.foreground,
                            ),
                            children: [
                              TextSpan(text: l10n.homeFertileWindow),
                              TextSpan(
                                text: l10n.homeHighEnergy,
                                style: const TextStyle(
                                  color: RhythmaColors.rose,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: RhythmaDimens.gapLarge),
              Container(
                height: 1,
                color: RhythmaColors.border,
              ),
              const SizedBox(height: RhythmaDimens.gapLarge),
              Row(
                children: [
                  StatCell(label: l10n.homeMhs, value: '$mhs', color: RhythmaColors.primary),
                  StatDivider(),
                  StatCell(label: l10n.homeCvi, value: '$cvi', color: RhythmaColors.teal),
                  StatDivider(),
                  StatCell(label: l10n.homeSleep, value: '$sleepHours', color: RhythmaColors.coral),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class StatCell extends StatelessWidget {
  final String label;
  final String value;
  final Color color;

  const StatCell({
    super.key,
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Column(
        children: [
          Text(label,
              style: TextStyle(
                  fontSize: 11,
                  color: RhythmaColors.mutedFg,
                  fontWeight: FontWeight.w500)),
          const SizedBox(height: 3),
          Text(value,
              style: TextStyle(
                  fontSize: 15, fontWeight: FontWeight.w700, color: color)),
        ],
      ),
    );
  }
}

class StatDivider extends StatelessWidget {
  const StatDivider({super.key});
  @override
  Widget build(BuildContext context) => Container(
        width: 1,
        height: 28,
        color: RhythmaColors.border,
      );
}

// ── Assistant Card ───────────────────────────────────────────────────────────

/// A call-to-action card encouraging the user to interact with the AI assistant.
class HomeAssistantCardWidget extends StatelessWidget {
  const HomeAssistantCardWidget({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return GradientBox(
      padding: const EdgeInsets.all(RhythmaDimens.iconLarge),
      child: Stack(
        children: [
          Positioned(
            right: -8,
            top: -8,
            child: Icon(
              Icons.auto_awesome_rounded,
              size: 80,
              color: Colors.white.withOpacity(0.15),
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(Icons.auto_awesome_rounded, size: RhythmaDimens.iconSmall, color: Colors.white),
                  const SizedBox(width: 6),
                  Text(
                    l10n.homeAiTitle,
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w700,
                      color: Colors.white.withOpacity(0.9),
                      letterSpacing: 1,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: RhythmaDimens.gapSmall),
              Text(
                l10n.homeAiSubtitle,
                style: const TextStyle(
                  fontSize: 17,
                  fontWeight: FontWeight.w700,
                  color: Colors.white,
                  height: 1.3,
                ),
              ),
              const SizedBox(height: RhythmaDimens.gapDefault),
              Row(
                children: [
                  Expanded(
                    child: GestureDetector(
                      onTap: () {
                        Navigator.pushNamed(context, '/assistant');
                      },
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(RhythmaDimens.radiusLarge),
                        ),
                        child: Row(
                          children: [
                            Icon(Icons.chat_bubble_outline_rounded,
                                size: 15, color: Colors.white.withOpacity(0.9)),
                            const SizedBox(width: RhythmaDimens.gapSmall),
                            Text(
                              l10n.homeAiPrompt,
                              style: TextStyle(
                                fontSize: 13,
                                color: Colors.white.withOpacity(0.9),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: RhythmaDimens.gapSmall),
                  Container(
                    width: 40,
                    height: 40,
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.25),
                      borderRadius: BorderRadius.circular(RhythmaDimens.radiusLarge),
                    ),
                    child: const Icon(Icons.mic_rounded, size: RhythmaDimens.iconLarge, color: Colors.white),
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }
}

// ── Log Grid ─────────────────────────────────────────────────────────────────

/// A grid of quick-log buttons allowing the user to record daily flow, mood,
/// sleep, and stress directly from the home screen.
class HomeLogGridWidget extends StatelessWidget {
  final VoidCallback onLogSaved;
  const HomeLogGridWidget({super.key, required this.onLogSaved});

  void _showQuickLogSheet(BuildContext context, {
    required String field,
    required String label,
    required IconData icon,
    required Color color,
    required List<String> options,
  }) {
    final l10n = AppLocalizations.of(context)!;
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (ctx) => Padding(
        padding: EdgeInsets.only(bottom: MediaQuery.of(ctx).viewInsets.bottom),
        child: Container(
          decoration: BoxDecoration(
            color: RhythmaColors.surface,
            borderRadius: const BorderRadius.vertical(top: Radius.circular(RhythmaDimens.radiusSheet)),
          ),
          padding: const EdgeInsets.all(RhythmaDimens.gapXl),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    width: RhythmaDimens.tintedIconSize,
                    height: RhythmaDimens.tintedIconSize,
                    decoration: BoxDecoration(
                      color: color.withOpacity(0.15),
                      borderRadius: BorderRadius.circular(RhythmaDimens.tintedIconRadius),
                    ),
                    child: Icon(icon, color: color, size: RhythmaDimens.iconMedium),
                  ),
                  const SizedBox(width: RhythmaDimens.gapMedium),
                  Text(
                    l10n.homeQuickLogTitle(label),
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                      color: RhythmaColors.foreground,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: RhythmaDimens.gapLarge),
              Wrap(
                spacing: RhythmaDimens.gapSmall,
                runSpacing: RhythmaDimens.gapSmall,
                children: options.map((opt) {
                  return GestureDetector(
                    onTap: () async {
                      await LocalStorageService.saveQuickLogField(
                          DateTime.now(), field, opt);
                      if (ctx.mounted) Navigator.pop(ctx);
                      onLogSaved();
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text(l10n.homeQuickLogSaved(label, opt))),
                      );
                    },
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 14, vertical: 9),
                      decoration: BoxDecoration(
                        color: RhythmaColors.surfaceMuted,
                        borderRadius: BorderRadius.circular(RhythmaDimens.radiusLarge),
                        border: Border.all(color: RhythmaColors.border),
                      ),
                      child: Text(
                        opt,
                        style: TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w600,
                            color: RhythmaColors.foreground),
                      ),
                    ),
                  );
                }).toList(),
              ),
              const SizedBox(height: RhythmaDimens.gapSmall),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Column(
      children: [
        SectionHeader(
          title: l10n.homeFeelingTitle,
          action: l10n.homeLogAll,
          onAction: () {
            final currentDate = DateTime.now();
            final existingLog = LocalStorageService.getCycleLogForDate(currentDate);

            LogEntrySheet.show(
              context,
              currentDate,
              existingLog: existingLog,
            ).then((_) {
              onLogSaved();
            });
          },
        ),
        Row(
          children: [
            LogButton(
              icon: Icons.water_drop_outlined,
              label: l10n.homeLogFlow,
              color: RhythmaColors.rose,
              onTap: () => _showQuickLogSheet(
                context,
                field: 'flow_intensity',
                label: l10n.homeLogFlow,
                icon: Icons.water_drop_outlined,
                color: RhythmaColors.rose,
                options: [
                  l10n.logNone,
                  l10n.logLight,
                  l10n.logMedium,
                  l10n.logHeavy
                ],
              ),
            ),
            const SizedBox(width: RhythmaDimens.gapMedium),
            LogButton(
              icon: Icons.favorite_border_rounded,
              label: l10n.homeLogMood,
              color: RhythmaColors.coral,
              onTap: () => _showQuickLogSheet(
                context,
                field: 'mood',
                label: l10n.homeLogMood,
                icon: Icons.favorite_border_rounded,
                color: RhythmaColors.coral,
                options: const ['😊', '😐', '😔', '😤', '🥰'],
              ),
            ),
            const SizedBox(width: RhythmaDimens.gapMedium),
            LogButton(
              icon: Icons.bedtime_outlined,
              label: l10n.homeLogSleep,
              color: RhythmaColors.primary,
              onTap: () => _showQuickLogSheet(
                context,
                field: 'sleep_hours',
                label: l10n.homeLogSleep,
                icon: Icons.bedtime_outlined,
                color: RhythmaColors.primary,
                options: [
                  l10n.logSleep1,
                  l10n.logSleep2,
                  l10n.logSleep3,
                  l10n.logSleep4
                ],
              ),
            ),
            const SizedBox(width: RhythmaDimens.gapMedium),
            LogButton(
              icon: Icons.air_rounded,
              label: l10n.homeLogStress,
              color: RhythmaColors.teal,
              onTap: () => _showQuickLogSheet(
                context,
                field: 'stress_level',
                label: l10n.homeLogStress,
                icon: Icons.air_rounded,
                color: RhythmaColors.teal,
                options: [
                  l10n.logEnergyLow,
                  l10n.logEnergyMid,
                  l10n.logEnergyHigh
                ],
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class LogButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback? onTap;

  const LogButton(
      {super.key, required this.icon,
      required this.label,
      required this.color,
      this.onTap});

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: GlassCard(
        padding: const EdgeInsets.symmetric(vertical: 14),
        onTap: onTap,
        child: Column(
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: color.withOpacity(0.15),
                borderRadius: BorderRadius.circular(14),
              ),
              child: Icon(icon, color: color, size: RhythmaDimens.iconXl),
            ),
            const SizedBox(height: 6),
            Text(label,
                style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                    color: RhythmaColors.foreground)),
          ],
        ),
      ),
    );
  }
}

// ── Insight Card ─────────────────────────────────────────────────────────────

class HomeInsightCardWidget extends StatelessWidget {
  const HomeInsightCardWidget({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
              builder: (_) =>
                  const ShellBackground(child: InsightsScreen())),
        );
      },
      child: GlassCard(
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    l10n.homeWeeklyInsightLabel,
                    style: const TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w700,
                      color: RhythmaColors.teal,
                      letterSpacing: 1,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    l10n.homeWeeklyInsightTitle,
                    style: TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.w600,
                      color: RhythmaColors.foreground,
                      height: 1.35,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    l10n.homeWeeklyInsightDesc,
                    style: TextStyle(
                      fontSize: 13,
                      color: RhythmaColors.mutedFg,
                      height: 1.4,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: RhythmaDimens.gapSmall),
            Icon(Icons.chevron_right_rounded,
                color: RhythmaColors.mutedFg),
          ],
        ),
      ),
    );
  }
}

// ── Learn Section ────────────────────────────────────────────────────────────

class HomeLearnSectionWidget extends StatelessWidget {
  const HomeLearnSectionWidget({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Column(
      children: [
        SectionHeader(title: l10n.homeLearnTitle),
        SizedBox(
          height: RhythmaDimens.learnCardHeight,
          child: ListView(
            scrollDirection: Axis.horizontal,
            children: [
              LearnCard(
                title: l10n.homeLearnPcos,
                color: RhythmaColors.rose,
                label: l10n.homeArticle,
                onTap: () =>
                    showComingSoonDialog(context, l10n.homeLearnPcos),
              ),
              const SizedBox(width: RhythmaDimens.gapMedium),
              LearnCard(
                title: l10n.homeLearnHormones,
                color: RhythmaColors.primary,
                label: l10n.homeArticle,
                onTap: () =>
                    showComingSoonDialog(context, l10n.homeLearnHormones),
              ),
              const SizedBox(width: RhythmaDimens.gapMedium),
              LearnCard(
                title: l10n.homeLearnIron,
                color: RhythmaColors.coral,
                label: l10n.homeArticle,
                onTap: () =>
                    showComingSoonDialog(context, l10n.homeLearnIron),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class LearnCard extends StatelessWidget {
  final String title;
  final Color color;
  final String label;
  final VoidCallback? onTap;

  const LearnCard(
      {super.key, required this.title,
      required this.color,
      required this.label,
      this.onTap});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: RhythmaDimens.learnCardWidth,
        decoration: BoxDecoration(
          gradient: isDark
              ? null
              : LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    color,
                    Color.lerp(color, RhythmaColors.primary, 0.5)!
                  ],
                ),
          color: isDark ? color.withOpacity(0.15) : null,
          border: isDark ? Border.all(color: color.withOpacity(0.3)) : null,
          borderRadius: BorderRadius.circular(RhythmaDimens.radiusLarge),
        ),
        padding: const EdgeInsets.all(RhythmaDimens.gapLarge),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.end,
          children: [
            Text(
              label,
              style: TextStyle(
                  fontSize: 9,
                  fontWeight: FontWeight.w700,
                  color: Colors.white.withOpacity(0.75),
                  letterSpacing: 1),
            ),
            const SizedBox(height: 4),
            Text(
              title,
              style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w700,
                color: Colors.white,
                height: 1.25,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
