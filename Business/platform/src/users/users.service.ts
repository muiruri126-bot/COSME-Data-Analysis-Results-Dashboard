import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';

@Injectable()
export class UsersService {
  constructor(private prisma: PrismaService) {}

  async findById(id: string) {
    const user = await this.prisma.user.findUnique({
      where: { id },
      include: {
        profile: {
          include: { location: true },
        },
        roles: {
          include: { category: { select: { id: true, name: true, slug: true } } },
        },
        skills: {
          include: { skill: true },
        },
        verifications: {
          where: { status: 'verified' },
          select: { type: true, verifiedAt: true },
        },
      },
    });

    if (!user) {
      throw new NotFoundException('User not found');
    }

    return user;
  }

  async getPublicProfile(userId: string) {
    const user = await this.prisma.user.findUnique({
      where: { id: userId },
      select: {
        id: true,
        isVerified: true,
        createdAt: true,
        profile: {
          select: {
            displayName: true,
            firstName: true,
            lastName: true,
            bio: true,
            avatarUrl: true,
            averageRating: true,
            totalReviews: true,
            totalCompletedJobs: true,
            isAvailable: true,
            availabilityNote: true,
            location: {
              select: { county: true, subCounty: true, estateArea: true },
            },
          },
        },
        roles: {
          select: {
            roleType: true,
            category: { select: { name: true, slug: true } },
          },
        },
        skills: {
          include: { skill: { select: { name: true, slug: true } } },
        },
        verifications: {
          where: { status: 'verified' },
          select: { type: true },
        },
        reviewsReceived: {
          where: { isVisible: true },
          orderBy: { createdAt: 'desc' },
          take: 10,
          select: {
            rating: true,
            comment: true,
            createdAt: true,
            reviewer: {
              select: {
                profile: { select: { displayName: true, avatarUrl: true } },
              },
            },
          },
        },
      },
    });

    if (!user) {
      throw new NotFoundException('User not found');
    }

    return user;
  }

  async updateStatus(userId: string, status: 'active' | 'suspended' | 'deactivated') {
    return this.prisma.user.update({
      where: { id: userId },
      data: { status },
    });
  }
}
