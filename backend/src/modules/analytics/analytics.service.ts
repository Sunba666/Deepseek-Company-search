import { Injectable } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';

@Injectable()
export class AnalyticsService {
  constructor(private prisma: PrismaService) {}

  async track(data: { userId?: string; action: string; targetType?: string; targetId?: string; metadata?: any; ipAddress?: string; userAgent?: string }) {
    return this.prisma.activityLog.create({ data });
  }

  async getDashboard() {
    const [users, jobs, referrals, applications] = await Promise.all([
      this.prisma.user.count({ where: { deletedAt: null } }),
      this.prisma.job.count({ where: { isActive: true, deletedAt: null } }),
      this.prisma.referral.count({ where: { status: 'active', deletedAt: null } }),
      this.prisma.application.count({ where: { deletedAt: null } }),
    ]);
    return { users, jobs, referrals, applications };
  }
}
