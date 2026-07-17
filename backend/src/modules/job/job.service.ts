import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';
import { Prisma } from '@prisma/client';

@Injectable()
export class JobService {
  constructor(private prisma: PrismaService) {}

  async findAll(params: { page?: number; limit?: number; category?: string; subCategory?: string; city?: string; experience?: string; education?: string; salaryMin?: number; salaryMax?: number; isRemote?: boolean; sort?: string; q?: string }) {
    const page = params.page || 1;
    const limit = params.limit || 20;
    const where: Prisma.JobWhereInput = { isActive: true, deletedAt: null };
    if (params.category && params.category !== '全部') where.category = params.category;
    if (params.subCategory) where.subCategory = params.subCategory;
    if (params.city) where.city = params.city;
    if (params.experience) where.experience = params.experience;
    if (params.education) where.education = params.education;
    if (params.salaryMin) where.salaryMin = { gte: params.salaryMin };
    if (params.salaryMax) where.salaryMax = { lte: params.salaryMax };
    if (params.isRemote !== undefined) where.isRemote = params.isRemote;
    if (params.q) where.OR = [{ title: { contains: params.q } }, { companyName: { contains: params.q } }, { skills: { hasSome: [params.q] } }];
    const orderBy: Prisma.JobOrderByWithRelationInput = params.sort === 'salary' ? { salaryMax: 'desc' } : { publishedAt: 'desc' };
    const [data, total] = await Promise.all([
      this.prisma.job.findMany({ where, orderBy, skip: (page - 1) * limit, take: limit, include: { company: { select: { id: true, name: true, slug: true, logo: true } } } }),
      this.prisma.job.count({ where }),
    ]);
    return { data, meta: { page, limit, total, totalPages: Math.ceil(total / limit) } };
  }

  async findById(id: string) {
    const job = await this.prisma.job.findUnique({ where: { id }, include: { company: true, referrals: { where: { status: 'active', deletedAt: null }, orderBy: { confidenceScore: 'desc' } } } });
    if (!job) throw new NotFoundException('岗位不存在');
    return job;
  }

  async search(q: string) { return this.findAll({ q, limit: 10 }); }
}
