import 'package:dio/dio.dart';
import 'package:platform_mobile/config/constants.dart';
import 'package:platform_mobile/core/network/api_client.dart';
import 'package:platform_mobile/core/network/api_exception.dart';
import 'package:platform_mobile/shared/models/listing_model.dart';

class ListingsRepository {
  final ApiClient _api;

  ListingsRepository(this._api);

  Future<Map<String, dynamic>> search({
    String? categoryId,
    String? categorySlug,
    String? query,
    double? lat,
    double? lng,
    double? radiusKm,
    String? county,
    double? budgetMin,
    double? budgetMax,
    String? engagementType,
    String? listingType,
    String? sortBy,
    int page = 1,
    int limit = 20,
  }) async {
    try {
      final params = <String, dynamic>{
        'page': page,
        'limit': limit,
      };
      if (categoryId != null) params['categoryId'] = categoryId;
      if (categorySlug != null) params['categorySlug'] = categorySlug;
      if (query != null) params['query'] = query;
      if (lat != null) params['lat'] = lat;
      if (lng != null) params['lng'] = lng;
      if (radiusKm != null) params['radiusKm'] = radiusKm;
      if (county != null) params['county'] = county;
      if (budgetMin != null) params['budgetMin'] = budgetMin;
      if (budgetMax != null) params['budgetMax'] = budgetMax;
      if (engagementType != null) params['engagementType'] = engagementType;
      if (listingType != null) params['listingType'] = listingType;
      if (sortBy != null) params['sortBy'] = sortBy;

      final response = await _api.dio.get(
        ApiConstants.searchListings,
        queryParameters: params,
      );

      final data = response.data;
      return {
        'listings': (data['data'] as List).map((j) => Listing.fromJson(j)).toList(),
        'total': data['meta']['total'],
        'page': data['meta']['page'],
        'totalPages': data['meta']['totalPages'],
      };
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  Future<Listing> getById(String id) async {
    try {
      final response = await _api.dio.get('${ApiConstants.listings}/$id');
      return Listing.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  Future<Listing> create(Map<String, dynamic> data) async {
    try {
      final response = await _api.dio.post(ApiConstants.listings, data: data);
      return Listing.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  Future<Listing> update(String id, Map<String, dynamic> data) async {
    try {
      final response = await _api.dio.put('${ApiConstants.listings}/$id', data: data);
      return Listing.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  Future<void> delete(String id) async {
    try {
      await _api.dio.delete('${ApiConstants.listings}/$id');
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  Future<List<Listing>> getRecent({int limit = 20}) async {
    final result = await search(sortBy: 'recent', limit: limit);
    return result['listings'] as List<Listing>;
  }
}
