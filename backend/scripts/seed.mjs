import { PrismaClient } from '@prisma/client';
import * as bcrypt from 'bcryptjs';
const prisma = new PrismaClient();
async function main() {
  const adminPwd = await bcrypt.hash('admin123', 10);
  await prisma.user.upsert({ where: { email: 'admin@jobnav.ai' }, update: {}, create: { email: 'admin@jobnav.ai', password: adminPwd, nickname: '管理员', role: 'super_admin', status: 'active' } });
  console.log('Seed: admin user created');
}
main().catch(e => { console.error(e); process.exit(1); }).finally(() => prisma.$disconnect());
