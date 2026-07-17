import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';

@Injectable()
export class UserService {
  constructor(private prisma: PrismaService) {}

  async getProfile(userId: string) {
    const user = await this.prisma.user.findUnique({
      where: { id: userId },
      select: { id: true, email: true, nickname: true, avatar: true, role: true, status: true,
        yearsExp: true, education: true, currentCity: true, currentCompany: true, currentTitle: true,
        skills: true, salaryMin: true, salaryMax: true, preferredCities: true, emailVerified: true,
        createdAt: true, lastLoginAt: true },
    });
    if (!user) throw new NotFoundException('用户不存在');
    const count = await this.prisma.resume.count({ where: { userId } });
    return { ...user, resumeCount: count };
  }

  async updateProfile(userId: string, data: any) {
    const allowed = ['nickname', 'avatar', 'yearsExp', 'education', 'currentCity', 'currentCompany', 'currentTitle', 'skills', 'salaryMin', 'salaryMax', 'preferredCities'];
    const updateData: any = {};
    for (const key of allowed) {
      if (data[key] !== undefined) updateData[key] = data[key];
    }
    return this.prisma.user.update({ where: { id: userId }, data: updateData, select: { id: true, nickname: true, avatar: true, yearsExp: true, education: true, currentCity: true, skills: true, salaryMin: true, salaryMax: true } });
  }

  async updateAvatar(userId: string, avatarUrl: string) {
    return this.prisma.user.update({ where: { id: userId }, data: { avatar: avatarUrl }, select: { id: true, avatar: true } });
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

  // Resume management
  async listResumes(userId: string) {
    return this.prisma.resume.findMany({ where: { userId, deletedAt: null }, orderBy: { createdAt: 'desc' }, select: { id: true, title: true, fileName: true, fileUrl: true, isDefault: true, createdAt: true, updatedAt: true } });
  }

  async createResume(userId: string, data: { title?: string; fileName?: string; fileUrl?: string; content?: string }) {
    const count = await this.prisma.resume.count({ where: { userId } });
    return this.prisma.resume.create({
      data: { userId, title: data.title || data.fileName || '未命名简历', fileName: data.fileName, fileUrl: data.fileUrl, content: data.content, isDefault: count === 0 },
    });
  }

  async deleteResume(id: string, userId: string) {
    const resume = await this.prisma.resume.findFirst({ where: { id, userId } });
    if (!resume) throw new NotFoundException('简历不存在');
    return this.prisma.resume.update({ where: { id }, data: { deletedAt: new Date() } });
  }
}
