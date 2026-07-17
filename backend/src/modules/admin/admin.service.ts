import { Injectable } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';

@Injectable()
export class AdminService {
  constructor(private prisma: PrismaService) {}

  async getDashboard() {
    const [users, companies, jobs, referrals, applications] = await Promise.all([
      this.prisma.user.count(), this.prisma.company.count(),
      this.prisma.job.count({ where: { isActive: true } }),
      this.prisma.referral.count({ where: { status: 'active' } }),
      this.prisma.application.count(),
    ]);
    const recentUsers = await this.prisma.user.findMany({ orderBy: { createdAt: 'desc' }, take: 10, select: { id: true, email: true, nickname: true, role: true, createdAt: true } });
    const recentJobs = await this.prisma.job.findMany({ orderBy: { createdAt: 'desc' }, take: 10, include: { company: { select: { name: true } } } });
    return { stats: { users, companies, jobs, referrals, applications }, recentUsers, recentJobs };
  }

  async listUsers(page = 1, limit = 20) {
    const [data, total] = await Promise.all([
      this.prisma.user.findMany({ skip: (page - 1) * limit, take: limit, orderBy: { createdAt: 'desc' }, select: { id: true, email: true, nickname: true, role: true, status: true, createdAt: true, lastLoginAt: true } }),
      this.prisma.user.count(),
    ]); return { data, meta: { page, limit, total, totalPages: Math.ceil(total / limit) } };
  }

  async updateUserRole(id: string, role: string) { return this.prisma.user.update({ where: { id }, data: { role } }); }

  async toggleUserStatus(id: string) {
    const user = await this.prisma.user.findUnique({ where: { id } });
    return this.prisma.user.update({ where: { id }, data: { status: user?.status === 'active' ? 'banned' : 'active' } });
  }

  async listJobs(page = 1, limit = 20) {
    const [data, total] = await Promise.all([
      this.prisma.job.findMany({ skip: (page - 1) * limit, take: limit, orderBy: { createdAt: 'desc' }, include: { company: { select: { name: true, slug: true } } } }),
      this.prisma.job.count(),
    ]); return { data, meta: { page, limit, total, totalPages: Math.ceil(total / limit) } };
  }

  async toggleJobStatus(id: string) {
    const job = await this.prisma.job.findUnique({ where: { id } });
    return this.prisma.job.update({ where: { id }, data: { isActive: !job?.isActive } });
  }

  async createJob(data: { companyId: string; title: string; category: string; city: string; salaryMin?: number; salaryMax?: number; experience?: string; education?: string; skills?: string[]; description?: string }) {
    const company = await this.prisma.company.findUnique({ where: { id: data.companyId } });
    return this.prisma.job.create({
      data: {
        companyId: data.companyId, companyName: company?.name || '',
        title: data.title, category: data.category || '其他', city: data.city,
        salaryMin: data.salaryMin, salaryMax: data.salaryMax,
        experience: data.experience, education: data.education,
        skills: data.skills || [], description: data.description,
        isActive: true, publishedAt: new Date(),
      },
    });
  }

  async getAIConfig() { return { provider: process.env.AI_PROVIDER || 'deepseek', model: process.env.AI_MODEL || 'deepseek-chat', apiKey: process.env.AI_API_KEY ? '***' : '' }; }

  async getLogs(page = 1, limit = 50) {
    const [data, total] = await Promise.all([
      this.prisma.systemLog.findMany({ skip: (page - 1) * limit, take: limit, orderBy: { createdAt: 'desc' } }),
      this.prisma.systemLog.count(),
    ]); return { data, meta: { page, limit, total, totalPages: Math.ceil(total / limit) } };
  }
}
