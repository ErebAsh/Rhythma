import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:firebase_auth/firebase_auth.dart' hide User;
import 'package:rhythma/providers/profile_provider.dart';
import 'package:rhythma/providers/locale_provider.dart';
import 'package:rhythma/services/auth_service.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _phoneController = TextEditingController();
  final _otpController = TextEditingController();
  
  bool _loading = false;
  bool _otpSent = false;
  String? _verificationId;

  @override
  void dispose() {
    _phoneController.dispose();
    _otpController.dispose();
    super.dispose();
  }

  void _showMessage(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  Future<void> _sendOtp() async {
    String phone = _phoneController.text.trim();
    if (phone.isEmpty) {
      _showMessage('Please enter your phone number.');
      return;
    }

    // Automatically format to E.164 (+91 for India) if they just entered 10 digits
    if (phone.length == 10 && !phone.startsWith('+')) {
      phone = '+91$phone';
    } else if (!phone.startsWith('+')) {
      _showMessage('Please enter a valid phone number with country code (e.g., +91).');
      return;
    }

    setState(() => _loading = true);
    
    try {
      await FirebaseAuth.instance.verifyPhoneNumber(
        phoneNumber: phone,
        verificationCompleted: (PhoneAuthCredential credential) async {
          await _signInWithCredential(credential);
        },
        verificationFailed: (FirebaseAuthException e) {
          if (!mounted) return;
          setState(() => _loading = false);
          _showMessage(e.message ?? 'Verification failed');
        },
        codeSent: (String verificationId, int? resendToken) {
          if (!mounted) return;
          setState(() {
            _loading = false;
            _otpSent = true;
            _verificationId = verificationId;
          });
          _showMessage('OTP sent to $phone');
        },
        codeAutoRetrievalTimeout: (String verificationId) {
          _verificationId = verificationId;
        },
      );
    } catch (e) {
      if (!mounted) return;
      setState(() => _loading = false);
      _showMessage(e.toString());
    }
  }

  Future<void> _verifyOtp() async {
    final otp = _otpController.text.trim();
    if (otp.isEmpty || _verificationId == null) {
      _showMessage('Please enter the OTP.');
      return;
    }

    setState(() => _loading = true);

    try {
      final credential = PhoneAuthProvider.credential(
        verificationId: _verificationId!,
        smsCode: otp,
      );
      await _signInWithCredential(credential);
    } catch (e) {
      if (!mounted) return;
      setState(() => _loading = false);
      _showMessage('Invalid OTP. Please try again.');
    }
  }

  Future<void> _signInWithCredential(PhoneAuthCredential credential) async {
    try {
      final userCredential = await FirebaseAuth.instance.signInWithCredential(credential);
      final idToken = await userCredential.user?.getIdToken();
      
      if (idToken == null) throw Exception('Failed to get ID token');

      await AuthService().firebaseLogin(idToken);
      if (!mounted) return;

      context.read<ProfileProvider>().reloadProfile();
      final profile = context.read<ProfileProvider>().profile;
      final lang = profile['language'] as String?;
      if (lang != null) {
        context.read<LocaleProvider>().setLocale(Locale(lang));
      }

      Navigator.pushNamedAndRemoveUntil(context, '/home', (route) => false);
    } catch (e) {
      if (!mounted) return;
      setState(() => _loading = false);
      _showMessage(e.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Image.asset(
                  'assets/images/logo.png',
                  height: 120,
                  fit: BoxFit.contain,
                ),
                const SizedBox(height: 12),
                const Text(
                  'Welcome to Rhythma',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 30, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                Text(
                  _otpSent 
                    ? 'Enter the OTP sent to your phone'
                    : 'Log in or sign up with your phone number.',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Theme.of(context).hintColor),
                ),
                const SizedBox(height: 36),
                
                if (!_otpSent) ...[
                  TextField(
                    controller: _phoneController,
                    enabled: !_loading,
                    keyboardType: TextInputType.phone,
                    textInputAction: TextInputAction.next,
                    decoration: const InputDecoration(
                      labelText: 'Phone Number',
                      hintText: '+91 9876543210',
                      prefixIcon: Icon(Icons.phone_outlined),
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton.icon(
                    onPressed: _loading ? null : _sendOtp,
                    icon: _loading
                        ? const SizedBox(
                            width: 18,
                            height: 18,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.send_rounded),
                    label: Text(_loading ? 'Sending OTP...' : 'Get OTP'),
                    style: ElevatedButton.styleFrom(
                      minimumSize: const Size(double.infinity, 50),
                    ),
                  ),
                ] else ...[
                  TextField(
                    controller: _otpController,
                    enabled: !_loading,
                    keyboardType: TextInputType.number,
                    textInputAction: TextInputAction.done,
                    onSubmitted: (_) => _verifyOtp(),
                    decoration: const InputDecoration(
                      labelText: 'OTP',
                      hintText: '123456',
                      prefixIcon: Icon(Icons.password_outlined),
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton.icon(
                    onPressed: _loading ? null : _verifyOtp,
                    icon: _loading
                        ? const SizedBox(
                            width: 18,
                            height: 18,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.login_rounded),
                    label: Text(_loading ? 'Verifying...' : 'Verify OTP'),
                    style: ElevatedButton.styleFrom(
                      minimumSize: const Size(double.infinity, 50),
                    ),
                  ),
                  TextButton(
                    onPressed: _loading ? null : () => setState(() => _otpSent = false),
                    child: const Text("Use a different phone number"),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}
