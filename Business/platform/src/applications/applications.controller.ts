import {
  Controller,
  Post,
  Get,
  Patch,
  Param,
  Body,
  Query,
  UseGuards,
} from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';
import { ApplicationsService } from './applications.service';
import { CreateApplicationDto, UpdateApplicationStatusDto } from './dto/application.dto';
import { CurrentUser } from '../common/decorators';

@Controller('applications')
@UseGuards(AuthGuard('jwt'))
export class ApplicationsController {
  constructor(private applicationsService: ApplicationsService) {}

  @Post()
  create(@CurrentUser('id') userId: string, @Body() dto: CreateApplicationDto) {
    return this.applicationsService.create(userId, dto);
  }

  @Get('my')
  getMyApplications(@CurrentUser('id') userId: string) {
    return this.applicationsService.getMyApplications(userId);
  }

  @Get('listing/:listingId')
  getForListing(
    @CurrentUser('id') userId: string,
    @Param('listingId') listingId: string,
  ) {
    return this.applicationsService.getForListing(listingId, userId);
  }

  @Patch(':id/status')
  updateStatus(
    @CurrentUser('id') userId: string,
    @Param('id') id: string,
    @Body() dto: UpdateApplicationStatusDto,
  ) {
    return this.applicationsService.updateStatus(id, userId, dto);
  }
}
