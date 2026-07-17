import { Controller, Get } from '@nestjs/common';
import { Public } from '../common/decorators/public.decorator';
import { PrismaService } from '../prisma/prisma.service';
import { RedisService } from '../redis/redis.service';

@Controller('api/v1/health')
export class HealthController {
  constructor(private prisma: PrismaService, private redis: RedisService) {}
  @Public() @Get()
  async check() {
    try { await this.prisma.$queryRaw`SELECT 1`; var db = 'ok'; } catch { db = 'error'; }
    return { status: 'ok', timestamp: new Date().toISOString(), database: db, cache: this.redis.getStats() };
  }
}
