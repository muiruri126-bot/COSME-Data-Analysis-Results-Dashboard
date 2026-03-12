import { Injectable, BadRequestException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { CreateReportDto } from './dto/report.dto';

@Injectable()
export class ReportsService {
  constructor(private prisma: PrismaService) {}

  async create(reporterId: string, dto: CreateReportDto) {
    if (!dto.reportedUserId && !dto.reportedListingId) {
      throw new BadRequestException(
        'Please specify either a user or a listing to report',
      );
    }

    return this.prisma.report.create({
      data: {
        reporterId,
        reportedUserId: dto.reportedUserId,
        reportedListingId: dto.reportedListingId,
        reason: dto.reason,
        description: dto.description,
      },
    });
  }

  async getMyReports(reporterId: string) {
    return this.prisma.report.findMany({
      where: { reporterId },
      orderBy: { createdAt: 'desc' },
    });
  }

  // Admin methods
  async getPendingReports(page = 1, limit = 20) {
    const skip = (page - 1) * limit;

    const [reports, total] = await Promise.all([
      this.prisma.report.findMany({
        where: { status: { in: ['pending', 'investigating'] } },
        include: {
          reporter: {
            select: {
              id: true,
              phone: true,
              profile: { select: { displayName: true } },
            },
          },
          reportedUser: {
            select: {
              id: true,
              phone: true,
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

  async resolveReport(
    reportId: string,
    adminId: string,
    status: 'resolved' | 'dismissed',
    notes?: string,
  ) {
    return this.prisma.report.update({
      where: { id: reportId },
      data: {
        status,
        resolvedBy: adminId,
        resolutionNotes: notes,
      },
    });
  }
}
