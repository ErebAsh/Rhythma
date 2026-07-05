import 'package:dio/dio.dart';
import '../utils/secure_storage.dart';
import '../config/app_config.dart';

class ApiClient {
  static final Dio _dio = Dio(BaseOptions(
    baseUrl: AppConfig.apiBaseUrl,
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 10),
  ));
  static void Function()? _onUnauthorized;
  static bool _initialized = false;

  static void init({void Function()? onUnauthorized}) {
    _onUnauthorized = onUnauthorized;
    if (_initialized) return;
    _initialized = true;
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await SecureStorage.getToken();
          if (token != null && token.isNotEmpty) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          return handler.next(options);
        },
        onError: (error, handler) async {
          if (error.response?.statusCode == 401) {
            await SecureStorage.deleteToken();
            _onUnauthorized?.call();
          }
          return handler.next(error);
        },
      ),
    );
  }

  static Dio get dio => _dio;
}
