import {
  Controller,
  Get,
  Post,
  Param,
  Body,
  Query,
  UseGuards,
} from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';
import { ChatService } from './chat.service';
import { CreateConversationDto, SendMessageDto } from './dto/chat.dto';
import { CurrentUser } from '../common/decorators';

@Controller('chat')
@UseGuards(AuthGuard('jwt'))
export class ChatController {
  constructor(private chatService: ChatService) {}

  @Post('conversations')
  createConversation(
    @CurrentUser('id') userId: string,
    @Body() dto: CreateConversationDto,
  ) {
    return this.chatService.createConversation(userId, dto);
  }

  @Get('conversations')
  getConversations(@CurrentUser('id') userId: string) {
    return this.chatService.getConversations(userId);
  }

  @Get('conversations/:id/messages')
  getMessages(
    @CurrentUser('id') userId: string,
    @Param('id') conversationId: string,
    @Query('page') page?: number,
    @Query('limit') limit?: number,
  ) {
    return this.chatService.getMessages(userId, conversationId, page, limit);
  }

  @Post('messages')
  sendMessage(@CurrentUser('id') userId: string, @Body() dto: SendMessageDto) {
    return this.chatService.sendMessage(userId, dto);
  }
}
