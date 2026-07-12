import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:rhythma/l10n/app_localizations.dart';
import '../../config/theme.dart';
import '../../config/constants.dart';
import '../../providers/dashboard_provider.dart';
import 'components/home_components.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final dashboard = context.watch<DashboardProvider>();
    final l10n = AppLocalizations.of(context)!;

    if (dashboard.loading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (dashboard.error.isNotEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 48, color: RhythmaColors.rose),
            const SizedBox(height: RhythmaDimens.gapLarge),
            Text(
              l10n.homeFailedLoad,
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: RhythmaDimens.gapSmall),
            Text(
              dashboard.errorKeyToMessage(l10n, dashboard.error),
              style: TextStyle(color: RhythmaColors.mutedFg),
            ),
            const SizedBox(height: RhythmaDimens.gapLarge),
            ElevatedButton(
              onPressed: dashboard.fetchDashboardData,
              child: Text(l10n.homeRetry),
            ),
          ],
        ),
      );
    }

    final userName = dashboard.userData['name'] ?? 'User';
    final nextPeriodDays = dashboard.cycleData['nextPeriodDays'] ?? 14;
    final cycleDay = dashboard.cycleData['day'] ?? 14;
    final totalCycle = dashboard.cycleData['total'] ?? 28;
    final mhs = dashboard.insights['mhs'] ?? 82;
    final cvi = dashboard.insights['cvi'] ?? 'Low';
    final sleepHours = dashboard.insights['sleepHours'] ?? '7.2h';

    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(
        RhythmaDimens.pageHorizontal, 
        0, 
        RhythmaDimens.pageHorizontal, 
        RhythmaDimens.pageBottomOverflow
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          HomeHeaderWidget(userName: userName),
          HomeCycleCardWidget(
            nextPeriodDays: nextPeriodDays,
            cycleDay: cycleDay,
            totalCycle: totalCycle,
            mhs: mhs,
            cvi: cvi,
            sleepHours: sleepHours,
          ),
          const SizedBox(height: RhythmaDimens.gapDefault),
          const HomeAssistantCardWidget(),
          const SizedBox(height: RhythmaDimens.gapDefault),
          HomeLogGridWidget(onLogSaved: dashboard.fetchDashboardData),
          const SizedBox(height: RhythmaDimens.gapDefault),
          const HomeInsightCardWidget(),
          const SizedBox(height: RhythmaDimens.gapDefault),
          const HomeLearnSectionWidget(),
        ],
      ),
    );
  }
}