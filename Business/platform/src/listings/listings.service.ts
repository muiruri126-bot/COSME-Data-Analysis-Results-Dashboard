import {
  Injectable,
  NotFoundException,
  ForbiddenException,
} from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { CreateListingDto, UpdateListingDto, SearchListingsDto } from './dto/listing.dto';
import { Prisma, ListingStatus } from '@prisma/client';

@Injectable()
export class ListingsService {
  constructor(private prisma: PrismaService) {}

  async create(userId: string, dto: CreateListingDto) {
    // Create location for this listing
    const location = await this.prisma.location.create({
      data: {
        county: dto.location.county,
        subCounty: dto.location.subCounty,
        town: dto.location.town,
        estateArea: dto.location.estateArea,
        fullAddress: dto.location.fullAddress,
        latitude: dto.location.latitude,
        longitude: dto.location.longitude,
      },
    });

    return this.prisma.listing.create({
      data: {
        userId,
        categoryId: dto.categoryId,
        title: dto.title,
        description: dto.description,
        listingType: dto.listingType,
        status: 'active',
        locationId: location.id,
        attributes: dto.attributes ?? Prisma.JsonNull,
        budgetMin: dto.budgetMin,
        budgetMax: dto.budgetMax,
        budgetPeriod: dto.budgetPeriod,
        currency: dto.currency || 'KES',
        availabilityStart: dto.availabilityStart
          ? new Date(dto.availabilityStart)
          : undefined,
        availabilityEnd: dto.availabilityEnd
          ? new Date(dto.availabilityEnd)
          : undefined,
        engagementType: dto.engagementType,
        images: dto.images ?? [],
      },
      include: {
        category: { select: { name: true, slug: true } },
        location: true,
        user: {
          select: {
            id: true,
            profile: {
              select: { displayName: true, avatarUrl: true, averageRating: true },
            },
          },
        },
      },
    });
  }

  async findById(id: string) {
    const listing = await this.prisma.listing.findUnique({
      where: { id },
      include: {
        category: true,
        location: true,
        user: {
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
              },
            },
            verifications: {
              where: { status: 'verified' },
              select: { type: true },
            },
          },
        },
      },
    });

    if (!listing) {
      throw new NotFoundException('Listing not found');
    }

    // Increment view count
    await this.prisma.listing.update({
      where: { id },
      data: { viewCount: { increment: 1 } },
    });

    return listing;
  }

  async update(userId: string, listingId: string, dto: UpdateListingDto) {
    const listing = await this.prisma.listing.findUnique({
      where: { id: listingId },
    });

    if (!listing) {
      throw new NotFoundException('Listing not found');
    }

    if (listing.userId !== userId) {
      throw new ForbiddenException('You can only edit your own listings');
    }

    return this.prisma.listing.update({
      where: { id: listingId },
      data: {
        title: dto.title,
        description: dto.description,
        attributes: dto.attributes,
        budgetMin: dto.budgetMin,
        budgetMax: dto.budgetMax,
        budgetPeriod: dto.budgetPeriod,
        availabilityStart: dto.availabilityStart
          ? new Date(dto.availabilityStart)
          : undefined,
        availabilityEnd: dto.availabilityEnd
          ? new Date(dto.availabilityEnd)
          : undefined,
        engagementType: dto.engagementType,
        images: dto.images,
        status: dto.status as ListingStatus,
      },
    });
  }

  async delete(userId: string, listingId: string) {
    const listing = await this.prisma.listing.findUnique({
      where: { id: listingId },
    });

    if (!listing) {
      throw new NotFoundException('Listing not found');
    }

    if (listing.userId !== userId) {
      throw new ForbiddenException('You can only delete your own listings');
    }

    return this.prisma.listing.update({
      where: { id: listingId },
      data: { status: 'removed' },
    });
  }

  async search(dto: SearchListingsDto) {
    const page = dto.page || 1;
    const limit = Math.min(dto.limit || 20, 50);
    const skip = (page - 1) * limit;

    const where: Prisma.ListingWhereInput = {
      status: 'active',
    };

    // Category filter
    if (dto.categoryId) {
      where.categoryId = dto.categoryId;
    } else if (dto.categorySlug) {
      where.category = { slug: dto.categorySlug };
    }

    // Listing type filter
    if (dto.listingType) {
      where.listingType = dto.listingType;
    }

    // Budget filter
    if (dto.budgetMin !== undefined || dto.budgetMax !== undefined) {
      where.AND = [
        ...(Array.isArray(where.AND) ? where.AND : []),
        ...(dto.budgetMin !== undefined
          ? [{ budgetMax: { gte: dto.budgetMin } }]
          : []),
        ...(dto.budgetMax !== undefined
          ? [{ budgetMin: { lte: dto.budgetMax } }]
          : []),
      ];
    }

    // Engagement type filter
    if (dto.engagementType) {
      where.engagementType = dto.engagementType;
    }

    // Location filter (area-based)
    if (dto.county || dto.subCounty) {
      where.location = {
        ...(dto.county && { county: { equals: dto.county, mode: 'insensitive' } }),
        ...(dto.subCounty && {
          subCounty: { equals: dto.subCounty, mode: 'insensitive' },
        }),
      };
    }

    // Text search (title/description)
    if (dto.query) {
      where.OR = [
        { title: { contains: dto.query, mode: 'insensitive' } },
        { description: { contains: dto.query, mode: 'insensitive' } },
      ];
    }

    // Sorting
    let orderBy: Prisma.ListingOrderByWithRelationInput = {
      createdAt: 'desc',
    };

    if (dto.sortBy === 'price_low') {
      orderBy = { budgetMin: 'asc' };
    } else if (dto.sortBy === 'price_high') {
      orderBy = { budgetMax: 'desc' };
    }

    const [listings, total] = await Promise.all([
      this.prisma.listing.findMany({
        where,
        include: {
          category: { select: { name: true, slug: true, iconUrl: true } },
          location: {
            select: { county: true, subCounty: true, estateArea: true, latitude: true, longitude: true },
          },
          user: {
            select: {
              id: true,
              isVerified: true,
              profile: {
                select: { displayName: true, avatarUrl: true, averageRating: true },
              },
            },
          },
        },
        orderBy,
        skip,
        take: limit,
      }),
      this.prisma.listing.count({ where }),
    ]);

    // If location-based search with coordinates, compute distances and sort
    let results = listings;
    if (dto.lat !== undefined && dto.lng !== undefined) {
      const resultsWithDistance = listings.map((listing) => ({
        ...listing,
        _distance: listing.location
          ? this.haversineDistance(
              dto.lat!,
              dto.lng!,
              Number(listing.location.latitude),
              Number(listing.location.longitude),
            )
          : Infinity,
      }));

      // Filter by radius if specified
      const radiusKm = dto.radiusKm || 20;
      results = resultsWithDistance
        .filter((l) => l._distance <= radiusKm)
        .sort((a, b) => a._distance - b._distance) as any;
    }

    return {
      data: results,
      meta: {
        total,
        page,
        limit,
        totalPages: Math.ceil(total / limit),
      },
    };
  }

  async getMyListings(userId: string, status?: string) {
    const where: Prisma.ListingWhereInput = { userId };
    if (status) {
      where.status = status as ListingStatus;
    }

    return this.prisma.listing.findMany({
      where,
      include: {
        category: { select: { name: true, slug: true } },
        location: { select: { county: true, subCounty: true, estateArea: true } },
        _count: { select: { applications: true } },
      },
      orderBy: { createdAt: 'desc' },
    });
  }

  private haversineDistance(
    lat1: number,
    lon1: number,
    lat2: number,
    lon2: number,
  ): number {
    const R = 6371; // Earth's radius in km
    const dLat = this.toRad(lat2 - lat1);
    const dLon = this.toRad(lon2 - lon1);
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(this.toRad(lat1)) *
        Math.cos(this.toRad(lat2)) *
        Math.sin(dLon / 2) *
        Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  }

  private toRad(deg: number): number {
    return deg * (Math.PI / 180);
  }
}
