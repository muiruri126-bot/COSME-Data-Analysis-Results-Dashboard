import { Controller, Post, Put, Get, Body, UseGuards } from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';
import { ProfilesService } from './profiles.service';
import { CreateProfileDto, UpdateProfileDto } from './dto/profile.dto';
import { CurrentUser } from '../common/decorators';

@Controller('profiles')
@UseGuards(AuthGuard('jwt'))
export class ProfilesController {
  constructor(private profilesService: ProfilesService) {}

  @Post()
  create(@CurrentUser('id') userId: string, @Body() dto: CreateProfileDto) {
    return this.profilesService.create(userId, dto);
  }

  @Put()
  update(@CurrentUser('id') userId: string, @Body() dto: UpdateProfileDto) {
    return this.profilesService.update(userId, dto);
  }

  @Get('me')
  getMyProfile(@CurrentUser('id') userId: string) {
    return this.profilesService.findByUserId(userId);
  }
}
