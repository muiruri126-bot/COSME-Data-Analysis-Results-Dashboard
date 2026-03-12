import {
  Injectable,
  NotFoundException,
  ForbiddenException,
  ConflictException,
} from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { CreateApplicationDto, UpdateApplicationStatusDto } from './dto/application.dto';

@Injectable()
export class ApplicationsService {
  constructor(private prisma: PrismaService) {}

  async create(applicantId: string, dto: CreateApplicationDto) {
    const listing = await this.prisma.listing.findUnique({
      where: { id: dto.listingId },
    });

    if (!listing) {
      throw new NotFoundException('Listing not found');
    }

    if (listing.status !== 'active') {
      throw new ConflictException('Listing is no longer accepting applications');
    }

    if (listing.userId === applicantId) {
      throw new ForbiddenException('You cannot apply to your own listing');
    }

    const existing = await this.prisma.application.findUnique({
      where: {
        listingId_applicantId: {
          listingId: dto.listingId,
          applicantId,
        },
      },
    });

    if (existing) {
      throw new ConflictException('You have already applied to this listing');
    }

    const application = await this.prisma.application.create({
      data: {
        listingId: dto.listingId,
        applicantId,
        coverMessage: dto.coverMessage,
        proposedRate: dto.proposedRate,
        ratePeriod: dto.ratePeriod,
      },
    });

    // Increment application count on listing
    await this.prisma.listing.update({
      where: { id: dto.listingId },
      data: { applicationCount: { increment: 1 } },
    });

    return application;
  }

  async getForListing(listingId: string, userId: string) {
    // Verify the listing belongs to the user
    const listing = await this.prisma.listing.findUnique({
      where: { id: listingId },
    });

    if (!listing) {
      throw new NotFoundException('Listing not found');
    }

    if (listing.userId !== userId) {
      throw new ForbiddenException('You can only view applications for your own listings');
    }

    return this.prisma.application.findMany({
      where: { listingId },
      include: {
        applicant: {
          select: {
            id: true,
            isVerified: true,
            profile: {
              select: {
                displayName: true,
                firstName: true,
                avatarUrl: true,
                averageRating: true,
                totalReviews: true,
                totalCompletedJobs: true,
                isAvailable: true,
              },
            },
            skills: {
              include: { skill: { select: { name: true } } },
            },
            verifications: {
              where: { status: 'verified' },
              select: { type: true },
            },
          },
        },
      },
      orderBy: { createdAt: 'desc' },
    });
  }

  async getMyApplications(applicantId: string) {
    return this.prisma.application.findMany({
      where: { applicantId },
      include: {
        listing: {
          select: {
            id: true,
            title: true,
            status: true,
            budgetMin: true,
            budgetMax: true,
            budgetPeriod: true,
            category: { select: { name: true, slug: true } },
            location: {
              select: { county: true, subCounty: true, estateArea: true },
            },
            user: {
              select: {
                profile: { select: { displayName: true } },
              },
            },
          },
        },
      },
      orderBy: { createdAt: 'desc' },
    });
  }

  async updateStatus(
    applicationId: string,
    userId: string,
    dto: UpdateApplicationStatusDto,
  ) {
    const application = await this.prisma.application.findUnique({
      where: { id: applicationId },
      include: { listing: true },
    });

    if (!application) {
      throw new NotFoundException('Application not found');
    }

    // Listing owner can accept/reject/shortlist; applicant can withdraw
    if (dto.status === 'withdrawn') {
      if (application.applicantId !== userId) {
        throw new ForbiddenException('Only the applicant can withdraw');
      }
    } else {
      if (application.listing.userId !== userId) {
        throw new ForbiddenException('Only the listing owner can update application status');
      }
    }

    const updated = await this.prisma.application.update({
      where: { id: applicationId },
      data: { status: dto.status },
    });

    // If accepted, update listing status and provider stats
    if (dto.status === 'accepted') {
      await this.prisma.listing.update({
        where: { id: application.listingId },
        data: { status: 'filled' },
      });

      await this.prisma.profile.update({
        where: { userId: application.applicantId },
        data: { totalCompletedJobs: { increment: 1 } },
      });
    }

    return updated;
  }
}
