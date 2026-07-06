import 'package:hive_flutter/hive_flutter.dart';

/// Keys used in Hive boxes
class _Keys {
  static const cycleBox = 'cycle_logs';
  static const settingsBox = 'settings';
  static const userBox = 'user_profile';
}

/// Manages all on-device storage via Hive.
/// All health data is stored locally first and synced to Firestore
/// only when the user explicitly enables cloud sync.
class LocalStorageService {
  static bool _initialised = false;

  // Test mocks to bypass Hive lock conflicts during unit/widget tests
  static bool isTesting = false;
  static Map<String, dynamic>? mockProfile;
  static List<Map<String, String>> mockEmergencyContacts = [];
  static bool mockOnboardingCompleted = false;

  /// Call once at app startup (after WidgetsFlutterBinding.ensureInitialized)
  static Future<void> init() async {
    if (_initialised) return;
    await Hive.initFlutter();
    await Hive.openBox<Map>(_Keys.cycleBox);
    await Hive.openBox<dynamic>(_Keys.settingsBox);
    await Hive.openBox<Map>(_Keys.userBox);
    _initialised = true;
  }

  // ── Per-account data scoping ────────────────────────────────────────────
  //
  // This store was originally shared by whoever happened to be logged in —
  // profile/chat history/cycle logs weren't tied to an account, just the
  // device. That meant a second person logging into a different account on
  // the same phone would see the first person's data. Personal data below
  // is now namespaced by the signed-in user's id. Device-level preferences
  // (theme, language, notification toggles) intentionally stay un-scoped,
  // since those are reasonably "this phone's" settings rather than "this
  // account's".

  static const _kCurrentUserId = 'current_user_id';

  /// The id of the currently signed-in user. Set by AuthService right after
  /// a successful login or a successful session validation at launch.
  static String? get currentUserId => _settings.get(_kCurrentUserId) as String?;

  static Future<void> setCurrentUserId(String? userId) async {
    if (userId == null) {
      // Just clears the "which account is active" pointer — does NOT
      // delete anyone's data, so it's still there if they log back in.
      await _settings.delete(_kCurrentUserId);
      return;
    }
    await _migrateLegacyDataIfNeeded(userId);
    await _settings.put(_kCurrentUserId, userId);
  }

  static String _scoped(String baseKey) {
    final uid = currentUserId;
    return uid == null ? baseKey : '$uid::$baseKey';
  }

  /// One-time migration: silently moves any pre-existing un-scoped entries
  /// into the first account that logs in after this update, so an
  /// existing user's profile/chat history/cycle logs don't appear to
  /// vanish just because storage is now namespaced.
  static Future<void> _migrateLegacyDataIfNeeded(String uid) async {
    final scopedProfileKey = '$uid::profile';
    if (_userBox.containsKey('profile') && !_userBox.containsKey(scopedProfileKey)) {
      final legacyProfile = _userBox.get('profile');
      if (legacyProfile != null) {
        await _userBox.put(scopedProfileKey, legacyProfile);
      }
      await _userBox.delete('profile');
    }

    const legacyChatKey = 'chat_history';
    final scopedChatKey = '$uid::chat_history';
    if (_settings.containsKey(legacyChatKey) && !_settings.containsKey(scopedChatKey)) {
      await _settings.put(scopedChatKey, _settings.get(legacyChatKey));
      await _settings.delete(legacyChatKey);
    }

    final legacyCycleKeys =
        _cycleBox.keys.where((k) => !k.toString().contains('::')).toList();
    for (final key in legacyCycleKeys) {
      final legacyLog = _cycleBox.get(key);
      if (legacyLog != null) {
        await _cycleBox.put('$uid::$key', legacyLog);
      }
      await _cycleBox.delete(key);
    }
  }

  // ── Cycle Logs ────────────────────────────────────────────────────────────

  static Box<Map> get _cycleBox => Hive.box<Map>(_Keys.cycleBox);

  /// Save a cycle log entry. Key = ISO date string of start_date, scoped
  /// to the currently signed-in user.
  static Future<void> saveCycleLog(Map<String, dynamic> log) async {
    if (isTesting) return;
    final key = log['start_date'] as String;
    await _cycleBox.put(_scoped(key), log);
  }

  /// Returns all cycle logs for the current user, sorted most recent first.
  static List<Map<String, dynamic>> getCycleLogs() {
    final uid = currentUserId;
    final prefix = uid == null ? null : '$uid::';
    return _cycleBox.keys
        .where((k) {
          final key = k.toString();
          return prefix != null ? key.startsWith(prefix) : !key.contains('::');
        })
        .map((k) => Map<String, dynamic>.from(_cycleBox.get(k) as Map))
        .toList()
      ..sort((a, b) =>
          (b['start_date'] as String).compareTo(a['start_date'] as String));
  }

  /// Returns the last [n] cycle logs.
  static List<Map<String, dynamic>> getRecentCycleLogs({int n = 6}) {
    if (isTesting) return [];
    return getCycleLogs().take(n).toList();
  }

  // ── User Settings ─────────────────────────────────────────────────────────

  static Box<dynamic> get _settings => Hive.box<dynamic>(_Keys.settingsBox);

  static String get preferredLanguage {
    if (isTesting) return 'en';
    return _settings.get('language', defaultValue: 'en') as String;
  }

  static Future<void> setPreferredLanguage(String code) async {
    if (isTesting) return;
    await _settings.put('language', code);
  }

  static bool get cloudSyncEnabled {
    if (isTesting) return false;
    return _settings.get('cloud_sync', defaultValue: false) as bool;
  }

  static Future<void> setCloudSync(bool enabled) async {
    if (isTesting) return;
    await _settings.put('cloud_sync', enabled);
  }

  static bool get smsEnabled {
    if (isTesting) return false;
    return _settings.get('sms_enabled', defaultValue: false) as bool;
  }

  static Future<void> setSmsEnabled(bool enabled) async {
    if (isTesting) return;
    await _settings.put('sms_enabled', enabled);
  }

  static String? getThemeMode() {
    if (isTesting) return null;
    return _settings.get('theme_mode') as String?;
  }

  static Future<void> setThemeMode(String mode) async {
    if (isTesting) return;
    await _settings.put('theme_mode', mode);
  }

  static int? getPrimaryColor() {
    if (isTesting) return null;
    return _settings.get('primary_color') as int?;
  }

  static Future<void> setPrimaryColor(int colorValue) async {
    if (isTesting) return;
    await _settings.put('primary_color', colorValue);
  }

  // ── Onboarding ────────────────────────────────────────────────────────────

  /// Returns true if the user has completed onboarding at least once.
  static bool get onboardingCompleted {
    if (isTesting) return mockOnboardingCompleted;
    return _settings.get('onboarding_completed', defaultValue: false) as bool;
  }

  static Future<void> setOnboardingCompleted(bool value) async {
    if (isTesting) {
      mockOnboardingCompleted = value;
      return;
    }
    await _settings.put('onboarding_completed', value);
  }

  // ── User Profile ──────────────────────────────────────────────────────────

  static Box<Map> get _userBox => Hive.box<Map>(_Keys.userBox);

  static Map<String, dynamic>? getProfile() {
    if (isTesting) return mockProfile;
    final raw = _userBox.get(_scoped('profile'));
    return raw != null ? Map<String, dynamic>.from(raw) : null;
  }

  static Future<void> saveProfile(Map<String, dynamic> profile) async {
    if (isTesting) {
      mockProfile = profile;
      return;
    }
    await _userBox.put(_scoped('profile'), profile);
  }

  /// Save (merge) a single field into today's — or a given date's — cycle log
  /// entry. Used by quick log actions (e.g. Home screen Flow/Mood/Sleep/Stress
  /// buttons) that log one value at a time rather than a full CycleLog form.
  static Future<void> saveQuickLogField(DateTime date, String field, String value) async {
    final key = _scoped(_dateKey(date));
    final existing = _cycleBox.get(key);
    final data = existing != null
        ? Map<String, dynamic>.from(existing)
        : <String, dynamic>{'start_date': _dateKey(date)};
    data[field] = value;
    await _cycleBox.put(key, data);
  }

  /// Merges [updates] into the existing profile instead of overwriting it.
  /// Fields present in [updates] overwrite existing values; other fields
  /// (e.g. those saved during onboarding) are left untouched.
  static Future<void> mergeProfile(Map<String, dynamic> updates) async {
    final existing = getProfile() ?? {};
    final merged = {...existing, ...updates};
    await saveProfile(merged);
    if (isTesting) mockProfile = merged;
  }
  static String _dateKey(DateTime date) =>
      '${date.year.toString().padLeft(4, '0')}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';

  // ── Emergency Contacts ────────────────────────────────────────────────────

  /// Returns a list of saved emergency contacts.
  static List<Map<String, String>> getEmergencyContacts() {
    if (isTesting) return mockEmergencyContacts;
    final raw = _settings.get('emergency_contacts');
    if (raw != null) {
      return List<Map<String, String>>.from(
        (raw as List).map((e) => Map<String, String>.from(e as Map)),
      );
    }
    return [];
  }

  /// Save the list of emergency contacts.
  static Future<void> saveEmergencyContacts(List<Map<String, String>> contacts) async {
    if (isTesting) {
      mockEmergencyContacts = contacts;
      return;
    }
    await _settings.put('emergency_contacts', contacts);
  }

  // ── Assistant Chat History ────────────────────────────────────────────────

  /// Returns the saved assistant conversation (role/content pairs), oldest first.
  static List<Map<String, String>> getChatHistory() {
    final raw = _settings.get(_scoped('chat_history'));
    if (raw != null) {
      return List<Map<String, String>>.from(
        (raw as List).map((e) => Map<String, String>.from(e as Map)),
      );
    }
    return [];
  }

  /// Persists the assistant conversation so it survives app restarts.
  static Future<void> saveChatHistory(List<Map<String, String>> history) =>
      _settings.put(_scoped('chat_history'), history);

  static Future<void> clearChatHistory() => _settings.delete(_scoped('chat_history'));

  // ── Clear all data ────────────────────────────────────────────────────────

  /// Wipes every local box for every account that's ever used this device
  /// (not just the currently signed-in one) — this is a full device reset,
  /// not a per-account logout. Not currently called anywhere in the app;
  /// kept for a future "reset this device" debug/support feature.
  static Future<void> clearAll() async {
    if (isTesting) {
      mockProfile = null;
      mockEmergencyContacts = [];
      mockOnboardingCompleted = false;
      return;
    }
    await _cycleBox.clear();
    await _settings.clear();
    await _userBox.clear();
  }
}