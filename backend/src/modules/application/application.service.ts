import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';
const VALID_TRANSITIONS: Record<string, string[]> = {
  saved: ['ready_to_apply', 'withdrawn'], ready_to_apply: ['applied', 'withdrawn'], applied: ['hr_viewed', 'rejected', 'withdrawn'],
  hr_viewed: ['written_test', 'rejected'], written_test: ['interview_1', 'rejected'],
  interview_1: ['interview_2', 'rejected', 'offer'], interview_2: ['hr_interview', 'rejected', 'offer'],
  hr_interview: ['offer', 'rejected'], offer: ['rejected', 'withdrawn', 'accepted'],
  rejected: [], withdrawn: [],
};

@Injectable()
export class ApplicationService {
  constructor(private prisma: PrismaService) {}

  async findAll(userId: string, params: { status?: string; page?: number; limit?: number }) {
    const page = params.page || 1; const limit = params.limit || 20;
    const where: any = { userId, deletedAt: null };
    if (params.status) where.status = params.status;
    const [data, total] = await Promise.all([
      this.prisma.application.findMany({ where, orderBy: { updatedAt: 'desc' }, skip: (page - 1) * limit, take: limit, include: { job: { select: { id: true, title: true, company: { select: { id: true, name: true } } } } } }),
      this.prisma.application.count({ where }),
    ]);
    const stats = await this.prisma.application.groupBy({ by: ['status'], where: { userId, deletedAt: null }, _count: true });
    return { data, meta: { page, limit, total, totalPages: Math.ceil(total / limit) }, stats };
  }

  async create(userId: string, data: { jobId: string; referralId?: string; notes?: string }) {
    const existing = await this.prisma.application.findUnique({ where: { userId_jobId: { userId, jobId: data.jobId } } });
    if (existing) throw new Error('已收藏该岗位');
    return this.prisma.application.create({ data: { userId, jobId: data.jobId, companyId: '', status: 'saved', referralId: data.referralId, notes: data.notes, statusHistory: [{ status: 'saved', timestamp: new Date().toISOString() }] as any } });
  }

  async updateStatus(userId: string, id: string, newStatus: string) {
    const app = await this.prisma.application.findFirst({ where: { id, userId, deletedAt: null } });
    if (!app) throw new NotFoundException('投递记录不存在');
    const allowed = VALID_TRANSITIONS[app.status];
    if (!allowed?.includes(newStatus)) throw new Error(`不能从 ${app.status} 变更为 ${newStatus}`);
    const history = (app.statusHistory as any[]) || [];
    history.push({ status: newStatus, timestamp: new Date().toISOString() });
    return this.prisma.application.update({ where: { id }, data: { status: newStatus, statusHistory: history as any, appliedAt: newStatus === 'applied' ? new Date() : undefined } });
  }

  async getStats(userId: string) {
    const [total, byStatus] = await Promise.all([
      this.prisma.application.count({ where: { userId, deletedAt: null } }),
      this.prisma.application.groupBy({ by: ['status'], where: { userId, deletedAt: null }, _count: true }),
    ]);
    return { total, byStatus };
  }
}
