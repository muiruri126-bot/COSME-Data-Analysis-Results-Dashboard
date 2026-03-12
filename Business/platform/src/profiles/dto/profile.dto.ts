import {
  IsString,
  IsOptional,
  IsBoolean,
  IsEnum,
  IsArray,
  ValidateNested,
  IsNumber,
  IsDateString,
  MaxLength,
} from 'class-validator';
import { Type } from 'class-transformer';
import { Gender, RoleType, Proficiency } from '@prisma/client';

export class LocationDto {
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

export class UserRoleDto {
  @IsString()
  categoryId: string;

  @IsEnum(RoleType)
  roleType: RoleType;
}

export class UserSkillDto {
  @IsString()
  skillId: string;

  @IsOptional()
  @IsNumber()
  yearsExperience?: number;

  @IsOptional()
  @IsEnum(Proficiency)
  proficiency?: Proficiency;
}

export class CreateProfileDto {
  @IsString()
  @MaxLength(100)
  firstName: string;

  @IsString()
  @MaxLength(100)
  lastName: string;

  @IsOptional()
  @IsString()
  @MaxLength(100)
  displayName?: string;

  @IsOptional()
  @IsString()
  bio?: string;

  @IsOptional()
  @IsString()
  avatarUrl?: string;

  @IsOptional()
  @IsDateString()
  dateOfBirth?: string;

  @IsOptional()
  @IsEnum(Gender)
  gender?: Gender;

  @ValidateNested()
  @Type(() => LocationDto)
  location: LocationDto;

  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => UserRoleDto)
  roles: UserRoleDto[];

  @IsOptional()
  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => UserSkillDto)
  skills?: UserSkillDto[];

  @IsOptional()
  @IsBoolean()
  isAvailable?: boolean;

  @IsOptional()
  @IsString()
  @MaxLength(500)
  availabilityNote?: string;
}

export class UpdateProfileDto {
  @IsOptional()
  @IsString()
  @MaxLength(100)
  firstName?: string;

  @IsOptional()
  @IsString()
  @MaxLength(100)
  lastName?: string;

  @IsOptional()
  @IsString()
  @MaxLength(100)
  displayName?: string;

  @IsOptional()
  @IsString()
  bio?: string;

  @IsOptional()
  @IsString()
  avatarUrl?: string;

  @IsOptional()
  @IsDateString()
  dateOfBirth?: string;

  @IsOptional()
  @IsEnum(Gender)
  gender?: Gender;

  @IsOptional()
  @ValidateNested()
  @Type(() => LocationDto)
  location?: LocationDto;

  @IsOptional()
  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => UserRoleDto)
  roles?: UserRoleDto[];

  @IsOptional()
  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => UserSkillDto)
  skills?: UserSkillDto[];

  @IsOptional()
  @IsBoolean()
  isAvailable?: boolean;

  @IsOptional()
  @IsString()
  @MaxLength(500)
  availabilityNote?: string;
}
