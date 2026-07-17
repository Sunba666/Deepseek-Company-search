import { Injectable, NotFoundException, ForbiddenException, Logger } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';

@Injectable()
export class ReferralService {
  private readonly logger = new Logger(ReferralService.name);
  constructor(private prisma: PrismaService) {}

  async findAll(params: { page?: number; limit?: number; companyId?: string; status?: string; minScore?: number; userId?: string }) {
    const page = params.page || 1; const limit = params.limit || 20;
    const where: any = { deletedAt: null };
    if (params.companyId) where.companyId = params.companyId;
    if (params.status) where.status = params.status;
    if (params.minScore) where.confidenceScore = { gte: params.minScore };

    const [data, total] = await Promise.all([
      this.prisma.referral.findMany({
        where,
        orderBy: { confidenceScore: 'desc' },
        skip: (page - 1) * limit,
        take: limit,
        include: {
          company: { select: { id: true, name: true, slug: true, logo: true } },
          job: { select: { id: true, title: true, salaryMin: true, salaryMax: true } },
          ...(params.userId ? {
            referralFavorites: { where: { userId: params.userId }, select: { id: true } },
          } : {}),
          _count: { select: { referralFavorites: true, referralRatings: true } },
        },
      }),
      this.prisma.referral.count({ where }),
    ]);
    return { data, meta: { page, limit, total, totalPages: Math.ceil(total / limit) } };
  }

  async findById(id: string) {
    const ref = await this.prisma.referral.findUnique({
      where: { id },
      include: {
        company: true, job: true,
        _count: { select: { referralFavorites: true, referralRatings: true } },
      },
    });
    if (!ref) throw new NotFoundException('内推信息不存在');
    return ref;
  }

  async create(data: {
    companyId: string; jobId?: string; referralCode: string; referralLink?: string;
    referrerName?: string; isEmployee?: boolean; notes?: string; userId: string;
  }) {
    const company = await this.prisma.company.findUnique({ where: { id: data.companyId } });
    if (!company) throw new NotFoundException('公司不存在');

    // Recalculate confidence score
    const confidenceScore = this.calculateConfidence({
      isEmployee: data.isEmployee ?? false, verifiedCount: 0, successCount: 0, failCount: 0,
    });

    return this.prisma.referral.create({
      data: {
        companyId: data.companyId, companyName: company.name,
        jobId: data.jobId, referralCode: data.referralCode,
        referralLink: data.referralLink, referrerName: data.referrerName,
        referrerTitle: '', isEmployee: data.isEmployee ?? false,
        confidenceScore, confidenceLevel: this.getLevel(confidenceScore),
        status: 'active', publishedAt: new Date(),
        notes: data.notes,
      },
    });
  }

  async toggleFavorite(referralId: string, userId: string) {
    const existing = await this.prisma.referralFavorite.findUnique({
      where: { userId_referralId: { userId, referralId } },
    });
    if (existing) {
      await this.prisma.referralFavorite.delete({ where: { id: existing.id } });
      return { favorited: false };
    }
    await this.prisma.referralFavorite.create({ data: { userId, referralId } });
    return { favorited: true };
  }

  async rate(referralId: string, userId: string, data: { score: number; comment?: string; responseTime?: string; isSuccess?: boolean }) {
    const referral = await this.prisma.referral.findUnique({ where: { id: referralId } });
    if (!referral) throw new NotFoundException('内推信息不存在');

    await this.prisma.referralRating.upsert({
      where: { userId_referralId: { userId, referralId } },
      create: { userId, referralId, score: data.score, comment: data.comment, responseTime: data.responseTime, isSuccess: data.isSuccess },
      update: { score: data.score, comment: data.comment, responseTime: data.responseTime, isSuccess: data.isSuccess },
    });

    // Recalculate confidence score
    const ratings = await this.prisma.referralRating.findMany({ where: { referralId } });
    const verifiedCount = ratings.length;
    const successCount = ratings.filter(r => r.isSuccess === true).length;
    const failCount = ratings.filter(r => r.isSuccess === false).length;
    const avgScore = ratings.reduce((s, r) => s + r.score, 0) / ratings.length;
    const fastResponse = ratings.filter(r => r.responseTime === 'fast').length;
    const slowResponse = ratings.filter(r => r.responseTime === 'slow').length;

    const confidenceScore = this.calculateConfidence({
      isEmployee: referral.isEmployee,
      verifiedCount,
      successCount,
      failCount,
      avgScore,
      fastResponse,
      slowResponse,
    });

    await this.prisma.referral.update({
      where: { id: referralId },
      data: {
        confidenceScore,
        confidenceLevel: this.getLevel(confidenceScore),
        verifiedCount,
        successCount,
        failCount,
        isVerified: successCount >= 2,
      },
    });

    return { confidenceScore, verifiedCount, successCount };
  }

  async report(referralId: string, userId: string, data: { reason: string; detail?: string }) {
    const referral = await this.prisma.referral.findUnique({ where: { id: referralId } });
    if (!referral) throw new NotFoundException('内推信息不存在');

    return this.prisma.referralReport.create({
      data: { userId, referralId, reason: data.reason, detail: data.detail, status: 'pending' },
    });
  }

  async reportExpired(id: string) {
    return this.prisma.referral.update({
      where: { id },
      data: { status: 'invalid', failCount: { increment: 1 } },
    });
  }

  async findByCode(code: string) {
    return this.prisma.referral.findFirst({ where: { referralCode: code, status: 'active' } });
  }

  // ===== Confidence Score Algorithm =====
  private calculateConfidence(params: {
    isEmployee: boolean; verifiedCount: number; successCount: number; failCount: number;
    avgScore?: number; fastResponse?: number; slowResponse?: number;
  }): number {
    let score = 50; // base

    // Employee bonus
    if (params.isEmployee) score += 15;

    // Verification history
    score += Math.min(params.verifiedCount * 5, 20);

    // Success rate
    const total = params.successCount + params.failCount;
    if (total > 0) {
      const rate = params.successCount / total;
      score += Math.round(rate * 15);
    }

    // Average user rating
    if (params.avgScore) {
      score += Math.round((params.avgScore / 5) * 10);
    }

    // Response speed
    if (params.fastResponse) score += Math.min(params.fastResponse * 3, 6);
    if (params.slowResponse) score -= Math.min(params.slowResponse * 2, 4);

    return Math.max(10, Math.min(100, score));
  }

  private getLevel(score: number): string {
    if (score >= 80) return '高可信';
    if (score >= 60) return '中等';
    return '低可信';
  }
}
