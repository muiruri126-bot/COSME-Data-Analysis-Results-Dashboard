import { IsString, IsEnum, IsOptional } from 'class-validator';
import { VerificationType } from '@prisma/client';

export class SubmitVerificationDto {
  @IsEnum(VerificationType)
  type: VerificationType;

  @IsOptional()
  @IsString()
  documentUrl?: string;
}
