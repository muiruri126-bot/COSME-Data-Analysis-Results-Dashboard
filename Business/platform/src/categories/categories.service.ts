import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';

@Injectable()
export class CategoriesService {
  constructor(private prisma: PrismaService) {}

  async findAll(includeInactive = false) {
    const where = includeInactive ? {} : { isActive: true };

    const categories = await this.prisma.serviceCategory.findMany({
      where: { ...where, parentId: null },
      include: {
        children: {
          where,
          orderBy: { sortOrder: 'asc' },
        },
      },
      orderBy: { sortOrder: 'asc' },
    });

    return categories;
  }

  async findBySlug(slug: string) {
    const category = await this.prisma.serviceCategory.findUnique({
      where: { slug },
      include: {
        children: { where: { isActive: true } },
        skills: { where: { isActive: true } },
      },
    });

    if (!category) {
      throw new NotFoundException('Category not found');
    }

    return category;
  }

  async getSkills(categoryId: string) {
    return this.prisma.skill.findMany({
      where: { categoryId, isActive: true },
      orderBy: { name: 'asc' },
    });
  }
}
