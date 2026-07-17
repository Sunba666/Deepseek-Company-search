import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';

@Injectable()
export class UserService {
  constructor(private prisma: PrismaService) {}

  async getProfile(userId: string) {
    const user = await this.prisma.user.findUnique({
      where: { id: userId },
      select: { id: true, email: true, nickname: true, avatar: true, role: true, status: true,
        yearsExp: true, education: true, currentCity: true, skills: true,
        salaryMin: true, salaryMax: true, preferredCities: true, emailVerified: true,
        createdAt: true, lastLoginAt: true },
    });
    if (!user) throw new NotFoundException('用户不存在');
    return user;
  }

  async updateProfile(userId: string, data: any) {
    return this.prisma.user.update({ where: { id: userId }, data, select: { id: true, nickname: true, avatar: true } });
  }

  async getStats(userId: string) {
    const [total, applied, interviewing, offer] = await Promise.all([
      this.prisma.application.count({ where: { userId, deletedAt: null } }),
      this.prisma.application.count({ where: { userId, status: { in: ['applied', 'hr_viewed', 'written_test'] }, deletedAt: null } }),
      this.prisma.application.count({ where: { userId, status: { in: ['interview_1', 'interview_2', 'hr_interview'] }, deletedAt: null } }),
      this.prisma.application.count({ where: { userId, status: 'offer', deletedAt: null } }),
    ]);
    return { totalApplications: total, applied, interviewing, offer, interviewRate: total > 0 ? Math.round((interviewing / total) * 100) : 0 };
  }
}
