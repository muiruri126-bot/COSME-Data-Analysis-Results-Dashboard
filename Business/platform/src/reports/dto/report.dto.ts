import { IsString, IsOptional, IsEnum } from 'class-validator';
import { ReportReason } from '@prisma/client';

export class CreateReportDto {
  @IsOptional()
  @IsString()
  reportedUserId?: string;

  @IsOptional()
  @IsString()
  reportedListingId?: string;

  @IsEnum(ReportReason)
  reason: ReportReason;

  @IsString()
  description: string;
}
