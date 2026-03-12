import { Injectable, ConflictException, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { SubmitVerificationDto } from './dto/verification.dto';
import { VerificationStatus } from '@prisma/client';

@Injectable()
export class VerificationService {
  constructor(private prisma: PrismaService) {}

  async submit(userId: string, dto: SubmitVerificationDto) {
    // Check for existing pending verification of same type
    const existing = await this.prisma.verification.findFirst({
      where: {
        userId,
        type: dto.type,
        status: { in: ['pending', 'verified'] },
      },
    });

    if (existing?.status === 'verified') {
      throw new ConflictException('This verification type is already verified');
    }

    if (existing?.status === 'pending') {
      throw new ConflictException('You already have a pending verification of this type');
    }

    return this.prisma.verification.create({
      data: {
        userId,
        type: dto.type,
        documentUrl: dto.documentUrl,
        status: 'pending',
      },
    });
  }

  async getUserVerifications(userId: string) {
    return this.prisma.verification.findMany({
      where: { userId },
      orderBy: { createdAt: 'desc' },
    });
  }

  // Admin methods
  async getPendingVerifications(page = 1, limit = 20) {
    const skip = (page - 1) * limit;

    const [verifications, total] = await Promise.all([
      this.prisma.verification.findMany({
        where: { status: 'pending' },
        include: {
          user: {
            select: {
              id: true,
              phone: true,
              profile: {
                select: { firstName: true, lastName: true, displayName: true },
              },
            },
          },
        },
        orderBy: { createdAt: 'asc' },
        skip,
        take: limit,
      }),
      this.prisma.verification.count({ where: { status: 'pending' } }),
    ]);

    return {
      data: verifications,
      meta: { total, page, limit, totalPages: Math.ceil(total / limit) },
    };
  }

  async processVerification(
    verificationId: string,
    adminId: string,
    status: 'verified' | 'rejected',
    notes?: string,
  ) {
    const verification = await this.prisma.verification.findUnique({
      where: { id: verificationId },
    });

    if (!verification) {
      throw new NotFoundException('Verification not found');
    }

    const updated = await this.prisma.verification.update({
      where: { id: verificationId },
      data: {
        status: status as VerificationStatus,
        verifiedBy: adminId,
        verifiedAt: new Date(),
        notes,
      },
    });

    // If ID verification is approved, mark user as verified
    if (status === 'verified' && verification.type === 'national_id') {
      await this.prisma.user.update({
        where: { id: verification.userId },
        data: { isVerified: true },
      });
    }

    return updated;
  }
}
