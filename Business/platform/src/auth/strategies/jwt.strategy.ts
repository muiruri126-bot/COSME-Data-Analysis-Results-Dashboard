import { Injectable, UnauthorizedException } from '@nestjs/common';
import { PassportStrategy } from '@nestjs/passport';
import { ExtractJwt, Strategy } from 'passport-jwt';
import { ConfigService } from '@nestjs/config';
import { PrismaService } from '../../prisma/prisma.service';

export interface JwtPayload {
  sub: string;
  phone: string;
}

@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy) {
  constructor(
    config: ConfigService,
    private prisma: PrismaService,
  ) {
    super({
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
      ignoreExpiration: false,
      secretOrKey: config.get<string>('JWT_SECRET')!,
    });
  }

  async validate(payload: JwtPayload) {
    const user = await this.prisma.user.findUnique({
      where: { id: payload.sub },
      select: {
        id: true,
        phone: true,
        email: true,
        status: true,
        isVerified: true,
        roles: {
          select: {
            roleType: true,
            category: { select: { slug: true } },
          },
        },
      },
    });

    if (!user || user.status === 'suspended' || user.status === 'deactivated') {
      throw new UnauthorizedException('Account is not accessible');
    }

    return {
      id: user.id,
      phone: user.phone,
      email: user.email,
      status: user.status,
      isVerified: user.isVerified,
      roles: user.roles.map((r) =>
        r.category ? `${r.roleType}:${r.category.slug}` : r.roleType,
      ),
    };
  }
}
