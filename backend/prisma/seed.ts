import { PrismaClient } from '@prisma/client';
import * as bcrypt from 'bcryptjs';

const prisma = new PrismaClient();

async function main() {
  console.log('Seeding database...');

  // Users
  const pwd = await bcrypt.hash('admin123', 10);
  await prisma.user.upsert({
    where: { email: 'admin@jobnav.ai' },
    update: {},
    create: { email: 'admin@jobnav.ai', password: pwd, nickname: '管理员', role: 'super_admin', status: 'active' },
  });
  await prisma.user.upsert({
    where: { email: 'user@jobnav.ai' },
    update: {},
    create: { email: 'user@jobnav.ai', password: pwd, nickname: '求职者小明', role: 'user', status: 'active', skills: ['Python', 'Java'], yearsExp: 3, currentCity: '北京' },
  });
  console.log('Users: admin@jobnav.ai / user@jobnav.ai (password: admin123)');

  // Companies
  const companies = [
    { name: '字节跳动', slug: 'bytedance', industry: '互联网', city: '北京', scale: '2000+', stage: '独角兽', hiringCount: 128, averageSalary: 45 },
    { name: '腾讯', slug: 'tencent', industry: '互联网', city: '深圳', scale: '2000+', stage: '上市公司', hiringCount: 95, averageSalary: 42 },
    { name: '阿里巴巴', slug: 'alibaba', industry: '电商', city: '杭州', scale: '2000+', stage: '上市公司', hiringCount: 82, averageSalary: 40 },
    { name: '美团', slug: 'meituan', industry: '互联网', city: '北京', scale: '2000+', stage: '上市公司', hiringCount: 45, averageSalary: 38 },
    { name: 'DeepSeek', slug: 'deepseek', industry: 'AI', city: '杭州', scale: '200-500', stage: 'A轮', hiringCount: 12, averageSalary: 60 },
    { name: '小红书', slug: 'xiaohongshu', industry: '社区', city: '上海', scale: '1000-2000', stage: 'D轮', hiringCount: 28, averageSalary: 38 },
    { name: '快手', slug: 'kuaishou', industry: '互联网', city: '北京', scale: '2000+', stage: '上市公司', hiringCount: 25, averageSalary: 36 },
  ];
  for (const c of companies) {
    await prisma.company.upsert({ where: { slug: c.slug }, update: {}, create: c });
  }
  console.log('Companies:', companies.length);

  // Jobs
  const jobsData = [
    { slug: 'bytedance', title: 'AI算法工程师', cat: 'AI', sub: '大模型', city: '上海', min: 50, max: 80, exp: '3-5年', edu: '硕士', skills: ['Python', 'PyTorch', 'Transformer'] },
    { slug: 'bytedance', title: 'Java后端开发', cat: '研发', sub: 'Java', city: '深圳', min: 30, max: 60, exp: '3-5年', edu: '本科', skills: ['Java', 'Spring Boot', 'MySQL'] },
    { slug: 'tencent', title: '前端开发工程师', cat: '研发', sub: '前端', city: '深圳', min: 25, max: 50, exp: '3-5年', edu: '本科', skills: ['React', 'TypeScript', 'Node.js'] },
    { slug: 'tencent', title: '产品经理', cat: '产品', sub: '产品经理', city: '广州', min: 25, max: 45, exp: '3-5年', edu: '本科', skills: ['产品策略', '数据分析'] },
    { slug: 'alibaba', title: '算法专家', cat: 'AI', sub: '推荐算法', city: '杭州', min: 60, max: 100, exp: '5年以上', edu: '硕士', skills: ['推荐系统', 'C++', 'TensorFlow'] },
    { slug: 'deepseek', title: '大模型研究员', cat: 'AI', sub: '大模型', city: '杭州', min: 50, max: 90, exp: '3-5年', edu: '硕士', skills: ['Python', 'CUDA', 'LLM'] },
  ];
  for (const jd of jobsData) {
    const c = await prisma.company.findUnique({ where: { slug: jd.slug } });
    if (c) {
      await prisma.job.create({
        data: { companyId: c.id, companyName: c.name, title: jd.title, category: jd.cat, subCategory: jd.sub, city: jd.city, salaryMin: jd.min, salaryMax: jd.max, experience: jd.exp, education: jd.edu, skills: jd.skills, isActive: true, publishedAt: new Date() },
      });
    }
  }
  console.log('Jobs: 6');

  // Referrals — fresh seed
  await prisma.referralFavorite.deleteMany();
  await prisma.referralRating.deleteMany();
  await prisma.referralReport.deleteMany();
  await prisma.referral.deleteMany();

  const refs = [
    { code: 'NTABkC8', slug: 'bytedance', jobIdx: 0, name: '张三', title: '高级工程师', emp: true, score: 95, src: '脉脉', verified: true },
    { code: 'ABC123', slug: 'tencent', jobIdx: 2, name: '李四', title: '前端工程师', emp: true, score: 88, src: '知乎', verified: true },
    { code: 'XYZ789', slug: 'alibaba', jobIdx: 4, name: '王五', title: '技术专家', emp: true, score: 72, src: '脉脉', verified: true },
    { code: 'DEF456', slug: 'bytedance', jobIdx: 0, name: '赵六', title: '产品总监', emp: true, score: 90, src: '内推', verified: false },
    { code: 'GHI012', slug: 'tencent', jobIdx: 3, name: '孙七', title: 'HR', emp: true, score: 65, src: '知乎', verified: false },
    { code: 'JKL345', slug: 'deepseek', jobIdx: 5, name: '周八', title: '研究员', emp: false, score: 82, src: '牛客', verified: false },
    { code: 'MNO678', slug: 'bytedance', jobIdx: 1, name: '吴九', title: '后端工程师', emp: true, score: 78, src: '脉脉', verified: true },
    { code: 'PQR901', slug: 'tencent', jobIdx: 2, name: '郑十', title: '工程师', emp: true, score: 85, src: '朋友圈', verified: true },
    { code: 'STU234', slug: 'xiaohongshu', jobIdx: 2, name: '陈一', title: '社区运营', emp: false, score: 70, src: '小红书', verified: false },
    { code: 'VWX567', slug: 'kuaishou', jobIdx: 1, name: '林二', title: '架构师', emp: true, score: 92, src: '脉脉', verified: true },
  ];

  for (let i = 0; i < refs.length; i++) {
    const r = refs[i];
    const company = await prisma.company.findUnique({ where: { slug: r.slug } });
    if (!company) continue;
    const jobs = await prisma.job.findMany({ where: { companyId: company.id }, take: 1 });
    const job = jobs[r.jobIdx] || jobs[0];
    if (!job) continue;

    await prisma.referral.create({
      data: {
        companyId: company.id, companyName: company.name,
        jobId: job.id,
        referralCode: r.code,
        referralLink: i < 5 ? 'https://jobnav.ai/refer/' + r.code : null,
        referrerName: r.name,
        referrerTitle: r.title,
        isEmployee: r.emp,
        isVerified: r.verified,
        confidenceScore: r.score,
        confidenceLevel: r.score >= 80 ? '高可信' : r.score >= 60 ? '中等' : '低可信',
        verifiedCount: r.verified ? 3 + i : 0,
        successCount: i < 5 ? 2 + Math.floor(i / 2) : 1,
        failCount: i > 6 ? i - 5 : 0,
        source: r.src,
        status: 'active',
        publishedAt: new Date(Date.now() - i * 2 * 86400000),
      },
    });
  }
  console.log('Referrals: ' + refs.length);

  console.log('Seed completed!');
}

main()
  .catch((e) => { console.error(e); process.exit(1); })
  .finally(async () => { await prisma.$disconnect(); });
