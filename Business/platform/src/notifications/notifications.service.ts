import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { NotificationType } from '@prisma/client';

@Injectable()
export class NotificationsService {
  constructor(private prisma: PrismaService) {}

  async send(
    userId: string,
    type: NotificationType,
    title: string,
    body: string,
    data?: Record<string, any>,
  ) {
    const notification = await this.prisma.notification.create({
      data: {
        userId,
        type,
        title,
        body,
        data: data ?? undefined,
        sentAt: new Date(),
      },
    });

    // Channel dispatch based on type
    switch (type) {
      case 'push':
        await this.sendPush(userId, title, body, data);
        break;
      case 'sms':
        await this.sendSms(userId, body);
        break;
      case 'in_app':
        // Already stored in DB — clients pull or receive via WebSocket
        break;
      // email and whatsapp channels added in Phase 2
    }

    return notification;
  }

  async getUserNotifications(userId: string, page = 1, limit = 20) {
    const skip = (page - 1) * limit;

    const [notifications, total] = await Promise.all([
      this.prisma.notification.findMany({
        where: { userId },
        orderBy: { createdAt: 'desc' },
        skip,
        take: limit,
      }),
      this.prisma.notification.count({ where: { userId } }),
    ]);

    return {
      data: notifications,
      meta: { total, page, limit, totalPages: Math.ceil(total / limit) },
    };
  }

  async markAsRead(userId: string, notificationId: string) {
    return this.prisma.notification.updateMany({
      where: { id: notificationId, userId },
      data: { isRead: true },
    });
  }

  async markAllAsRead(userId: string) {
    return this.prisma.notification.updateMany({
      where: { userId, isRead: false },
      data: { isRead: true },
    });
  }

  async getUnreadCount(userId: string) {
    const count = await this.prisma.notification.count({
      where: { userId, isRead: false },
    });
    return { unreadCount: count };
  }

  // ── Channel implementations ──

  private async sendPush(
    userId: string,
    title: string,
    body: string,
    data?: Record<string, any>,
  ) {
    // TODO: Integrate Firebase Cloud Messaging
    // 1. Look up user's FCM token from a device_tokens table
    // 2. Send push via firebase-admin SDK
    console.log(`[PUSH] To ${userId}: ${title} - ${body}`);
  }

  private async sendSms(userId: string, message: string) {
    // TODO: Integrate Africa's Talking SMS API
    // 1. Look up user's phone number
    // 2. Send via Africa's Talking SDK
    const user = await this.prisma.user.findUnique({
      where: { id: userId },
      select: { phone: true },
    });
    console.log(`[SMS] To ${user?.phone}: ${message}`);
  }
}
