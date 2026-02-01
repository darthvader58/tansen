import 'package:dio/dio.dart';
import 'package:dio_cache_interceptor/dio_cache_interceptor.dart';
import '../constants/api_constants.dart';

class ApiService {
  late final Dio _dio;
  late final CacheOptions _cacheOptions;
  String? _sessionToken;

  ApiService() {
    _dio = Dio(BaseOptions(
      baseUrl: ApiConstants.baseUrl,
      connectTimeout: ApiConstants.connectTimeout,
      receiveTimeout: ApiConstants.receiveTimeout,
      sendTimeout: ApiConstants.sendTimeout,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));

    // Cache configuration
    _cacheOptions = CacheOptions(
      store: MemCacheStore(),
      policy: CachePolicy.request,
      hitCacheOnErrorExcept: [401, 403],
      maxStale: const Duration(days: 7),
      priority: CachePriority.normal,
      cipher: null,
      keyBuilder: CacheOptions.defaultCacheKeyBuilder,
      allowPostMethod: false,
    );

    _dio.interceptors.add(DioCacheInterceptor(options: _cacheOptions));
    
    // Add auth interceptor
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        if (_sessionToken != null) {
          options.headers['Authorization'] = 'Bearer $_sessionToken';
        }
        return handler.next(options);
      },
      onError: (error, handler) {
        if (error.response?.statusCode == 401) {
          // Token expired, clear session
          _sessionToken = null;
        }
        return handler.next(error);
      },
    ));

    // Logging interceptor (only in debug mode)
    _dio.interceptors.add(LogInterceptor(
      requestBody: true,
      responseBody: true,
      error: true,
    ));
  }

  void setSessionToken(String? token) {
    _sessionToken = token;
  }

  String? get sessionToken => _sessionToken;

  // GET request
  Future<Response> get(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      return await _dio.get(
        path,
        queryParameters: queryParameters,
        options: options,
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // POST request
  Future<Response> post(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      return await _dio.post(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // PATCH request
  Future<Response> patch(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      return await _dio.patch(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // DELETE request
  Future<Response> delete(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      return await _dio.delete(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // Upload file
  Future<Response> uploadFile(
    String path,
    String filePath, {
    Map<String, dynamic>? data,
    ProgressCallback? onSendProgress,
  }) async {
    try {
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(filePath),
        ...?data,
      });

      return await _dio.post(
        path,
        data: formData,
        options: Options(
          headers: {'Content-Type': 'multipart/form-data'},
        ),
        onSendProgress: onSendProgress,
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  ApiException _handleError(DioException error) {
    if (error.response != null) {
      final data = error.response!.data;
      if (data is Map<String, dynamic> && data.containsKey('error')) {
        return ApiException(
          errorCode: data['error'] as String,
          message: data['message'] as String,
          statusCode: error.response!.statusCode ?? 500,
        );
      }
    }

    // Network or other errors
    if (error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.receiveTimeout) {
      return ApiException(
        errorCode: 'TIMEOUT',
        message: 'Connection timeout. Please check your internet connection.',
        statusCode: 408,
      );
    }

    if (error.type == DioExceptionType.connectionError) {
      return ApiException(
        errorCode: 'CONNECTION_ERROR',
        message: 'Unable to connect to server. Please check your internet connection.',
        statusCode: 503,
      );
    }

    return ApiException(
      errorCode: 'UNKNOWN_ERROR',
      message: error.message ?? 'An unexpected error occurred.',
      statusCode: 500,
    );
  }
}

class ApiException implements Exception {
  final String errorCode;
  final String message;
  final int statusCode;

  ApiException({
    required this.errorCode,
    required this.message,
    required this.statusCode,
  });

  String getUserFriendlyMessage() {
    switch (errorCode) {
      case 'RATE_LIMIT_EXCEEDED':
        return 'You\'ve reached the daily limit of 10 transcriptions. Please try again tomorrow.';
      case 'INVALID_FILE_FORMAT':
        return 'This file format is not supported. Please use MP3, WAV, M4A, OGG, or FLAC.';
      case 'FILE_TOO_LARGE':
        return 'File is too large. Maximum size is 50MB.';
      case 'TRANSCRIPTION_FAILED':
        return 'We couldn\'t transcribe this audio. Please try a different file.';
      case 'UNAUTHORIZED':
        return 'Please sign in to continue.';
      case 'NOT_FOUND':
        return 'The requested resource was not found.';
      case 'TIMEOUT':
      case 'CONNECTION_ERROR':
        return message;
      default:
        return 'An error occurred. Please try again.';
    }
  }

  @override
  String toString() => 'ApiException($errorCode): $message';
}
