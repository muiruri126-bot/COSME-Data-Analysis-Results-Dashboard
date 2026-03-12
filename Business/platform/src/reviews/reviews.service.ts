import {
  Injectable,
  NotFoundException,
  ForbiddenException,
  ConflictException,
} from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { CreateReviewDto } from './dto/review.dto';
import { Decimal } from '@prisma/client/runtime/library';

@Injectable()
export class ReviewsService {
  constructor(private prisma: PrismaService) {}

  async create(reviewerId: string, dto: CreateReviewDto) {
    // Verify the listing exists
    const listing = await this.prisma.listing.findUnique({
      where: { id: dto.listingId },
    });

    if (!listing) {
      throw new NotFoundException('Listing not found');
    }

    // Verify reviewer was involved in the listing
    const isListerOrApplicant =
      listing.userId === reviewerId ||
      (await this.prisma.application.findFirst({
        where: {
          listingId: dto.listingId,
          applicantId: reviewerId,
          status: 'accepted',
        },
      }));

    if (!isListerOrApplicant) {
      throw new ForbiddenException(
        'You can only review users you have engaged with through a listing',
      );
    }

    if (reviewerId === dto.revieweeId) {
      throw new ForbiddenException('You cannot review yourself');
    }

    // Check for existing review
    const existing = await this.prisma.review.findUnique({
      where: {
        listingId_reviewerId_revieweeId: {
          listingId: dto.listingId,
          reviewerId,
          revieweeId: dto.revieweeId,
        },
      },
    });

    if (existing) {
      throw new ConflictException('You have already reviewed this user for this listing');
    }

    const review = await this.prisma.review.create({
      data: {
        listingId: dto.listingId,
        reviewerId,
        revieweeId: dto.revieweeId,
        rating: dto.rating,
        comment: dto.comment,
      },
    });

    // Update reviewee's average rating
    const stats = await this.prisma.review.aggregate({
      where: { revieweeId: dto.revieweeId, isVisible: true },
      _avg: { rating: true },
      _count: { rating: true },
    });

    await this.prisma.profile.update({
      where: { userId: dto.revieweeId },
      data: {
        averageRating: new Decimal(stats._avg.rating || 0).toDecimalPlaces(1),
        totalReviews: stats._count.rating,
      },
    });

    return review;
  }

  async getForUser(userId: string, page = 1, limit = 10) {
    const skip = (page - 1) * limit;

    const [reviews, total] = await Promise.all([
      this.prisma.review.findMany({
        where: { revieweeId: userId, isVisible: true },
        include: {
          reviewer: {
            select: {
              profile: { select: { displayName: true, avatarUrl: true } },
            },
          },
          listing: {
            select: {
              title: true,
              category: { select: { name: true } },
            },
          },
        },
        orderBy: { createdAt: 'desc' },
        skip,
        take: limit,
      }),
      this.prisma.review.count({
        where: { revieweeId: userId, isVisible: true },
      }),
    ]);

    return {
      data: reviews,
      meta: { total, page, limit, totalPages: Math.ceil(total / limit) },
    };
  }
}
