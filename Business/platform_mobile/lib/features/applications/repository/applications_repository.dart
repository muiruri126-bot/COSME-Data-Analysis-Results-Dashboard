import 'package:dio/dio.dart';
import 'package:platform_mobile/config/constants.dart';
import 'package:platform_mobile/core/network/api_client.dart';
import 'package:platform_mobile/core/network/api_exception.dart';
import 'package:platform_mobile/shared/models/models.dart';

class ApplicationsRepository {
  final ApiClient _api;

  ApplicationsRepository(this._api);

  Future<List<Application>> getMyApplications() async {
    try {
      final response = await _api.dio.get('${ApiConstants.applications}/my');
      return (response.data as List)
          .map((json) => Application.fromJson(json))
          .toList();
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  Future<List<Application>> getApplicationsForListing(String listingId) async {
    try {
      final response = await _api.dio.get(
        '${ApiConstants.applications}/listing/$listingId',
      );
      return (response.data as List)
          .map((json) => Application.fromJson(json))
          .toList();
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  Future<Application> apply(Map<String, dynamic> data) async {
    try {
      final response = await _api.dio.post(ApiConstants.applications, data: data);
      return Application.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  Future<Application> updateStatus(String id, String status) async {
    try {
      final response = await _api.dio.patch(
        '${ApiConstants.applications}/$id/status',
        data: {'status': status},
      );
      return Application.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }
}
