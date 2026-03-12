import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { UserStatus, ListingStatus } from '@prisma/client';

@Injectable()
export class AdminService {
  constructor(private prisma: PrismaService) {}

  // ─── Users Management ───

  async getUsers(page = 1, limit = 20, search?: string) {
    const skip = (page - 1) * limit;
    const where = search
      ? {
          OR: [
            { phone: { contains: search } },
            { email: { contains: search, mode: 'insensitive' as const } },
            {
              profile: {
                displayName: {
                  contains: search,
                  mode: 'insensitive' as const,
                },
              },
            },
          ],
        }
      : {};

    const [users, total] = await Promise.all([
      this.prisma.user.findMany({
        where,
        select: {
          id: true,
          phone: true,
          email: true,
          status: true,
          isVerified: true,
          createdAt: true,
          lastLoginAt: true,
          profile: {
            select: {
              displayName: true,
              avatarUrl: true,
              averageRating: true,
              totalReviews: true,
            },
          },
          roles: {
            select: {
              roleType: true,
              category: { select: { name: true, slug: true } },
            },
          },
        },
        orderBy: { createdAt: 'desc' },
        skip,
        take: limit,
      }),
      this.prisma.user.count({ where }),
    ]);

    return {
      data: users,
      meta: { total, page, limit, totalPages: Math.ceil(total / limit) },
    };
  }

  async getUserDetail(userId: string) {
    const user = await this.prisma.user.findUnique({
      where: { id: userId },
      include: {
        profile: { include: { location: true } },
        roles: { include: { category: true } },
        skills: { include: { skill: true } },
        verifications: true,
        listings: {
          orderBy: { createdAt: 'desc' },
          take: 10,
          select: { id: true, title: true, status: true, createdAt: true },
        },
        reviewsReceived: {
          orderBy: { createdAt: 'desc' },
          take: 5,
          select: { rating: true, comment: true, createdAt: true },
        },
        reportsFiled: { select: { id: true, reason: true, status: true } },
        reportsReceived: { select: { id: true, reason: true, status: true } },
      },
    });
    if (!user) throw new NotFoundException('User not found');
    return user;
  }

  async updateUserStatus(userId: string, status: UserStatus) {
    return this.prisma.user.update({
      where: { id: userId },
      data: { status },
      select: { id: true, phone: true, status: true },
    });
  }

  // ─── Listings Moderation ───

  async getListingsForModeration(page = 1, limit = 20, status?: ListingStatus) {
    const skip = (page - 1) * limit;
    const where = status ? { status } : {};

    const [listings, total] = await Promise.all([
      this.prisma.listing.findMany({
        where,
        include: {
          user: {
            select: {
              id: true,
              phone: true,
              profile: { select: { displayName: true } },
            },
          },
          category: { select: { name: true, slug: true } },
        },
        orderBy: { createdAt: 'desc' },
        skip,
        take: limit,
      }),
      this.prisma.listing.count({ where }),
    ]);

    return {
      data: listings,
      meta: { total, page, limit, totalPages: Math.ceil(total / limit) },
    };
  }

  async updateListingStatus(listingId: string, status: ListingStatus) {
    return this.prisma.listing.update({
      where: { id: listingId },
      data: { status },
      select: { id: true, title: true, status: true },
    });
  }

  // ─── Category Management ───

  async createCategory(data: {
    name: string;
    slug: string;
    listingType: 'job' | 'rental' | 'service_request' | 'space' | 'offer';
    description?: string;
    parentId?: string;
    iconUrl?: string;
    attributeSchema?: any;
    sortOrder?: number;
  }) {
    return this.prisma.serviceCategory.create({ data });
  }

  async updateCategory(
    id: string,
    data: {
      name?: string;
      description?: string;
      iconUrl?: string;
      isActive?: boolean;
      attributeSchema?: any;
      sortOrder?: number;
    },
  ) {
    return this.prisma.serviceCategory.update({
      where: { id },
      data,
    });
  }

  async deleteCategory(id: string) {
    // Soft-delete: deactivate instead of hard deleting
    return this.prisma.serviceCategory.update({
      where: { id },
      data: { isActive: false },
    });
  }

  // ─── Verification Queue ───

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
              profile: { select: { displayName: true, firstName: true, lastName: true } },
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

  // ─── Reports Queue ───

  async getPendingReports(page = 1, limit = 20) {
    const skip = (page - 1) * limit;
    const [reports, total] = await Promise.all([
      this.prisma.report.findMany({
        where: { status: { in: ['pending', 'investigating'] } },
        include: {
          reporter: {
            select: {
              id: true,
              profile: { select: { displayName: true } },
            },
          },
          reportedUser: {
            select: {
              id: true,
              profile: { select: { displayName: true } },
            },
          },
        },
        orderBy: { createdAt: 'asc' },
        skip,
        take: limit,
      }),
      this.prisma.report.count({
        where: { status: { in: ['pending', 'investigating'] } },
      }),
    ]);

    return {
      data: reports,
      meta: { total, page, limit, totalPages: Math.ceil(total / limit) },
    };
  }

  // ─── Analytics / Dashboard ───

  async getDashboardStats() {
    const [
      totalUsers,
      activeUsers,
      totalListings,
      activeListings,
      totalApplications,
      totalReviews,
      pendingVerifications,
      pendingReports,
    ] = await Promise.all([
      this.prisma.user.count(),
      this.prisma.user.count({ where: { status: 'active' } }),
      this.prisma.listing.count(),
      this.prisma.listing.count({ where: { status: 'active' } }),
      this.prisma.application.count(),
      this.prisma.review.count(),
      this.prisma.verification.count({ where: { status: 'pending' } }),
      this.prisma.report.count({
        where: { status: { in: ['pending', 'investigating'] } },
      }),
    ]);

    // New users in last 30 days
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    const newUsersLast30Days = await this.prisma.user.count({
      where: { createdAt: { gte: thirtyDaysAgo } },
    });

    // Listings per category
    const listingsPerCategory = await this.prisma.listing.groupBy({
      by: ['categoryId'],
      _count: { id: true },
      where: { status: 'active' },
    });

    return {
      totalUsers,
      activeUsers,
      newUsersLast30Days,
      totalListings,
      activeListings,
      totalApplications,
      totalReviews,
      pendingVerifications,
      pendingReports,
      listingsPerCategory,
    };
  }
}
