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

  /// Call once at app startup (after WidgetsFlutterBinding.ensureInitialized)
  static Future<void> init() async {
    if (_initialised) return;
    await Hive.initFlutter();
    await Hive.openBox<Map>(_Keys.cycleBox);
    await Hive.openBox<dynamic>(_Keys.settingsBox);
    await Hive.openBox<Map>(_Keys.userBox);
    _initialised = true;
  }

  // ── Cycle Logs ────────────────────────────────────────────────────────────

  static Box<Map> get _cycleBox => Hive.box<Map>(_Keys.cycleBox);

  /// Save a cycle log entry. Key = ISO date string of start_date.
  static Future<void> saveCycleLog(Map<String, dynamic> log) async {
    final key = log['start_date'] as String;
    await _cycleBox.put(key, log);
  }

  /// Returns all cycle logs sorted by date (most recent first).
  static List<Map<String, dynamic>> getCycleLogs() {
    return _cycleBox.values
        .map((e) => Map<String, dynamic>.from(e))
        .toList()
      ..sort((a, b) =>
          (b['start_date'] as String).compareTo(a['start_date'] as String));
  }

  /// Returns the last [n] cycle logs.
  static List<Map<String, dynamic>> getRecentCycleLogs({int n = 6}) {
    return getCycleLogs().take(n).toList();
  }

  // ── User Settings ─────────────────────────────────────────────────────────

  static Box<dynamic> get _settings => Hive.box<dynamic>(_Keys.settingsBox);

  static String get preferredLanguage =>
      _settings.get('language', defaultValue: 'en') as String;

  static Future<void> setPreferredLanguage(String code) =>
      _settings.put('language', code);

  static bool get cloudSyncEnabled =>
      _settings.get('cloud_sync', defaultValue: false) as bool;

  static Future<void> setCloudSync(bool enabled) =>
      _settings.put('cloud_sync', enabled);

  static bool get smsEnabled =>
      _settings.get('sms_enabled', defaultValue: false) as bool;

  static Future<void> setSmsEnabled(bool enabled) =>
      _settings.put('sms_enabled', enabled);

  static String? getThemeMode() =>
      _settings.get('theme_mode') as String?;

  static Future<void> setThemeMode(String mode) =>
      _settings.put('theme_mode', mode);

  static int? getPrimaryColor() =>
      _settings.get('primary_color') as int?;

  static Future<void> setPrimaryColor(int colorValue) =>
      _settings.put('primary_color', colorValue);

  // ── User Profile ──────────────────────────────────────────────────────────

  static Box<Map> get _userBox => Hive.box<Map>(_Keys.userBox);

  static Map<String, dynamic>? getProfile() {
    if (isTesting) return mockProfile;
    final raw = _userBox.get('profile');
    return raw != null ? Map<String, dynamic>.from(raw) : null;
  }

  static Future<void> saveProfile(Map<String, dynamic> profile) async {
    if (isTesting) {
      mockProfile = profile;
      return;
    }
    await _userBox.put('profile', profile);
  }

  /// Save (merge) a single field into today's — or a given date's — cycle log
  /// entry. Used by quick log actions (e.g. Home screen Flow/Mood/Sleep/Stress
  /// buttons) that log one value at a time rather than a full CycleLog form.
  static Future<void> saveQuickLogField(DateTime date, String field, String value) async {
    final key = _dateKey(date);
    final existing = _cycleBox.get(key);
    final data = existing != null
        ? Map<String, dynamic>.from(existing)
        : <String, dynamic>{'start_date': key};
    data[field] = value;
    await _cycleBox.put(key, data);
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

  /// Returns the saved assistant conversation (role/text pairs), oldest first.
  static List<Map<String, String>> getChatHistory() {
    final raw = _settings.get('chat_history');
    if (raw != null) {
      return List<Map<String, String>>.from(
        (raw as List).map((e) => Map<String, String>.from(e as Map)),
      );
    }
    return [];
  }

  /// Persists the assistant conversation so it survives app restarts.
  static Future<void> saveChatHistory(List<Map<String, String>> history) =>
      _settings.put('chat_history', history);

  static Future<void> clearChatHistory() => _settings.delete('chat_history');

  // ── Clear all data ────────────────────────────────────────────────────────

  static Future<void> clearAll() async {
    if (isTesting) {
      mockProfile = null;
      mockEmergencyContacts = [];
      return;
    }
    await _cycleBox.clear();
    await _settings.clear();
    await _userBox.clear();
  }
}