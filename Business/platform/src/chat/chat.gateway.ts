import {
  WebSocketGateway,
  WebSocketServer,
  SubscribeMessage,
  ConnectedSocket,
  MessageBody,
  OnGatewayConnection,
  OnGatewayDisconnect,
} from '@nestjs/websockets';
import { Server, Socket } from 'socket.io';
import { ChatService } from './chat.service';
import { JwtService } from '@nestjs/jwt';
import { ConfigService } from '@nestjs/config';

@WebSocketGateway({
  cors: { origin: '*' },
  namespace: '/chat',
})
export class ChatGateway implements OnGatewayConnection, OnGatewayDisconnect {
  @WebSocketServer()
  server: Server;

  private userSockets = new Map<string, string[]>();

  constructor(
    private chatService: ChatService,
    private jwt: JwtService,
    private config: ConfigService,
  ) {}

  async handleConnection(client: Socket) {
    try {
      const token = client.handshake.auth?.token || client.handshake.headers?.authorization?.replace('Bearer ', '');

      if (!token) {
        client.disconnect();
        return;
      }

      const payload = this.jwt.verify(token, {
        secret: this.config.get<string>('JWT_SECRET'),
      });

      const userId = payload.sub;
      client.data.userId = userId;

      // Track user's socket connections
      const sockets = this.userSockets.get(userId) || [];
      sockets.push(client.id);
      this.userSockets.set(userId, sockets);

      // Join user's conversation rooms
      const conversations = await this.chatService.getConversations(userId);
      for (const conv of conversations) {
        client.join(`conversation:${conv.id}`);
      }
    } catch {
      client.disconnect();
    }
  }

  handleDisconnect(client: Socket) {
    const userId = client.data.userId;
    if (userId) {
      const sockets = this.userSockets.get(userId) || [];
      const updated = sockets.filter((s) => s !== client.id);
      if (updated.length === 0) {
        this.userSockets.delete(userId);
      } else {
        this.userSockets.set(userId, updated);
      }
    }
  }

  @SubscribeMessage('sendMessage')
  async handleMessage(
    @ConnectedSocket() client: Socket,
    @MessageBody() data: { conversationId: string; content: string },
  ) {
    const userId = client.data.userId;
    if (!userId) return;

    const message = await this.chatService.sendMessage(userId, {
      conversationId: data.conversationId,
      content: data.content,
    });

    this.server
      .to(`conversation:${data.conversationId}`)
      .emit('newMessage', message);

    return message;
  }

  @SubscribeMessage('joinConversation')
  handleJoinConversation(
    @ConnectedSocket() client: Socket,
    @MessageBody() data: { conversationId: string },
  ) {
    client.join(`conversation:${data.conversationId}`);
  }

  @SubscribeMessage('markRead')
  async handleMarkRead(
    @ConnectedSocket() client: Socket,
    @MessageBody() data: { conversationId: string },
  ) {
    const userId = client.data.userId;
    if (!userId) return;

    await this.chatService.getMessages(userId, data.conversationId, 1, 1);

    this.server
      .to(`conversation:${data.conversationId}`)
      .emit('messagesRead', { conversationId: data.conversationId, userId });
  }
}
