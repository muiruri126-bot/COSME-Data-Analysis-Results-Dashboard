import { Injectable, BadRequestException } from '@nestjs/common';
import { randomUUID } from 'crypto';
import * as path from 'path';
import * as fs from 'fs';
import { UploadType } from './dto/upload.dto';

@Injectable()
export class UploadService {
  private readonly uploadDir: string;

  constructor() {
    this.uploadDir = process.env.UPLOAD_DIR || './uploads';
    if (!fs.existsSync(this.uploadDir)) {
      fs.mkdirSync(this.uploadDir, { recursive: true });
    }
  }

  private readonly allowedImageTypes = [
    'image/jpeg',
    'image/png',
    'image/webp',
  ];

  private readonly allowedDocTypes = [
    'image/jpeg',
    'image/png',
    'application/pdf',
  ];

  private readonly maxImageSize = 5 * 1024 * 1024; // 5MB
  private readonly maxDocSize = 10 * 1024 * 1024; // 10MB

  async uploadFile(
    file: Express.Multer.File,
    type: UploadType,
    userId: string,
  ): Promise<{ url: string; key: string }> {
    this.validateFile(file, type);

    const ext = path.extname(file.originalname);
    const key = `${type}/${userId}/${randomUUID()}${ext}`;
    const filePath = path.join(this.uploadDir, key);

    const dir = path.dirname(filePath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    fs.writeFileSync(filePath, file.buffer);

    // In production, replace with S3 upload:
    // const s3Url = await this.uploadToS3(file.buffer, key, file.mimetype);
    const url = `/uploads/${key}`;

    return { url, key };
  }

  async deleteFile(key: string): Promise<void> {
    const filePath = path.join(this.uploadDir, key);
    if (fs.existsSync(filePath)) {
      fs.unlinkSync(filePath);
    }
  }

  private validateFile(file: Express.Multer.File, type: UploadType) {
    const isDoc = type === UploadType.VERIFICATION_DOC;
    const allowedTypes = isDoc ? this.allowedDocTypes : this.allowedImageTypes;
    const maxSize = isDoc ? this.maxDocSize : this.maxImageSize;

    if (!allowedTypes.includes(file.mimetype)) {
      throw new BadRequestException(
        `Invalid file type. Allowed: ${allowedTypes.join(', ')}`,
      );
    }

    if (file.size > maxSize) {
      throw new BadRequestException(
        `File too large. Max: ${maxSize / (1024 * 1024)}MB`,
      );
    }
  }

  // S3 upload stub for production usage
  // private async uploadToS3(buffer: Buffer, key: string, contentType: string) {
  //   const { S3Client, PutObjectCommand } = require('@aws-sdk/client-s3');
  //   const client = new S3Client({
  //     endpoint: process.env.S3_ENDPOINT,
  //     region: process.env.S3_REGION,
  //     credentials: {
  //       accessKeyId: process.env.S3_ACCESS_KEY,
  //       secretAccessKey: process.env.S3_SECRET_KEY,
  //     },
  //   });
  //   await client.send(new PutObjectCommand({
  //     Bucket: process.env.S3_BUCKET,
  //     Key: key,
  //     Body: buffer,
  //     ContentType: contentType,
  //     ACL: 'public-read',
  //   }));
  //   return `${process.env.S3_ENDPOINT}/${process.env.S3_BUCKET}/${key}`;
  // }
}
