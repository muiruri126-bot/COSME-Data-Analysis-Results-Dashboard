import { Injectable, ConflictException, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { CreateProfileDto, UpdateProfileDto } from './dto/profile.dto';

@Injectable()
export class ProfilesService {
  constructor(private prisma: PrismaService) {}

  async create(userId: string, dto: CreateProfileDto) {
    const existing = await this.prisma.profile.findUnique({
      where: { userId },
    });

    if (existing) {
      throw new ConflictException('Profile already exists. Use PUT to update.');
    }

    return this.prisma.$transaction(async (tx) => {
      // Create or find location
      const location = await tx.location.create({
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

      // Create profile
      const profile = await tx.profile.create({
        data: {
          userId,
          firstName: dto.firstName,
          lastName: dto.lastName,
          displayName: dto.displayName || `${dto.firstName} ${dto.lastName.charAt(0)}.`,
          bio: dto.bio,
          avatarUrl: dto.avatarUrl,
          dateOfBirth: dto.dateOfBirth ? new Date(dto.dateOfBirth) : undefined,
          gender: dto.gender,
          primaryLocationId: location.id,
          isAvailable: dto.isAvailable ?? true,
          availabilityNote: dto.availabilityNote,
        },
      });

      // Create user roles
      if (dto.roles?.length) {
        await tx.userRole.createMany({
          data: dto.roles.map((r) => ({
            userId,
            categoryId: r.categoryId,
            roleType: r.roleType,
          })),
          skipDuplicates: true,
        });
      }

      // Create user skills
      if (dto.skills?.length) {
        await tx.userSkill.createMany({
          data: dto.skills.map((s) => ({
            userId,
            skillId: s.skillId,
            yearsExperience: s.yearsExperience,
            proficiency: s.proficiency,
          })),
          skipDuplicates: true,
        });
      }

      // Update user status to active
      await tx.user.update({
        where: { id: userId },
        data: { status: 'active' },
      });

      return profile;
    });
  }

  async update(userId: string, dto: UpdateProfileDto) {
    const existing = await this.prisma.profile.findUnique({
      where: { userId },
    });

    if (!existing) {
      throw new NotFoundException('Profile not found. Create one first.');
    }

    return this.prisma.$transaction(async (tx) => {
      // Update location if provided
      if (dto.location && existing.primaryLocationId) {
        await tx.location.update({
          where: { id: existing.primaryLocationId },
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
      }

      // Update profile
      const profile = await tx.profile.update({
        where: { userId },
        data: {
          firstName: dto.firstName,
          lastName: dto.lastName,
          displayName: dto.displayName,
          bio: dto.bio,
          avatarUrl: dto.avatarUrl,
          dateOfBirth: dto.dateOfBirth ? new Date(dto.dateOfBirth) : undefined,
          gender: dto.gender,
          isAvailable: dto.isAvailable,
          availabilityNote: dto.availabilityNote,
        },
      });

      // Update roles if provided
      if (dto.roles) {
        await tx.userRole.deleteMany({ where: { userId } });
        await tx.userRole.createMany({
          data: dto.roles.map((r) => ({
            userId,
            categoryId: r.categoryId,
            roleType: r.roleType,
          })),
        });
      }

      // Update skills if provided
      if (dto.skills) {
        await tx.userSkill.deleteMany({ where: { userId } });
        await tx.userSkill.createMany({
          data: dto.skills.map((s) => ({
            userId,
            skillId: s.skillId,
            yearsExperience: s.yearsExperience,
            proficiency: s.proficiency,
          })),
        });
      }

      return profile;
    });
  }

  async findByUserId(userId: string) {
    const profile = await this.prisma.profile.findUnique({
      where: { userId },
      include: { location: true },
    });

    if (!profile) {
      throw new NotFoundException('Profile not found');
    }

    return profile;
  }
}
