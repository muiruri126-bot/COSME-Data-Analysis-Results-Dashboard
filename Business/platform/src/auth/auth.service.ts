import { Injectable, BadRequestException, UnauthorizedException } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { ConfigService } from '@nestjs/config';
import { randomInt } from 'crypto';
import { PrismaService } from '../prisma/prisma.service';
import { RequestOtpDto, VerifyOtpDto } from './dto/auth.dto';

@Injectable()
export class AuthService {
  // In-memory OTP store for development. In production, use Redis with TTL.
  private otpStore = new Map<string, { otp: string; expiresAt: number }>();

  constructor(
    private prisma: PrismaService,
    private jwt: JwtService,
    private config: ConfigService,
  ) {}

  async requestOtp(dto: RequestOtpDto) {
    const otp = this.generateOtp();
    const expirySeconds = this.config.get<number>('OTP_EXPIRY_SECONDS', 300);

    this.otpStore.set(dto.phone, {
      otp,
      expiresAt: Date.now() + expirySeconds * 1000,
    });

    // In production: send OTP via Africa's Talking SMS or WhatsApp
    // For development, log it
    if (this.config.get('NODE_ENV') === 'development') {
      console.log(`\n========================================`);
      console.log(`  OTP for ${dto.phone}: ${otp}`);
      console.log(`========================================\n`);
    }

    // TODO: Integrate Africa's Talking SMS service
    // await this.smsService.send(dto.phone, `Your verification code is: ${otp}`);

    return {
      message: 'OTP sent successfully',
      expiresIn: expirySeconds,
      ...(this.config.get('NODE_ENV') === 'development' && { otp }),
    };
  }

  async verifyOtp(dto: VerifyOtpDto) {
    const stored = this.otpStore.get(dto.phone);

    if (!stored) {
      throw new BadRequestException('No OTP request found for this phone number');
    }

    if (Date.now() > stored.expiresAt) {
      this.otpStore.delete(dto.phone);
      throw new BadRequestException('OTP has expired. Please request a new one');
    }

    if (stored.otp !== dto.otp) {
      throw new BadRequestException('Invalid OTP');
    }

    this.otpStore.delete(dto.phone);

    // Find or create user
    let user = await this.prisma.user.findUnique({
      where: { phone: dto.phone },
    });

    let isNewUser = false;

    if (!user) {
      user = await this.prisma.user.create({
        data: {
          phone: dto.phone,
          status: 'pending_profile',
          isVerified: false,
        },
      });
      isNewUser = true;

      // Create phone verification record
      await this.prisma.verification.create({
        data: {
          userId: user.id,
          type: 'phone',
          status: 'verified',
          verifiedAt: new Date(),
        },
      });
    }

    // Update last login
    await this.prisma.user.update({
      where: { id: user.id },
      data: { lastLoginAt: new Date() },
    });

    const tokens = await this.generateTokens(user.id, user.phone);

    // Fetch full user data for the response
    const fullUser = await this.prisma.user.findUnique({
      where: { id: user.id },
      include: {
        profile: { include: { location: true } },
        roles: { select: { roleType: true, category: { select: { id: true, name: true, slug: true } } } },
      },
    });

    return {
      ...tokens,
      isNewUser,
      user: fullUser,
    };
  }

  async refreshToken(refreshToken: string) {
    try {
      const payload = this.jwt.verify(refreshToken, {
        secret: this.config.get<string>('JWT_REFRESH_SECRET'),
      });

      const user = await this.prisma.user.findUnique({
        where: { id: payload.sub },
      });

      if (!user || user.status === 'suspended' || user.status === 'deactivated') {
        throw new UnauthorizedException('Account is not accessible');
      }

      return this.generateTokens(user.id, user.phone);
    } catch {
      throw new UnauthorizedException('Invalid refresh token');
    }
  }

  private async generateTokens(userId: string, phone: string) {
    const payload = { sub: userId, phone };

    const [accessToken, refreshToken] = await Promise.all([
      this.jwt.signAsync(payload, {
        secret: this.config.get<string>('JWT_SECRET')!,
        expiresIn: this.config.get<string>('JWT_EXPIRES_IN', '15m') as any,
      }),
      this.jwt.signAsync(payload, {
        secret: this.config.get<string>('JWT_REFRESH_SECRET')!,
        expiresIn: this.config.get<string>('JWT_REFRESH_EXPIRES_IN', '30d') as any,
      }),
    ]);

    return { accessToken, refreshToken };
  }

  private generateOtp(): string {
    const length = this.config.get<number>('OTP_LENGTH', 6);
    const min = Math.pow(10, length - 1);
    const max = Math.pow(10, length) - 1;
    return randomInt(min, max + 1).toString();
  }
}
