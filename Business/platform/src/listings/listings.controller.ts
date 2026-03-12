import {
  Controller,
  Get,
  Post,
  Put,
  Delete,
  Param,
  Body,
  Query,
  UseGuards,
} from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';
import { ListingsService } from './listings.service';
import { CreateListingDto, UpdateListingDto, SearchListingsDto } from './dto/listing.dto';
import { CurrentUser } from '../common/decorators';

@Controller('listings')
export class ListingsController {
  constructor(private listingsService: ListingsService) {}

  @Get('search')
  search(@Query() dto: SearchListingsDto) {
    return this.listingsService.search(dto);
  }

  @Get('my')
  @UseGuards(AuthGuard('jwt'))
  getMyListings(
    @CurrentUser('id') userId: string,
    @Query('status') status?: string,
  ) {
    return this.listingsService.getMyListings(userId, status);
  }

  @Get(':id')
  findById(@Param('id') id: string) {
    return this.listingsService.findById(id);
  }

  @Post()
  @UseGuards(AuthGuard('jwt'))
  create(@CurrentUser('id') userId: string, @Body() dto: CreateListingDto) {
    return this.listingsService.create(userId, dto);
  }

  @Put(':id')
  @UseGuards(AuthGuard('jwt'))
  update(
    @CurrentUser('id') userId: string,
    @Param('id') id: string,
    @Body() dto: UpdateListingDto,
  ) {
    return this.listingsService.update(userId, id, dto);
  }

  @Delete(':id')
  @UseGuards(AuthGuard('jwt'))
  delete(@CurrentUser('id') userId: string, @Param('id') id: string) {
    return this.listingsService.delete(userId, id);
  }
}
