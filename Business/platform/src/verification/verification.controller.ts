import { Controller, Post, Get, Body, UseGuards } from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';
import { VerificationService } from './verification.service';
import { SubmitVerificationDto } from './dto/verification.dto';
import { CurrentUser } from '../common/decorators';

@Controller('verification')
@UseGuards(AuthGuard('jwt'))
export class VerificationController {
  constructor(private verificationService: VerificationService) {}

  @Post()
  submit(
    @CurrentUser('id') userId: string,
    @Body() dto: SubmitVerificationDto,
  ) {
    return this.verificationService.submit(userId, dto);
  }

  @Get()
  getUserVerifications(@CurrentUser('id') userId: string) {
    return this.verificationService.getUserVerifications(userId);
  }
}
