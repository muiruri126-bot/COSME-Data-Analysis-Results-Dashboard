import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:platform_mobile/config/theme/app_theme.dart';
import 'package:platform_mobile/core/di/service_locator.dart';
import 'package:platform_mobile/features/chat/repository/chat_repository.dart';
import 'package:platform_mobile/shared/models/models.dart';

class ConversationsScreen extends StatefulWidget {
  const ConversationsScreen({super.key});

  @override
  State<ConversationsScreen> createState() => _ConversationsScreenState();
}

class _ConversationsScreenState extends State<ConversationsScreen> {
  late Future<List<Conversation>> _conversationsFuture;
  String? _currentUserId;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    _currentUserId = await sl<FlutterSecureStorage>().read(key: 'user_id');
    setState(() {
      _conversationsFuture = sl<ChatRepository>().getConversations();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Messages')),
      body: FutureBuilder<List<Conversation>>(
        future: _conversationsFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text('${snapshot.error}', style: const TextStyle(color: AppColors.error)),
                  const SizedBox(height: 16),
                  ElevatedButton(onPressed: _loadData, child: const Text('Retry')),
                ],
              ),
            );
          }

          final conversations = snapshot.data ?? [];
          if (conversations.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.chat_bubble_outline, size: 64, color: AppColors.textTertiary),
                  const SizedBox(height: 16),
                  Text(
                    'No messages yet',
                    style: TextStyle(color: AppColors.textSecondary, fontSize: 16),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Start a conversation from a listing',
                    style: TextStyle(color: AppColors.textTertiary),
                  ),
                ],
              ),
            );
          }

          return RefreshIndicator(
            onRefresh: () async => _loadData(),
            child: ListView.separated(
              itemCount: conversations.length,
              separatorBuilder: (_, __) => const Divider(height: 1, indent: 76),
              itemBuilder: (context, index) {
                final conv = conversations[index];
                final other = _currentUserId != null
                    ? conv.getOtherParticipant(_currentUserId!)
                    : null;
                return _ConversationTile(
                  conversation: conv,
                  otherParticipant: other,
                );
              },
            ),
          );
        },
      ),
    );
  }
}

class _ConversationTile extends StatelessWidget {
  final Conversation conversation;
  final ConversationParticipant? otherParticipant;

  const _ConversationTile({required this.conversation, this.otherParticipant});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 4),
      leading: CircleAvatar(
        radius: 24,
        backgroundColor: AppColors.surfaceVariant,
        backgroundImage: otherParticipant?.avatarUrl != null
            ? CachedNetworkImageProvider(otherParticipant!.avatarUrl!)
            : null,
        child: otherParticipant?.avatarUrl == null
            ? const Icon(Icons.person, color: AppColors.textTertiary)
            : null,
      ),
      title: Text(
        otherParticipant?.displayName ?? 'User',
        style: const TextStyle(fontWeight: FontWeight.w600),
      ),
      subtitle: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (conversation.listingTitle != null)
            Text(
              conversation.listingTitle!,
              style: TextStyle(fontSize: 12, color: AppColors.primary),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          if (conversation.lastMessage != null)
            Text(
              conversation.lastMessage!.content,
              style: TextStyle(fontSize: 13, color: AppColors.textSecondary),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
        ],
      ),
      trailing: conversation.lastMessage != null
          ? Text(
              _timeAgo(conversation.lastMessage!.createdAt),
              style: TextStyle(fontSize: 11, color: AppColors.textTertiary),
            )
          : null,
      onTap: () => context.push('/chat/${conversation.id}'),
    );
  }

  String _timeAgo(DateTime date) {
    final diff = DateTime.now().difference(date);
    if (diff.inDays > 0) return '${diff.inDays}d';
    if (diff.inHours > 0) return '${diff.inHours}h';
    if (diff.inMinutes > 0) return '${diff.inMinutes}m';
    return 'now';
  }
}
