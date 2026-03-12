import 'package:flutter/material.dart';
import 'package:platform_mobile/config/theme/app_theme.dart';
import 'package:platform_mobile/core/di/service_locator.dart';
import 'package:platform_mobile/features/notifications/repository/notifications_repository.dart';
import 'package:platform_mobile/shared/models/models.dart';

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  late Future<List<AppNotification>> _notificationsFuture;

  @override
  void initState() {
    super.initState();
    _notificationsFuture = sl<NotificationsRepository>().getAll();
  }

  void _refresh() {
    setState(() {
      _notificationsFuture = sl<NotificationsRepository>().getAll();
    });
  }

  Future<void> _markAllRead() async {
    try {
      await sl<NotificationsRepository>().markAllAsRead();
      _refresh();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('$e'), backgroundColor: AppColors.error),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Notifications'),
        actions: [
          TextButton(
            onPressed: _markAllRead,
            child: const Text('Mark all read'),
          ),
        ],
      ),
      body: FutureBuilder<List<AppNotification>>(
        future: _notificationsFuture,
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
                  ElevatedButton(onPressed: _refresh, child: const Text('Retry')),
                ],
              ),
            );
          }

          final notifications = snapshot.data ?? [];
          if (notifications.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.notifications_off_outlined,
                      size: 64, color: AppColors.textTertiary),
                  const SizedBox(height: 16),
                  Text(
                    'No notifications',
                    style: TextStyle(color: AppColors.textSecondary, fontSize: 16),
                  ),
                ],
              ),
            );
          }

          return RefreshIndicator(
            onRefresh: () async => _refresh(),
            child: ListView.separated(
              itemCount: notifications.length,
              separatorBuilder: (_, __) => const Divider(height: 1),
              itemBuilder: (context, index) {
                final notification = notifications[index];
                return _NotificationTile(
                  notification: notification,
                  onTap: () async {
                    if (!notification.isRead) {
                      await sl<NotificationsRepository>().markAsRead(notification.id);
                      _refresh();
                    }
                  },
                );
              },
            ),
          );
        },
      ),
    );
  }
}

class _NotificationTile extends StatelessWidget {
  final AppNotification notification;
  final VoidCallback onTap;

  const _NotificationTile({required this.notification, required this.onTap});

  IconData get _icon {
    switch (notification.type) {
      case 'application_received':
        return Icons.work_outline;
      case 'application_accepted':
        return Icons.check_circle_outline;
      case 'application_rejected':
        return Icons.cancel_outlined;
      case 'new_message':
        return Icons.chat_bubble_outline;
      case 'review_received':
        return Icons.star_outline;
      default:
        return Icons.notifications_outlined;
    }
  }

  @override
  Widget build(BuildContext context) {
    return ListTile(
      tileColor: notification.isRead ? null : AppColors.primaryLight.withValues(alpha: 0.05),
      contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
      leading: CircleAvatar(
        backgroundColor: AppColors.surfaceVariant,
        child: Icon(_icon, color: AppColors.primary, size: 20),
      ),
      title: Text(
        notification.title,
        style: TextStyle(
          fontWeight: notification.isRead ? FontWeight.normal : FontWeight.w600,
        ),
      ),
      subtitle: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 4),
          Text(
            notification.body,
            style: TextStyle(fontSize: 13, color: AppColors.textSecondary),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 4),
          Text(
            notification.timeAgo,
            style: TextStyle(fontSize: 11, color: AppColors.textTertiary),
          ),
        ],
      ),
      onTap: onTap,
    );
  }
}
