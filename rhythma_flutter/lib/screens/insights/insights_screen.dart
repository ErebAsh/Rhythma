import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:rhythma/l10n/app_localizations.dart';
import '../../config/theme.dart';
import '../../components/shared.dart';
import '../../components/charts.dart';
import '../../providers/theme_provider.dart';

class InsightsScreen extends StatelessWidget {
  const InsightsScreen({super.key});

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
          Padding(
            padding: const EdgeInsets.fromLTRB(2, 8, 2, 20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  l10n.insightsTitle,
                  style: TextStyle(
                    fontSize: 26,
                    fontWeight: FontWeight.w700,
                    color: RhythmaColors.foreground,
                  ),
                ),
                const SizedBox(height: 2),
                Text(l10n.insightsSubtitle,
                    style:
                        TextStyle(fontSize: 13, color: RhythmaColors.mutedFg)),
              ],
            ),
          ),

          // MHS hero card
          GlassCard(
            child: Stack(
              children: [
                Positioned(
                  right: -30,
                  top: -30,
                  child: Opacity(
                    opacity: 0.2,
                    child: Container(
                      width: 160,
                      height: 160,
                      decoration: BoxDecoration(
                        gradient: RhythmaGradients.primary,
                        shape: BoxShape.circle,
                  ),
                ),
              ),
                ),
                Row(
                  children: [
                    const ScoreRing(value: 82, size: 96),
                    const SizedBox(width: 18),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            l10n.insightsMhsLabel,
                            style: TextStyle(
                              fontSize: 10,
                              fontWeight: FontWeight.w700,
                              color: RhythmaColors.primary,
                              letterSpacing: 0.8,
                            ),
                          ),
                          const SizedBox(height: 5),
                          Text(
                            '82 / 100',
                            style: TextStyle(
                              fontSize: 28,
                              fontWeight: FontWeight.w700,
                              color: RhythmaColors.foreground,
                            ),
                          ),
                          const SizedBox(height: 5),
                          Row(
                            children: [
                              const Icon(Icons.trending_up_rounded,
                                  size: 14, color: RhythmaColors.teal),
                              const SizedBox(width: 5),
                              Text(
                                l10n.insightsMhsDelta,
                                style: TextStyle(
                                  fontSize: 12,
                                  color: RhythmaColors.mutedFg,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          const SizedBox(height: 14),

          // Mini stat grid
          Row(
            children: [
              Expanded(
                child: _MiniCard(
                  label: l10n.insightsVar,
                  value: '3.2 ${l10n.homeDaysLabel}',
                  delta: l10n.logEnergyLow,
                  trendUp: false,
                  color: RhythmaColors.teal,
                  icon: Icons.graphic_eq_rounded,
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: _MiniCard(
                  label: l10n.insightsAvgCycle,
                  value: '29 ${l10n.homeDaysLabel}',
                  delta: l10n.insightsRegular,
                  trendUp: true,
                  color: RhythmaColors.primary,
                  icon: Icons.favorite_rounded,
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Row(
            children: [
              Expanded(
                child: _MiniCard(
                  label: l10n.homeLogSleep,
                  value: '7.2h',
                  delta: '+12%',
                  trendUp: true,
                  color: RhythmaColors.primary,
                  icon: Icons.bedtime_rounded,
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: _MiniCard(
                  label: l10n.homeLogStress,
                  value: l10n.insightsModerate,
                  delta: '-8%',
                  trendUp: false,
                  color: RhythmaColors.coral,
                  icon: Icons.self_improvement_rounded,
                ),
              ),
            ],
          ),

          const SizedBox(height: 14),

          // Trend chart
          GlassCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            l10n.insightsTrendLabel,
                            style: TextStyle(
                              fontSize: 10,
                              fontWeight: FontWeight.w700,
                              color: RhythmaColors.mutedFg,
                              letterSpacing: 0.8,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            l10n.insightsStabilizing,
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w700,
                              color: RhythmaColors.foreground,
                            ),
                          ),
                        ],
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 10, vertical: 5),
                      decoration: BoxDecoration(
                        color: RhythmaColors.teal.withOpacity(0.14),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        l10n.insightsHealthy,
                        style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: RhythmaColors.teal,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 14),
                Semantics(
                  label:
                      'Trend chart showing health metrics from July to November with relatively stable values.',
                  child: TrendChart(
                    points: const [30, 32, 29, 31, 28, 29, 30, 29, 28, 29],
                    color: RhythmaColors.primary,
                    height: 80,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Your health trends remained relatively stable over the last five months.',
                   style: TextStyle(
                     fontSize: 12,
                     color: RhythmaColors.mutedFg,
                  ),
                ),
                const SizedBox(height: 8),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: ['Jul', 'Aug', 'Sep', 'Oct', 'Nov']
                      .map((m) => Text(
                            m,
                            style: TextStyle(
                              fontSize: 10,
                              color: RhythmaColors.mutedFg,
                            ),
                          ))
                      .toList(),
                ),
              ],
            ),
          ),
        

          const SizedBox(height: 14),

          // Symptom patterns
          GlassCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  l10n.insightsSymptomsLabel,
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                    color: RhythmaColors.foreground,
                  ),
                ),
              
                const SizedBox(height: 14),
                _SymptomBar(l10n.logSympCramps, 0.70, RhythmaColors.rose),
                const SizedBox(height: 12),
                _SymptomBar(l10n.logSympHeadache, 0.35, RhythmaColors.coral),
                const SizedBox(height: 12),
                _SymptomBar(l10n.logSympBloating, 0.55, RhythmaColors.primary),
                const SizedBox(height: 12),
                _SymptomBar(l10n.insightsMoodSwings, 0.45, RhythmaColors.teal),
              ],
            ),
          ),

          const SizedBox(height: 14),

          // Wellness recommendations
          SectionHeader(title: l10n.insightsWellnessLabel),
          ...[
            _Rec(l10n.insightsRec1, RhythmaColors.rose),
            _Rec(l10n.insightsRec2, RhythmaColors.primary),
            _Rec(l10n.insightsRec3, RhythmaColors.teal),
          ].map((r) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: r,
              )),
        ],
      ),
    );
  }
}

class _MiniCard extends StatelessWidget {
  final String label;
  final String value;
  final String delta;
  final bool trendUp;
  final Color color;
  final IconData icon;

  const _MiniCard({
    required this.label,
    required this.value,
    required this.delta,
    required this.trendUp,
    required this.color,
    required this.icon,
  });

 @override
Widget build(BuildContext context) {
  return Semantics(
    label: '$label, value $value, change $delta',
    child: GlassCard(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Container(
                width: 34,
                height: 34,
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.14),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: ExcludeSemantics(
                  child: Icon(icon, color: color, size: 17),
                ),
              ),
              ExcludeSemantics(
                child: Icon(
                  trendUp
                      ? Icons.trending_up_rounded
                      : Icons.trending_down_rounded,
                  size: 16,
                  color: color,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            label,
            style: TextStyle(
              fontSize: 11,
              color: RhythmaColors.mutedFg,
            ),
          ),
          const SizedBox(height: 3),
          Text(
            value,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w700,
              color: RhythmaColors.foreground,
              height: 1,
            ),
          ),
          const SizedBox(height: 3),
          Text(
            delta,
            style: TextStyle(
              fontSize: 10,
              color: color,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    ),
  );
}
}

class _SymptomBar extends StatelessWidget {
  final String label;
  final double fraction;
  final Color color;

  const _SymptomBar(this.label, this.fraction, this.color);

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label,
                style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: RhythmaColors.foreground)),
            Text('${(fraction * 100).round()}%',
                style: TextStyle(fontSize: 12, color: RhythmaColors.mutedFg)),
          ],
        ),
        const SizedBox(height: 6),
        Semantics(
          label: '$label ${(fraction * 100).round()} percent',
          child:ClipRRect(
                  borderRadius: BorderRadius.circular(4),
                  child: LinearProgressIndicator(
                  value: fraction,
                  minHeight: 8,
                  backgroundColor: RhythmaColors.surfaceMuted,
                  valueColor: AlwaysStoppedAnimation(color),
             ),
          ),
        ),
      ],
    );
  }
}

class _Rec extends StatelessWidget {
  final String text;
  final Color color;

  const _Rec(this.text, this.color);

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      padding: const EdgeInsets.all(14),
      child: Row(
        children: [
         Container(
           width: 36,
           height: 36,
           decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
         ),
        child: const ExcludeSemantics(
         child: Icon(
           Icons.favorite_rounded,
           color: Colors.white,
           size: 16,
       ),
     ),
  ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              text,
              style: TextStyle(
                fontSize: 13,
                color: RhythmaColors.foreground,
                height: 1.4,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

extension on Widget {
}