import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';

@Injectable()
export class CompanyService {
  constructor(private prisma: PrismaService) {}

  async findAll(params: { page?: number; limit?: number; industry?: string; city?: string }) {
    const page = params.page || 1;
    const limit = params.limit || 20;
    const where: any = { deletedAt: null };
    if (params.industry) where.industry = params.industry;
    if (params.city) where.city = params.city;
    const [data, total] = await Promise.all([
      this.prisma.company.findMany({ where, orderBy: { hiringCount: 'desc' }, skip: (page - 1) * limit, take: limit }),
      this.prisma.company.count({ where }),
    ]);
    return { data, meta: { page, limit, total, totalPages: Math.ceil(total / limit) } };
  }

  async findBySlug(slug: string) {
    const company = await this.prisma.company.findUnique({ where: { slug }, include: { companyProfile: true } });
    if (!company) throw new NotFoundException('公司不存在');
    return company;
  }

  async getJobs(slug: string, params: { category?: string }) {
    const company = await this.prisma.company.findUnique({ where: { slug } });
    if (!company) throw new NotFoundException('公司不存在');
    const where: any = { companyId: company.id, isActive: true, deletedAt: null };
    if (params.category) where.category = params.category;
    return this.prisma.job.findMany({ where, orderBy: { publishedAt: 'desc' }, take: 50 });
  }
}
