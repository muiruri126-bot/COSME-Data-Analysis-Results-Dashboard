import {
  Controller,
  Post,
  Get,
  Patch,
  Body,
  Param,
  Query,
  UseGuards,
} from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';
import { ReportsService } from './reports.service';
import { CreateReportDto } from './dto/report.dto';
import { CurrentUser } from '../common/decorators/current-user.decorator';
import { Roles } from '../common/decorators/roles.decorator';
import { RolesGuard } from '../common/guards/roles.guard';

@Controller('reports')
@UseGuards(AuthGuard('jwt'))
export class ReportsController {
  constructor(private reportsService: ReportsService) {}

  @Post()
  create(@CurrentUser('id') userId: string, @Body() dto: CreateReportDto) {
    return this.reportsService.create(userId, dto);
  }

  @Get('mine')
  getMyReports(@CurrentUser('id') userId: string) {
    return this.reportsService.getMyReports(userId);
  }

  @Get('pending')
  @UseGuards(RolesGuard)
  @Roles('admin')
  getPendingReports(
    @Query('page') page?: string,
    @Query('limit') limit?: string,
  ) {
    return this.reportsService.getPendingReports(
      page ? parseInt(page, 10) : 1,
      limit ? parseInt(limit, 10) : 20,
    );
  }

  @Patch(':id/resolve')
  @UseGuards(RolesGuard)
  @Roles('admin')
  resolveReport(
    @Param('id') id: string,
    @CurrentUser('id') adminId: string,
    @Body() body: { status: 'resolved' | 'dismissed'; notes?: string },
  ) {
    return this.reportsService.resolveReport(id, adminId, body.status, body.notes);
  }
}
