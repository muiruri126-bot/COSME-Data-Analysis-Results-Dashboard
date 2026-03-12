import { IsString, IsOptional, IsNumber, IsEnum } from 'class-validator';
import { BudgetPeriod, ApplicationStatus } from '@prisma/client';

export class CreateApplicationDto {
  @IsString()
  listingId: string;

  @IsOptional()
  @IsString()
  coverMessage?: string;

  @IsOptional()
  @IsNumber()
  proposedRate?: number;

  @IsOptional()
  @IsEnum(BudgetPeriod)
  ratePeriod?: BudgetPeriod;
}

export class UpdateApplicationStatusDto {
  @IsEnum(ApplicationStatus)
  status: ApplicationStatus;
}
