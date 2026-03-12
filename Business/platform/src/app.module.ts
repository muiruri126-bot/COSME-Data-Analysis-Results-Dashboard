import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { PrismaModule } from './prisma/prisma.module';
import { AuthModule } from './auth/auth.module';
import { UsersModule } from './users/users.module';
import { ProfilesModule } from './profiles/profiles.module';
import { CategoriesModule } from './categories/categories.module';
import { ListingsModule } from './listings/listings.module';
import { ApplicationsModule } from './applications/applications.module';
import { ReviewsModule } from './reviews/reviews.module';
import { ChatModule } from './chat/chat.module';
import { NotificationsModule } from './notifications/notifications.module';
import { VerificationModule } from './verification/verification.module';
import { ReportsModule } from './reports/reports.module';
import { UploadModule } from './upload/upload.module';
import { AdminModule } from './admin/admin.module';

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true }),
    PrismaModule,
    AuthModule,
    UsersModule,
    ProfilesModule,
    CategoriesModule,
    ListingsModule,
    ApplicationsModule,
    ReviewsModule,
    ChatModule,
    NotificationsModule,
    VerificationModule,
    ReportsModule,
    UploadModule,
    AdminModule,
  ],
})
export class AppModule {}
