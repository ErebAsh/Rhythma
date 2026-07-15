import 'package:flutter/material.dart';
import '../../config/theme.dart';
import '../../components/shared.dart';
import '../../services/api_client.dart';

/// SMS Health Summary screen.
/// Users can configure their phone number to receive weekly
/// menstrual health summaries via SMS — useful in low-data areas.
class SmsScreen extends StatefulWidget {
  const SmsScreen({super.key});

  @override
  State<SmsScreen> createState() => _SmsScreenState();
}

class _SmsScreenState extends State<SmsScreen> {
  final _phoneCtrl = TextEditingController();
  bool _smsEnabled = false;
  bool _saving = false;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  @override
  void dispose() {
    _phoneCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadSettings() async {
    setState(() => _loading = true);
    try {
      final dio = ApiClient.dio;
      final response = await dio.get('/sms/settings');
      setState(() {
        _phoneCtrl.text = response.data['phoneNumber'] ?? '';
        _smsEnabled = response.data['enabled'] ?? false;
        _loading = false;
      });
    } catch (e) {
      setState(() => _loading = false);
      // If endpoint returns 404, user has no settings yet – that's fine.
    }
  }

  Future<void> _save() async {
    final phone = _phoneCtrl.text.trim();
    if (_smsEnabled && phone.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please enter a phone number'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    setState(() => _saving = true);
    try {
      final dio = ApiClient.dio;
      await dio.post(
        '/sms/settings',
        data: {
          'phoneNumber': phone,
          'enabled': _smsEnabled,
        },
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('SMS settings saved successfully!'),
            backgroundColor: RhythmaColors.teal,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to save: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _saving = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(20, 8, 20, 100),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Padding(
            padding: const EdgeInsets.only(bottom: 20, top: 8),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('SMS Summaries',
                    style: TextStyle(
                        fontSize: 26,
                        fontWeight: FontWeight.w700,
                        color: RhythmaColors.foreground)),
                const SizedBox(height: 2),
                Text('Stay informed even without the app',
                    style:
                        TextStyle(fontSize: 13, color: RhythmaColors.mutedFg)),
              ],
            ),
          ),

          // Info card
          GlassCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const TintedIcon(
                        icon: Icons.sms_rounded, color: RhythmaColors.teal),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text('Weekly Health Summary',
                          style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                              color: RhythmaColors.foreground)),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Text(
                  'Every week, Rhythma will send you a brief summary of your '
                  'cycle status, health score, and any important patterns — '
                  'directly to your phone via SMS. Works without data or the app.',
                  style: TextStyle(
                      fontSize: 13, color: RhythmaColors.mutedFg, height: 1.5),
                ),
              ],
            ),
          ),

          const SizedBox(height: 16),

          // Config card
          GlassCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Configuration',
                    style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w600,
                        color: RhythmaColors.foreground)),
                const SizedBox(height: 16),
                TextField(
                  controller: _phoneCtrl,
                  keyboardType: TextInputType.phone,
                  decoration: const InputDecoration(
                    labelText: 'Phone Number',
                    hintText: '+91 98765 43210',
                    prefixIcon: Icon(Icons.phone_rounded),
                  ),
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: Text('Enable weekly SMS',
                          style: TextStyle(
                              fontSize: 14, color: RhythmaColors.foreground)),
                    ),
                    Switch(
                      value: _smsEnabled,
                      onChanged: (v) => setState(() => _smsEnabled = v),
                      activeThumbColor: RhythmaColors.primary,
                      activeTrackColor: RhythmaColors.primary.withValues(
                          alpha:
                              0.5), // ✅ Fixed: withValues instead of withOpacity
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: _saving ? null : _save,
                    child: _saving
                        ? const SizedBox(
                            width: 18,
                            height: 18,
                            child: CircularProgressIndicator(
                                strokeWidth: 2, color: Colors.white))
                        : const Text('Save Settings'),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 12),

          // Sample SMS preview
          GlassCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Sample SMS',
                    style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w700,
                        color: RhythmaColors.mutedFg,
                        letterSpacing: 0.8)),
                const SizedBox(height: 10),
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: RhythmaColors.surfaceMuted,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    '🌸 Rhythma Weekly Summary\n'
                    'Cycle Day 14 · Ovulation phase\n'
                    'Health Score: 82/100 · CVI: 72\n'
                    'Tip: Stay hydrated this week.\n'
                    'Reply STOP to unsubscribe.',
                    style: TextStyle(
                        fontSize: 13,
                        color: RhythmaColors.foreground,
                        height: 1.6,
                        fontFamily: 'monospace'),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
