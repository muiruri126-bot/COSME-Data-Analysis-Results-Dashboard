class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final dynamic data;

  ApiException({required this.message, this.statusCode, this.data});

  factory ApiException.fromDioError(dynamic error) {
    if (error.response != null) {
      final data = error.response!.data;
      final message = data is Map ? (data['message'] ?? 'Unknown error') : 'Unknown error';
      return ApiException(
        message: message is List ? message.join(', ') : message.toString(),
        statusCode: error.response!.statusCode,
        data: data,
      );
    }
    if (error.type.toString().contains('connectionTimeout') ||
        error.type.toString().contains('receiveTimeout')) {
      return ApiException(message: 'Connection timeout. Please check your internet.');
    }
    return ApiException(message: 'Network error. Please try again.');
  }

  @override
  String toString() => message;
}
