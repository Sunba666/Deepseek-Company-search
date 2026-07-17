import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';

@Injectable()
export class ReferralService {
  constructor(private prisma: PrismaService) {}

  async findAll(params: { page?: number; limit?: number; companyId?: string; status?: string; minScore?: number }) {
    const page = params.page || 1; const limit = params.limit || 20;
    const where: any = { deletedAt: null };
    if (params.companyId) where.companyId = params.companyId;
    if (params.status) where.status = params.status;
    if (params.minScore) where.confidenceScore = { gte: params.minScore };
    const [data, total] = await Promise.all([
      this.prisma.referral.findMany({ where, orderBy: { confidenceScore: 'desc' }, skip: (page - 1) * limit, take: limit, include: { company: { select: { id: true, name: true, slug: true } } } }),
      this.prisma.referral.count({ where }),
    ]);
    return { data, meta: { page, limit, total, totalPages: Math.ceil(total / limit) } };
  }

  async findById(id: string) {
    const ref = await this.prisma.referral.findUnique({ where: { id }, include: { company: true, job: true } });
    if (!ref) throw new NotFoundException('内推信息不存在');
    return ref;
  }

  async reportExpired(id: string) {
    return this.prisma.referral.update({ where: { id }, data: { status: 'invalid', failCount: { increment: 1 } } });
  }

  async findByCode(code: string) { return this.prisma.referral.findFirst({ where: { referralCode: code, status: 'active' } }); }
}
