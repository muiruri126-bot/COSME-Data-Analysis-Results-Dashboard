import { IsString, IsNotEmpty, Length, Matches } from 'class-validator';

export class RequestOtpDto {
  @IsString()
  @IsNotEmpty()
  @Matches(/^\+?[1-9]\d{6,14}$/, {
    message: 'Phone number must be a valid international format (e.g., +254712345678)',
  })
  phone: string;
}

export class VerifyOtpDto {
  @IsString()
  @IsNotEmpty()
  @Matches(/^\+?[1-9]\d{6,14}$/, {
    message: 'Phone number must be a valid international format',
  })
  phone: string;

  @IsString()
  @IsNotEmpty()
  @Length(6, 6, { message: 'OTP must be exactly 6 digits' })
  @Matches(/^\d{6}$/, { message: 'OTP must contain only digits' })
  otp: string;
}

export class RefreshTokenDto {
  @IsString()
  @IsNotEmpty()
  refreshToken: string;
}
