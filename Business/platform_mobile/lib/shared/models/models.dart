double? _toDouble(dynamic v) {
  if (v == null) return null;
  if (v is num) return v.toDouble();
  if (v is String) return double.tryParse(v);
  return null;
}

class Conversation {
  final String id;
  final String? listingId;
  final String status;
  final DateTime createdAt;
  final List<ConversationParticipant> participants;
  final Message? lastMessage;
  final String? listingTitle;

  Conversation({
    required this.id,
    this.listingId,
    required this.status,
    required this.createdAt,
    required this.participants,
    this.lastMessage,
    this.listingTitle,
  });

  factory Conversation.fromJson(Map<String, dynamic> json) {
    // Backend returns 'messages' array (take:1), extract last message from it
    Message? lastMsg;
    if (json['lastMessage'] != null) {
      lastMsg = Message.fromJson(json['lastMessage']);
    } else if (json['messages'] is List && (json['messages'] as List).isNotEmpty) {
      final m = (json['messages'] as List).first;
      lastMsg = Message(
        id: m['id'] ?? '',
        conversationId: json['id'] ?? '',
        senderId: m['senderId'] ?? '',
        content: m['content'] ?? '',
        messageType: m['messageType'] ?? 'text',
        createdAt: DateTime.parse(m['createdAt']),
      );
    }

    return Conversation(
      id: json['id'],
      listingId: json['listingId'],
      status: json['status'],
      createdAt: DateTime.parse(json['createdAt']),
      participants: (json['participants'] as List?)
              ?.map((p) => ConversationParticipant.fromJson(p))
              .toList() ??
          [],
      lastMessage: lastMsg,
      listingTitle: json['listing']?['title'],
    );
  }

  ConversationParticipant? getOtherParticipant(String currentUserId) {
    return participants.where((p) => p.userId != currentUserId).firstOrNull;
  }
}

class ConversationParticipant {
  final String userId;
  final String? displayName;
  final String? avatarUrl;

  ConversationParticipant({
    required this.userId,
    this.displayName,
    this.avatarUrl,
  });

  factory ConversationParticipant.fromJson(Map<String, dynamic> json) {
    return ConversationParticipant(
      userId: json['userId'],
      displayName: json['user']?['profile']?['displayName'],
      avatarUrl: json['user']?['profile']?['avatarUrl'],
    );
  }
}

class Message {
  final String id;
  final String conversationId;
  final String senderId;
  final String content;
  final String messageType;
  final DateTime createdAt;
  final bool isRead;

  Message({
    required this.id,
    required this.conversationId,
    required this.senderId,
    required this.content,
    required this.messageType,
    required this.createdAt,
    this.isRead = false,
  });

  factory Message.fromJson(Map<String, dynamic> json) {
    return Message(
      id: json['id'],
      conversationId: json['conversationId'],
      senderId: json['senderId'],
      content: json['content'],
      messageType: json['messageType'] ?? 'text',
      createdAt: DateTime.parse(json['createdAt']),
      isRead: json['isRead'] ?? false,
    );
  }
}

class AppNotification {
  final String id;
  final String title;
  final String body;
  final String type;
  final Map<String, dynamic>? data;
  final bool isRead;
  final DateTime createdAt;

  AppNotification({
    required this.id,
    required this.title,
    required this.body,
    required this.type,
    this.data,
    required this.isRead,
    required this.createdAt,
  });

  factory AppNotification.fromJson(Map<String, dynamic> json) {
    return AppNotification(
      id: json['id'],
      title: json['title'],
      body: json['body'],
      type: json['type'],
      data: json['data'],
      isRead: json['isRead'] ?? false,
      createdAt: DateTime.parse(json['createdAt']),
    );
  }

  String get timeAgo {
    final diff = DateTime.now().difference(createdAt);
    if (diff.inDays > 0) return '${diff.inDays}d ago';
    if (diff.inHours > 0) return '${diff.inHours}h ago';
    if (diff.inMinutes > 0) return '${diff.inMinutes}m ago';
    return 'Just now';
  }
}

class Application {
  final String id;
  final String listingId;
  final String applicantId;
  final String status;
  final String? coverMessage;
  final double? proposedRate;
  final String? ratePeriod;
  final DateTime createdAt;
  final ApplicationListing? listing;

  Application({
    required this.id,
    required this.listingId,
    required this.applicantId,
    required this.status,
    this.coverMessage,
    this.proposedRate,
    this.ratePeriod,
    required this.createdAt,
    this.listing,
  });

  factory Application.fromJson(Map<String, dynamic> json) {
    return Application(
      id: json['id'],
      listingId: json['listingId'],
      applicantId: json['applicantId'],
      status: json['status'],
      coverMessage: json['coverMessage'],
      proposedRate: _toDouble(json['proposedRate']),
      ratePeriod: json['ratePeriod'],
      createdAt: DateTime.parse(json['createdAt']),
      listing: json['listing'] != null
          ? ApplicationListing.fromJson(json['listing'])
          : null,
    );
  }
}

class ApplicationListing {
  final String id;
  final String title;
  final String? categoryName;

  ApplicationListing({required this.id, required this.title, this.categoryName});

  factory ApplicationListing.fromJson(Map<String, dynamic> json) {
    return ApplicationListing(
      id: json['id'],
      title: json['title'],
      categoryName: json['category']?['name'],
    );
  }
}

class Review {
  final String id;
  final int rating;
  final String? comment;
  final String reviewerId;
  final String revieweeId;
  final DateTime createdAt;
  final String? reviewerName;
  final String? reviewerAvatar;

  Review({
    required this.id,
    required this.rating,
    this.comment,
    required this.reviewerId,
    required this.revieweeId,
    required this.createdAt,
    this.reviewerName,
    this.reviewerAvatar,
  });

  factory Review.fromJson(Map<String, dynamic> json) {
    return Review(
      id: json['id'],
      rating: json['rating'],
      comment: json['comment'],
      reviewerId: json['reviewerId'],
      revieweeId: json['revieweeId'],
      createdAt: DateTime.parse(json['createdAt']),
      reviewerName: json['reviewer']?['profile']?['displayName'],
      reviewerAvatar: json['reviewer']?['profile']?['avatarUrl'],
    );
  }
}
