import 'package:dio/dio.dart';
import 'package:platform_mobile/config/constants.dart';
import 'package:platform_mobile/core/network/api_client.dart';
import 'package:platform_mobile/core/network/api_exception.dart';
import 'package:platform_mobile/shared/models/category_model.dart';

class CategoriesRepository {
  final ApiClient _api;

  CategoriesRepository(this._api);

  Future<List<ServiceCategory>> getAll() async {
    try {
      final response = await _api.dio.get(ApiConstants.categories);
      return (response.data as List)
          .map((json) => ServiceCategory.fromJson(json))
          .toList();
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  Future<ServiceCategory> getBySlug(String slug) async {
    try {
      final response = await _api.dio.get('${ApiConstants.categories}/$slug');
      return ServiceCategory.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }
}
