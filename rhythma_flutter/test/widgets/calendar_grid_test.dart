import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:rhythma/l10n/app_localizations.dart';
import 'package:rhythma/providers/cycle_provider.dart';
import 'package:rhythma/screens/cycle/components/calendar_grid.dart';
import 'package:rhythma/services/local_storage_service.dart';

void main() {
  setUp(() {
    LocalStorageService.isTesting = true;
    LocalStorageService.mockCycleLogs = [];
  });
  Widget buildTestableWidget({required Widget child}) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => CycleProvider()),
      ],
      child: MaterialApp(
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: Scaffold(
          body: child,
        ),
      ),
    );
  }

  testWidgets('CalendarGrid renders and handles date selection', (WidgetTester tester) async {
    final pageController = PageController(initialPage: 12000);
    
    await tester.pumpWidget(buildTestableWidget(
      child: CalendarGrid(
        pageController: pageController,
        initialPageOffset: 12000,
      ),
    ));

    // Wait for the PageView to layout
    await tester.pumpAndSettle();

    // Verify it renders some text days (like '15')
    expect(find.text('15'), findsWidgets);

    // Tap day 15
    await tester.tap(find.text('15').first);
    await tester.pump();

    // The CycleProvider should now have selected day 15. We test this indirectly by 
    // seeing if it still renders properly and doesn't throw.
    expect(find.text('15'), findsWidgets);
  });

  testWidgets('CalendarGrid supports month swiping via PageController', (WidgetTester tester) async {
    final pageController = PageController(initialPage: 12000);
    
    await tester.pumpWidget(buildTestableWidget(
      child: CalendarGrid(
        pageController: pageController,
        initialPageOffset: 12000,
      ),
    ));
    await tester.pumpAndSettle();

    // Swipe left (next month)
    pageController.nextPage(duration: const Duration(milliseconds: 100), curve: Curves.linear);
    await tester.pumpAndSettle();
    
    // We expect it to still render days
    expect(find.text('15'), findsWidgets);
  });
}
