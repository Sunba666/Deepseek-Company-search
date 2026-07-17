import { PrismaClient } from '@prisma/client';
import * as bcrypt from 'bcryptjs';

const prisma = new PrismaClient();

async function main() {
  console.log('Seeding database...');

  // Users
  const adminPwd = await bcrypt.hash('admin123', 10);
  const user1 = await prisma.user.upsert({
    where: { email: 'admin@jobnav.ai' },
    update: {},
    create: { email: 'admin@jobnav.ai', password: adminPwd, nickname: '管理员', role: 'super_admin', status: 'active' },
  });

  // Companies
  const companies = [
    { name: '字节跳动', slug: 'bytedance', industry: '互联网', city: '北京', scale: '2000+', stage: '独角兽', hiringCount: 128, averageSalary: 45, isUnicorn: true },
    { name: '腾讯', slug: 'tencent', industry: '互联网', city: '深圳', scale: '2000+', stage: '上市公司', hiringCount: 95, averageSalary: 42, isListed: true },
    { name: '阿里巴巴', slug: 'alibaba', industry: '电商', city: '杭州', scale: '2000+', stage: '上市公司', hiringCount: 82, averageSalary: 40, isListed: true },
    { name: '美团', slug: 'meituan', industry: '互联网', city: '北京', scale: '2000+', stage: '上市公司', hiringCount: 45, averageSalary: 38, isListed: true },
    { name: 'DeepSeek', slug: 'deepseek', industry: 'AI', city: '杭州', scale: '200-500', stage: 'A轮', hiringCount: 12, averageSalary: 60 },
  ];
  for (const c of companies) {
    await prisma.company.upsert({ where: { slug: c.slug }, update: {}, create: c });
  }

  // Jobs
  const byteDance = await prisma.company.findUnique({ where: { slug: 'bytedance' } });
  const tencent = await prisma.company.findUnique({ where: { slug: 'tencent' } });
  if (byteDance && tencent) {
    await prisma.job.createMany({
      data: [
        { companyId: byteDance.id, companyName: '字节跳动', title: 'AI算法工程师', category: 'AI', subCategory: '大模型', city: '上海', salaryMin: 50, salaryMax: 80, experience: '3-5年', education: '硕士', skills: ['Python', 'PyTorch', 'Transformer', '大模型'], isActive: true, publishedAt: new Date() },
        { companyId: byteDance.id, companyName: '字节跳动', title: 'Java后端开发', category: '研发', subCategory: 'Java', city: '深圳', salaryMin: 30, salaryMax: 60, experience: '3-5年', education: '本科', skills: ['Java', 'Spring Boot', 'MySQL', 'Redis'], isActive: true, publishedAt: new Date(Date.now() - 86400000) },
        { companyId: tencent.id, companyName: '腾讯', title: '前端开发工程师', category: '研发', subCategory: '前端', city: '深圳', salaryMin: 25, salaryMax: 50, experience: '3-5年', education: '本科', skills: ['React', 'TypeScript', 'Node.js'], isActive: true, publishedAt: new Date(Date.now() - 2 * 86400000) },
        { companyId: tencent.id, companyName: '腾讯', title: '产品经理', category: '产品', subCategory: '产品经理', city: '广州', salaryMin: 25, salaryMax: 45, experience: '3-5年', education: '本科', skills: ['产品策略', '数据分析', '用户研究'], isActive: true, publishedAt: new Date(Date.now() - 3 * 86400000) },
      ],
    });
  }

  // Referrals
  const jobs = await prisma.job.findMany({ take: 2 });
  for (let i = 0; i < jobs.length && i < 2; i++) {
    await prisma.referral.create({
      data: {
        companyId: jobs[i].companyId,
        companyName: jobs[i].companyName,
        jobId: jobs[i].id,
        referralCode: i === 0 ? 'NTABkC8' : 'ABC123',
        referrerName: i === 0 ? '张三' : '李四',
        isEmployee: i === 0,
        confidenceScore: i === 0 ? 95 : 70,
        confidenceLevel: i === 0 ? '高可信' : '中等',
        isVerified: i === 0,
        source: '脉脉',
        status: 'active',
        publishedAt: new Date(Date.now() - i * 86400000),
      },
    });
  }

  console.log('Seed completed!');
}
main()
  .catch((e) => { console.error(e); process.exit(1); })
  .finally(async () => { await prisma.$disconnect(); });
