part of '../api_service.dart';

extension ChannelApi on ApiService {
  Future<PaginatedResult<Message>> getMessages({
    int page = 1,
    int size = 50,
    int? senderId,
    int? receiverId,
    int? groupId,
    int? channelId,
    bool unreadOnly = false,
  }) async {
    final params = <String, String>{
      'page': '$page',
      'size': '$size',
    };
    if (senderId != null) params['sender_id'] = '$senderId';
    if (receiverId != null) params['receiver_id'] = '$receiverId';
    if (groupId != null) params['group_id'] = '$groupId';
    if (channelId != null) params['channel_id'] = '$channelId';
    if (unreadOnly) params['unread_only'] = 'true';
    final data = await _get('/chat/messages', params);
    return _paginated(data, Message.fromJson);
  }

  Future<Message> sendMessage(
    int senderId,
    String content, {
    int? receiverId,
    int? groupId,
    int? channelId,
    String messageType = 'text',
    String? mediaUrl,
    double? latitude,
    double? longitude,
    String? vcardData,
    String? icalData,
  }) async {
    final body = <String, dynamic>{
      'content': content,
      'sender_id': senderId,
      'message_type': messageType,
    };
    if (receiverId != null) body['receiver_id'] = receiverId;
    if (groupId != null) body['group_id'] = groupId;
    if (channelId != null) body['channel_id'] = channelId;
    if (mediaUrl != null) body['media_url'] = mediaUrl;
    if (latitude != null) body['latitude'] = latitude;
    if (longitude != null) body['longitude'] = longitude;
    if (vcardData != null) body['vcard_data'] = vcardData;
    if (icalData != null) body['ical_data'] = icalData;
    final data = await create('/chat/messages', body);
    return Message.fromJson(data);
  }

  Future<String> uploadChatImage(String filePath) async {
    final data = await _uploadFile('/uploads/chat-image', filePath);
    return data['url']?.toString() ?? '';
  }

  Future<void> markMessageRead(int messageId) async {
    await request('PUT', '/chat/messages/$messageId/read');
  }

  Future<void> deleteMessage(int messageId) async {
    await request('DELETE', '/chat/messages/$messageId');
  }
}
