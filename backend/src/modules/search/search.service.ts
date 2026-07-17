import { Injectable } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';

@Injectable()
export class SearchService {
  constructor(private prisma: PrismaService) {}

  async search(q: string, type?: string) {
    if (!q || q.length < 1) return { jobs: [], companies: [] };
    const [jobs, companies] = await Promise.all([
      this.prisma.job.findMany({ where: { isActive: true, deletedAt: null, OR: [{ title: { contains: q } }, { companyName: { contains: q } }, { skills: { hasSome: [q] } }] }, orderBy: { publishedAt: 'desc' }, take: 10, include: { company: { select: { id: true, name: true, slug: true, logo: true } } } }),
      this.prisma.company.findMany({ where: { deletedAt: null, OR: [{ name: { contains: q } }, { nameEn: { contains: q } }, { industry: { contains: q } }] }, orderBy: { hiringCount: 'desc' }, take: 5 }),
    ]);
    return { jobs, companies, total: jobs.length + companies.length };
  }

  async aiSearch(q: string) {
    // TODO: NLP parse query -> structured filters
    return this.search(q);
  }
}
