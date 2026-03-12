import {
  Controller,
  Post,
  Delete,
  Body,
  Param,
  UseGuards,
  UseInterceptors,
  UploadedFile,
} from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';
import { FileInterceptor } from '@nestjs/platform-express';
import { UploadService } from './upload.service';
import { UploadFileDto } from './dto/upload.dto';
import { CurrentUser } from '../common/decorators/current-user.decorator';

@Controller('upload')
@UseGuards(AuthGuard('jwt'))
export class UploadController {
  constructor(private uploadService: UploadService) {}

  @Post()
  @UseInterceptors(FileInterceptor('file'))
  uploadFile(
    @UploadedFile() file: Express.Multer.File,
    @Body() dto: UploadFileDto,
    @CurrentUser('id') userId: string,
  ) {
    return this.uploadService.uploadFile(file, dto.type, userId);
  }

  @Delete(':key')
  deleteFile(@Param('key') key: string) {
    return this.uploadService.deleteFile(key);
  }
}
