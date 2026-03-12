import {
  IsString,
  IsOptional,
  IsEnum,
  IsNumber,
  IsBoolean,
  IsArray,
  IsDateString,
  MaxLength,
  ValidateNested,
  IsObject,
} from 'class-validator';
import { Type } from 'class-transformer';
import { ListingType, BudgetPeriod, EngagementType } from '@prisma/client';

export class CreateListingLocationDto {
  @IsString()
  county: string;

  @IsOptional()
  @IsString()
  subCounty?: string;

  @IsOptional()
  @IsString()
  town?: string;

  @IsOptional()
  @IsString()
  estateArea?: string;

  @IsOptional()
  @IsString()
  fullAddress?: string;

  @IsNumber()
  latitude: number;

  @IsNumber()
  longitude: number;
}

export class CreateListingDto {
  @IsString()
  categoryId: string;

  @IsString()
  @MaxLength(200)
  title: string;

  @IsString()
  description: string;

  @IsEnum(ListingType)
  listingType: ListingType;

  @ValidateNested()
  @Type(() => CreateListingLocationDto)
  location: CreateListingLocationDto;

  @IsOptional()
  @IsObject()
  attributes?: Record<string, any>;

  @IsOptional()
  @IsNumber()
  budgetMin?: number;

  @IsOptional()
  @IsNumber()
  budgetMax?: number;

  @IsOptional()
  @IsEnum(BudgetPeriod)
  budgetPeriod?: BudgetPeriod;

  @IsOptional()
  @IsString()
  currency?: string;

  @IsOptional()
  @IsDateString()
  availabilityStart?: string;

  @IsOptional()
  @IsDateString()
  availabilityEnd?: string;

  @IsOptional()
  @IsEnum(EngagementType)
  engagementType?: EngagementType;

  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  images?: string[];
}

export class UpdateListingDto {
  @IsOptional()
  @IsString()
  @MaxLength(200)
  title?: string;

  @IsOptional()
  @IsString()
  description?: string;

  @IsOptional()
  @IsObject()
  attributes?: Record<string, any>;

  @IsOptional()
  @IsNumber()
  budgetMin?: number;

  @IsOptional()
  @IsNumber()
  budgetMax?: number;

  @IsOptional()
  @IsEnum(BudgetPeriod)
  budgetPeriod?: BudgetPeriod;

  @IsOptional()
  @IsDateString()
  availabilityStart?: string;

  @IsOptional()
  @IsDateString()
  availabilityEnd?: string;

  @IsOptional()
  @IsEnum(EngagementType)
  engagementType?: EngagementType;

  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  images?: string[];

  @IsOptional()
  @IsString()
  status?: string;
}

export class SearchListingsDto {
  @IsOptional()
  @IsString()
  categoryId?: string;

  @IsOptional()
  @IsString()
  categorySlug?: string;

  @IsOptional()
  @IsString()
  query?: string;

  @IsOptional()
  @IsNumber()
  @Type(() => Number)
  lat?: number;

  @IsOptional()
  @IsNumber()
  @Type(() => Number)
  lng?: number;

  @IsOptional()
  @IsNumber()
  @Type(() => Number)
  radiusKm?: number;

  @IsOptional()
  @IsString()
  county?: string;

  @IsOptional()
  @IsString()
  subCounty?: string;

  @IsOptional()
  @IsNumber()
  @Type(() => Number)
  budgetMin?: number;

  @IsOptional()
  @IsNumber()
  @Type(() => Number)
  budgetMax?: number;

  @IsOptional()
  @IsEnum(EngagementType)
  engagementType?: EngagementType;

  @IsOptional()
  @IsEnum(ListingType)
  listingType?: ListingType;

  @IsOptional()
  @IsString()
  sortBy?: 'recent' | 'rating' | 'price_low' | 'price_high';

  @IsOptional()
  @IsNumber()
  @Type(() => Number)
  page?: number;

  @IsOptional()
  @IsNumber()
  @Type(() => Number)
  limit?: number;
}
