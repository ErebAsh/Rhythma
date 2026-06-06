import 'dart:ui';
import 'package:flutter/material.dart';
import '../config/theme.dart';

/// Glassmorphism card — mirrors the web .glass-card utility
class GlassCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry padding;
  final double? borderRadius;
  final VoidCallback? onTap;

  const GlassCard({
    Key? key,
    required this.child,
    this.padding = const EdgeInsets.all(20),
    this.borderRadius,
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final r = borderRadius ?? 20.0;
    final card = ClipRRect(
      borderRadius: BorderRadius.circular(r),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20),
        child: Container(
          decoration: BoxDecoration(
            color: RhythmaColors.surface.withOpacity(0.75),
            borderRadius: BorderRadius.circular(r),
            border: Border.all(
              color: RhythmaColors.lavender.withOpacity(0.4),
              width: 1,
            ),
            boxShadow: [
              BoxShadow(
                color: RhythmaColors.primary.withOpacity(0.08),
                blurRadius: 24,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          padding: padding,
          child: child,
        ),
      ),
    );
    if (onTap != null) {
      return GestureDetector(onTap: onTap, child: card);
    }
    return card;
  }
}

/// Gradient container matching .gradient-primary
class GradientBox extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry padding;
  final double borderRadius;
  final List<Color>? colors;

  const GradientBox({
    Key? key,
    required this.child,
    this.padding = const EdgeInsets.all(20),
    this.borderRadius = 24,
    this.colors,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: padding,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: colors ??
              [RhythmaColors.primary, RhythmaColors.rose],
        ),
        borderRadius: BorderRadius.circular(borderRadius),
        boxShadow: [
          BoxShadow(
            color: RhythmaColors.primary.withOpacity(0.28),
            blurRadius: 40,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: child,
    );
  }
}

/// Tinted icon box (the colored icon containers on cards)
class TintedIcon extends StatelessWidget {
  final IconData icon;
  final Color color;
  final double size;

  const TintedIcon({
    Key? key,
    required this.icon,
    required this.color,
    this.size = 36,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: color.withOpacity(0.15),
        borderRadius: BorderRadius.circular(size * 0.35),
      ),
      child: Icon(icon, color: color, size: size * 0.5),
    );
  }
}

/// Section header row with optional action link
class SectionHeader extends StatelessWidget {
  final String title;
  final String? action;
  final VoidCallback? onAction;

  const SectionHeader({
    Key? key,
    required this.title,
    this.action,
    this.onAction,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12, left: 2, right: 2),
      child: Row(
        children: [
          Expanded(
            child: Text(
              title,
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: RhythmaColors.foreground,
              ),
            ),
          ),
          if (action != null)
            GestureDetector(
              onTap: onAction,
              child: Text(
                action!,
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: RhythmaColors.primary,
                ),
              ),
            ),
        ],
      ),
    );
  }
}

/// Gradient scaffold background
class RhythmaScaffold extends StatelessWidget {
  final Widget body;
  final bool extendBody;

  const RhythmaScaffold({
    Key? key,
    required this.body,
    this.extendBody = true,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(gradient: RhythmaGradients.bg),
      child: Scaffold(
        backgroundColor: Colors.transparent,
        extendBody: extendBody,
        body: body,
      ),
    );
  }
}
