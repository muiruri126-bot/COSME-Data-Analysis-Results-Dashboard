import 'package:dio/dio.dart';
import 'package:platform_mobile/config/constants.dart';
import 'package:platform_mobile/core/network/api_client.dart';
import 'package:platform_mobile/core/network/api_exception.dart';
import 'package:platform_mobile/shared/models/models.dart';

class NotificationsRepository {
  final ApiClient _api;

  NotificationsRepository(this._api);

  Future<List<AppNotification>> getAll() async {
    try {
      final response = await _api.dio.get(ApiConstants.notifications);
      final data = response.data;
      final list = data is List ? data : (data['data'] as List);
      return list
          .map((json) => AppNotification.fromJson(json))
          .toList();
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  Future<void> markAsRead(String id) async {
    try {
      await _api.dio.patch('${ApiConstants.notifications}/$id/read');
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  Future<void> markAllAsRead() async {
    try {
      await _api.dio.patch('${ApiConstants.notifications}/read-all');
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }
}
