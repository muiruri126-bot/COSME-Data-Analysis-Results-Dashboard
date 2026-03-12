import 'package:dio/dio.dart';
import 'package:platform_mobile/config/constants.dart';
import 'package:platform_mobile/core/network/api_client.dart';
import 'package:platform_mobile/core/network/api_exception.dart';
import 'package:platform_mobile/shared/models/models.dart';

class ChatRepository {
  final ApiClient _api;

  ChatRepository(this._api);

  Future<List<Conversation>> getConversations() async {
    try {
      final response = await _api.dio.get(ApiConstants.conversations);
      return (response.data as List)
          .map((json) => Conversation.fromJson(json))
          .toList();
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  Future<List<Message>> getMessages(String conversationId) async {
    try {
      final response = await _api.dio.get(
        '${ApiConstants.conversations}/$conversationId/messages',
      );
      final data = response.data;
      final list = data is List ? data : (data['data'] as List);
      return list
          .map((json) => Message.fromJson(json))
          .toList();
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  Future<Message> sendMessage(String conversationId, String content) async {
    try {
      final response = await _api.dio.post(
        '/chat/messages',
        data: {'conversationId': conversationId, 'content': content},
      );
      return Message.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  Future<Conversation> createConversation(String recipientId, {String? listingId}) async {
    try {
      final data = <String, dynamic>{'participantId': recipientId};
      if (listingId != null) data['listingId'] = listingId;
      final response = await _api.dio.post(
        ApiConstants.conversations,
        data: data,
      );
      return Conversation.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }
}
