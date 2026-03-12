import {
  Injectable,
  NotFoundException,
  ForbiddenException,
} from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { CreateConversationDto, SendMessageDto } from './dto/chat.dto';

@Injectable()
export class ChatService {
  constructor(private prisma: PrismaService) {}

  async createConversation(userId: string, dto: CreateConversationDto) {
    // Check if a conversation already exists between these users for this listing
    const existing = await this.prisma.conversation.findFirst({
      where: {
        listingId: dto.listingId || null,
        AND: [
          { participants: { some: { userId } } },
          { participants: { some: { userId: dto.participantId } } },
        ],
      },
      include: {
        participants: { select: { userId: true } },
        messages: { take: 1, orderBy: { createdAt: 'desc' } },
      },
    });

    if (existing) {
      return existing;
    }

    const conversation = await this.prisma.conversation.create({
      data: {
        listingId: dto.listingId,
        participants: {
          create: [{ userId }, { userId: dto.participantId }],
        },
        ...(dto.initialMessage && {
          messages: {
            create: {
              senderId: userId,
              content: dto.initialMessage,
              messageType: 'text',
            },
          },
        }),
      },
      include: {
        participants: {
          include: {
            user: {
              select: {
                id: true,
                profile: { select: { displayName: true, avatarUrl: true } },
              },
            },
          },
        },
        listing: {
          select: { id: true, title: true, category: { select: { name: true } } },
        },
      },
    });

    return conversation;
  }

  async sendMessage(userId: string, dto: SendMessageDto) {
    // Verify user is a participant
    const participant = await this.prisma.conversationParticipant.findUnique({
      where: {
        conversationId_userId: {
          conversationId: dto.conversationId,
          userId,
        },
      },
    });

    if (!participant) {
      throw new ForbiddenException('You are not a participant in this conversation');
    }

    const message = await this.prisma.message.create({
      data: {
        conversationId: dto.conversationId,
        senderId: userId,
        content: dto.content,
        messageType: dto.messageType || 'text',
        attachmentUrl: dto.attachmentUrl,
      },
      include: {
        sender: {
          select: {
            id: true,
            profile: { select: { displayName: true, avatarUrl: true } },
          },
        },
      },
    });

    // Update conversation timestamp
    await this.prisma.conversation.update({
      where: { id: dto.conversationId },
      data: { updatedAt: new Date() },
    });

    return message;
  }

  async getConversations(userId: string) {
    return this.prisma.conversation.findMany({
      where: {
        participants: { some: { userId } },
        status: 'active',
      },
      include: {
        participants: {
          include: {
            user: {
              select: {
                id: true,
                profile: { select: { displayName: true, avatarUrl: true } },
              },
            },
          },
        },
        listing: {
          select: { id: true, title: true, category: { select: { name: true } } },
        },
        messages: {
          take: 1,
          orderBy: { createdAt: 'desc' },
          select: { content: true, createdAt: true, senderId: true },
        },
      },
      orderBy: { updatedAt: 'desc' },
    });
  }

  async getMessages(userId: string, conversationId: string, page = 1, limit = 50) {
    // Verify participation
    const participant = await this.prisma.conversationParticipant.findUnique({
      where: {
        conversationId_userId: { conversationId, userId },
      },
    });

    if (!participant) {
      throw new ForbiddenException('You are not a participant in this conversation');
    }

    const skip = (page - 1) * limit;

    const [messages, total] = await Promise.all([
      this.prisma.message.findMany({
        where: { conversationId },
        include: {
          sender: {
            select: {
              id: true,
              profile: { select: { displayName: true, avatarUrl: true } },
            },
          },
        },
        orderBy: { createdAt: 'desc' },
        skip,
        take: limit,
      }),
      this.prisma.message.count({ where: { conversationId } }),
    ]);

    // Mark messages as read
    await this.prisma.message.updateMany({
      where: {
        conversationId,
        senderId: { not: userId },
        isRead: false,
      },
      data: { isRead: true },
    });

    // Update last read timestamp
    await this.prisma.conversationParticipant.update({
      where: { conversationId_userId: { conversationId, userId } },
      data: { lastReadAt: new Date() },
    });

    return {
      data: messages,
      meta: { total, page, limit, totalPages: Math.ceil(total / limit) },
    };
  }
}
