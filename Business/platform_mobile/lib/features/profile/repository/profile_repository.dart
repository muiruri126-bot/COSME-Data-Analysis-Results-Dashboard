import 'package:dio/dio.dart';
import 'package:platform_mobile/config/constants.dart';
import 'package:platform_mobile/core/network/api_client.dart';
import 'package:platform_mobile/core/network/api_exception.dart';
import 'package:platform_mobile/shared/models/user_model.dart';

class ProfileRepository {
  final ApiClient _api;

  ProfileRepository(this._api);

  Future<User> getMyProfile() async {
    try {
      final response = await _api.dio.get(ApiConstants.me);
      return User.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  Future<Profile> createProfile(Map<String, dynamic> data) async {
    try {
      final response = await _api.dio.post(ApiConstants.profiles, data: data);
      return Profile.fromJson(response.data);
    } on DioException catch (e) {
      // If profile already exists (409), fall back to update
      if (e.response?.statusCode == 409) {
        return updateProfile(data);
      }
      throw ApiException.fromDioError(e);
    }
  }

  Future<Profile> updateProfile(Map<String, dynamic> data) async {
    try {
      final response = await _api.dio.put(ApiConstants.profiles, data: data);
      return Profile.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  Future<User> getPublicProfile(String userId) async {
    try {
      final response = await _api.dio.get('${ApiConstants.userProfile}/$userId');
      return User.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  Future<String> uploadAvatar(String filePath) async {
    try {
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(filePath),
        'type': 'avatar',
      });
      final response = await _api.dio.post(ApiConstants.upload, data: formData);
      return response.data['url'];
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }
}
