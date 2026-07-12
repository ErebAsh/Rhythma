import 'package:email_validator/email_validator.dart';
import 'package:flutter/material.dart';
import 'package:rhythma/l10n/app_localizations.dart';
import 'package:rhythma/screens/auth/login_screen.dart';
import 'package:rhythma/services/auth_service.dart';
import 'package:rhythma/services/local_storage_service.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  final _ageController = TextEditingController();
  final _cycleLengthController = TextEditingController(text: '28');
  bool _loading = false;
  bool _obscurePassword = true;

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _usernameController.dispose();
    _passwordController.dispose();
    _ageController.dispose();
    _cycleLengthController.dispose();
    super.dispose();
  }

  Future<void> _register() async {
    final l10n = AppLocalizations.of(context)!;
    final email = _emailController.text.trim();
    final password = _passwordController.text;
    final username = _usernameController.text.trim();
    final fullName = _nameController.text.trim();
    final ageVal = int.tryParse(_ageController.text.trim());
    final cycleVal = int.tryParse(_cycleLengthController.text.trim());

    final validationError = _validateUsername(l10n, username) ??
        _validateEmail(l10n, email) ??
        _validatePassword(l10n, password) ??
        _validateAge(l10n, ageVal) ??
        _validateCycleLength(l10n, cycleVal);
    if (validationError != null) {
      _showMessage(validationError);
      return;
    }

    setState(() => _loading = true);
    try {
      await AuthService().register(
        username,
        email,
        password,
        fullName.isEmpty ? null : fullName,
      );

      // Seed the on-device profile with the details already collected here,
      // so it's populated the moment the user logs in for the first time
      // instead of falling back to placeholder defaults.
      await LocalStorageService.saveProfile({
        'name': fullName.isEmpty ? username : fullName,
        'age': ageVal!,
        'cycle_length': cycleVal!,
      });

      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(l10n.registerSuccess),
          backgroundColor: Colors.green,
        ),
      );
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const LoginScreen()),
      );
    } catch (e) {
      if (mounted) _showMessage(_friendlyErrorMessage(l10n, e));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  String _friendlyErrorMessage(AppLocalizations l10n, Object error) {
    final msg = error.toString();
    if (msg.contains('SocketException') || msg.contains('TimeoutException')) {
      return l10n.registerErrorNetwork;
    }
    if (msg.contains('409')) return l10n.registerErrorConflict;
    return l10n.registerErrorGeneric;
  }

  String? _validateEmail(AppLocalizations l10n, String email) {
    if (email.isEmpty) return l10n.registerEmailRequired;
    if (!EmailValidator.validate(email)) return l10n.registerEmailInvalid;
    return null;
  }

  String? _validatePassword(AppLocalizations l10n, String password) {
    if (password.isEmpty) return l10n.registerPasswordRequired;
    if (password.length < 8) return l10n.registerPasswordTooShort;
    return null;
  }

  String? _validateUsername(AppLocalizations l10n, String username) {
    if (username.isEmpty) return l10n.registerUsernameRequired;
    if (username.length < 6) return l10n.registerUsernameTooShort;
    if (username.length > 30) return l10n.registerUsernameTooLong;
    if (!RegExp(r'^[a-zA-Z0-9_]+$').hasMatch(username)) {
      return l10n.registerUsernameInvalid;
    }
    return null;
  }

  String? _validateAge(AppLocalizations l10n, int? age) {
    if (age == null) return l10n.registerAgeInvalid;
    if (age < 10 || age > 120) return l10n.registerAgeRange;
    return null;
  }

  String? _validateCycleLength(AppLocalizations l10n, int? cycleLength) {
    if (cycleLength == null) return l10n.registerCycleInvalid;
    if (cycleLength < 15 || cycleLength > 45) {
      return l10n.registerCycleRange;
    }
    return null;
  }

  void _showMessage(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 24),
              Icon(
                Icons.favorite_rounded,
                size: 52,
                color: Theme.of(context).primaryColor,
              ),
              const SizedBox(height: 12),
              Text(
                l10n.registerTitle,
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Text(
                l10n.registerSubtitle,
                textAlign: TextAlign.center,
                style: TextStyle(color: Theme.of(context).hintColor),
              ),
              const SizedBox(height: 36),
              TextField(
                controller: _nameController,
                enabled: !_loading,
                textCapitalization: TextCapitalization.words,
                decoration: InputDecoration(
                  labelText: l10n.registerFullName,
                  prefixIcon: const Icon(Icons.badge_outlined),
                  border: const OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _emailController,
                enabled: !_loading,
                keyboardType: TextInputType.emailAddress,
                textInputAction: TextInputAction.next,
                decoration: InputDecoration(
                  labelText: l10n.registerEmail,
                  prefixIcon: const Icon(Icons.email_outlined),
                  border: const OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _usernameController,
                enabled: !_loading,
                textInputAction: TextInputAction.next,
                decoration: InputDecoration(
                  labelText: l10n.loginUsername,
                  helperText: l10n.registerUsernameHelper,
                  prefixIcon: const Icon(Icons.person_outline),
                  border: const OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _ageController,
                enabled: !_loading,
                keyboardType: TextInputType.number,
                textInputAction: TextInputAction.next,
                decoration: InputDecoration(
                  labelText: l10n.registerAge,
                  helperText: l10n.registerAgeHelper,
                  prefixIcon: const Icon(Icons.cake_outlined),
                  border: const OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _cycleLengthController,
                enabled: !_loading,
                keyboardType: TextInputType.number,
                textInputAction: TextInputAction.next,
                decoration: InputDecoration(
                  labelText: l10n.registerCycleLength,
                  helperText: l10n.registerCycleHelper,
                  prefixIcon: const Icon(Icons.calendar_month_outlined),
                  border: const OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _passwordController,
                enabled: !_loading,
                obscureText: _obscurePassword,
                onSubmitted: (_) => _register(),
                decoration: InputDecoration(
                  labelText: l10n.loginPassword,
                  helperText: l10n.registerPasswordHelper,
                  prefixIcon: const Icon(Icons.lock_outline),
                  border: const OutlineInputBorder(),
                  suffixIcon: IconButton(
                    tooltip: _obscurePassword ? l10n.loginShowPassword : l10n.loginHidePassword,
                    icon: Icon(
                      _obscurePassword ? Icons.visibility_off : Icons.visibility,
                    ),
                    onPressed: () {
                      setState(() => _obscurePassword = !_obscurePassword);
                    },
                  ),
                ),
              ),
              const SizedBox(height: 24),
              ElevatedButton.icon(
                onPressed: _loading ? null : _register,
                icon: _loading
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.person_add_alt_1_rounded),
                label: Text(_loading ? l10n.registerCreating : l10n.registerButton),
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size(double.infinity, 50),
                ),
              ),
              TextButton(
                onPressed: _loading
                    ? null
                    : () {
                        Navigator.pushReplacement(
                          context,
                          MaterialPageRoute(builder: (_) => const LoginScreen()),
                        );
                      },
                child: Text(l10n.registerHaveAccount),
              ),
            ],
          ),
        ),
      ),
    );
  }
}