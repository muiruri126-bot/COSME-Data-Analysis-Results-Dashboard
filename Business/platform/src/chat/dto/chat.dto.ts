import { IsString, IsOptional, IsEnum } from 'class-validator';
import { MessageType } from '@prisma/client';

export class CreateConversationDto {
  @IsString()
  participantId: string;

  @IsOptional()
  @IsString()
  listingId?: string;

  @IsOptional()
  @IsString()
  initialMessage?: string;
}

export class SendMessageDto {
  @IsString()
  conversationId: string;

  @IsString()
  content: string;

  @IsOptional()
  @IsEnum(MessageType)
  messageType?: MessageType;

  @IsOptional()
  @IsString()
  attachmentUrl?: string;
}
