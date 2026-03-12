import { IsEnum, IsOptional, IsString } from 'class-validator';

export enum UploadType {
  PROFILE_PHOTO = 'profile_photo',
  LISTING_IMAGE = 'listing_image',
  VERIFICATION_DOC = 'verification_doc',
  CHAT_ATTACHMENT = 'chat_attachment',
}

export class UploadFileDto {
  @IsEnum(UploadType)
  type: UploadType;

  @IsOptional()
  @IsString()
  entityId?: string;
}
