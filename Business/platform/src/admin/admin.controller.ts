import {
  Controller,
  Get,
  Put,
  Post,
  Delete,
  Param,
  Query,
  Body,
  UseGuards,
  ParseIntPipe,
  DefaultValuePipe,
} from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';
import { AdminService } from './admin.service';
import { Roles } from '../common/decorators';
import { RolesGuard } from '../common/guards/roles.guard';
import { UserStatus, ListingStatus } from '@prisma/client';

@Controller('admin')
@UseGuards(AuthGuard('jwt'), RolesGuard)
@Roles('admin', 'super_admin')
export class AdminController {
  constructor(private adminService: AdminService) {}

  // ─── Dashboard ───

  @Get('dashboard')
  getDashboardStats() {
    return this.adminService.getDashboardStats();
  }

  // ─── Users ───

  @Get('users')
  getUsers(
    @Query('page', new DefaultValuePipe(1), ParseIntPipe) page: number,
    @Query('limit', new DefaultValuePipe(20), ParseIntPipe) limit: number,
    @Query('search') search?: string,
  ) {
    return this.adminService.getUsers(page, limit, search);
  }

  @Get('users/:id')
  getUserDetail(@Param('id') id: string) {
    return this.adminService.getUserDetail(id);
  }

  @Put('users/:id/status')
  updateUserStatus(
    @Param('id') id: string,
    @Body('status') status: UserStatus,
  ) {
    return this.adminService.updateUserStatus(id, status);
  }

  // ─── Listings Moderation ───

  @Get('listings')
  getListings(
    @Query('page', new DefaultValuePipe(1), ParseIntPipe) page: number,
    @Query('limit', new DefaultValuePipe(20), ParseIntPipe) limit: number,
    @Query('status') status?: ListingStatus,
  ) {
    return this.adminService.getListingsForModeration(page, limit, status);
  }

  @Put('listings/:id/status')
  updateListingStatus(
    @Param('id') id: string,
    @Body('status') status: ListingStatus,
  ) {
    return this.adminService.updateListingStatus(id, status);
  }

  // ─── Categories ───

  @Post('categories')
  createCategory(
    @Body()
    body: {
      name: string;
      slug: string;
      listingType: 'job' | 'rental' | 'service_request' | 'space' | 'offer';
      description?: string;
      parentId?: string;
      iconUrl?: string;
      attributeSchema?: any;
      sortOrder?: number;
    },
  ) {
    return this.adminService.createCategory(body);
  }

  @Put('categories/:id')
  updateCategory(
    @Param('id') id: string,
    @Body()
    body: {
      name?: string;
      description?: string;
      iconUrl?: string;
      isActive?: boolean;
      attributeSchema?: any;
      sortOrder?: number;
    },
  ) {
    return this.adminService.updateCategory(id, body);
  }

  @Delete('categories/:id')
  deleteCategory(@Param('id') id: string) {
    return this.adminService.deleteCategory(id);
  }

  // ─── Verifications ───

  @Get('verifications')
  getPendingVerifications(
    @Query('page', new DefaultValuePipe(1), ParseIntPipe) page: number,
    @Query('limit', new DefaultValuePipe(20), ParseIntPipe) limit: number,
  ) {
    return this.adminService.getPendingVerifications(page, limit);
  }

  // ─── Reports ───

  @Get('reports')
  getPendingReports(
    @Query('page', new DefaultValuePipe(1), ParseIntPipe) page: number,
    @Query('limit', new DefaultValuePipe(20), ParseIntPipe) limit: number,
  ) {
    return this.adminService.getPendingReports(page, limit);
  }
}
