import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:platform_mobile/config/constants.dart';
import 'package:platform_mobile/core/network/api_client.dart';
import 'package:platform_mobile/core/network/api_exception.dart';
import 'package:platform_mobile/shared/models/user_model.dart';

class AuthRepository {
  final ApiClient _api;
  final FlutterSecureStorage _storage;

  AuthRepository(this._api, this._storage);

  Future<void> requestOtp(String phone) async {
    try {
      await _api.dio.post(ApiConstants.requestOtp, data: {'phone': phone});
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  Future<User> verifyOtp(String phone, String otp) async {
    try {
      final response = await _api.dio.post(
        ApiConstants.verifyOtp,
        data: {'phone': phone, 'otp': otp},
      );

      final data = response.data;
      await _storage.write(key: 'access_token', value: data['accessToken']);
      await _storage.write(key: 'refresh_token', value: data['refreshToken']);
      await _storage.write(key: 'user_id', value: data['user']['id']);

      return User.fromJson(data['user']);
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  Future<User?> getCurrentUser() async {
    try {
      final token = await _storage.read(key: 'access_token');
      if (token == null) return null;

      final response = await _api.dio.get(ApiConstants.me);
      return User.fromJson(response.data);
    } catch (_) {
      // Clear stale tokens on any error (user deleted, token invalid, etc.)
      await logout();
      return null;
    }
  }

  Future<void> logout() async {
    await _storage.delete(key: 'access_token');
    await _storage.delete(key: 'refresh_token');
    await _storage.delete(key: 'user_id');
  }

  Future<bool> isLoggedIn() async {
    final token = await _storage.read(key: 'access_token');
    return token != null;
  }
}
