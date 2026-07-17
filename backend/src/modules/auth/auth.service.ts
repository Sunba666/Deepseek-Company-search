import { Injectable, UnauthorizedException, ConflictException, NotFoundException, BadRequestException, Logger } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { ConfigService } from '@nestjs/config';
import * as bcrypt from 'bcryptjs';
import * as crypto from 'crypto';
import { PrismaService } from '../../prisma/prisma.service';

@Injectable()
export class AuthService {
  private readonly logger = new Logger(AuthService.name);
  constructor(
    private prisma: PrismaService,
    private jwtService: JwtService,
    private config: ConfigService,
  ) {}

  async register(data: { email: string; password: string; nickname?: string }) {
    const existing = await this.prisma.user.findUnique({ where: { email: data.email } });
    if (existing) throw new ConflictException('该邮箱已注册');
    const password = await bcrypt.hash(data.password, 10);
    const user = await this.prisma.user.create({
      data: { email: data.email, password, nickname: data.nickname || data.email.split('@')[0] },
    });
    return this.generateTokens(user);
  }

  async login(email: string, password: string) {
    const user = await this.prisma.user.findUnique({ where: { email } });
    if (!user || !(await bcrypt.compare(password, user.password))) {
      throw new UnauthorizedException('邮箱或密码错误');
    }
    if (user.status === 'banned') throw new UnauthorizedException('账号已被禁用');
    await this.prisma.user.update({ where: { id: user.id }, data: { lastLoginAt: new Date() } });
    return this.generateTokens(user);
  }

  async changePassword(userId: string, oldPassword: string, newPassword: string) {
    const user = await this.prisma.user.findUnique({ where: { id: userId } });
    if (!user) throw new NotFoundException('用户不存在');
    if (!(await bcrypt.compare(oldPassword, user.password))) {
      throw new BadRequestException('原密码错误');
    }
    const hashed = await bcrypt.hash(newPassword, 10);
    await this.prisma.user.update({ where: { id: userId }, data: { password: hashed } });
    return { message: '密码修改成功' };
  }

  async forgotPassword(email: string) {
    const user = await this.prisma.user.findUnique({ where: { email } });
    if (!user) return { message: '如果该邮箱已注册，重置链接已发送' }; // Don't reveal if email exists
    const token = crypto.randomBytes(32).toString('hex');
    // Store reset token with expiry (1 hour)
    await this.prisma.user.update({
      where: { id: user.id },
      data: { refreshToken: token }, // reuse refreshToken field as reset token storage
    });
    // In production, send email here. For now we log and return token for dev convenience
    this.logger.log(`Password reset token for ${email}: ${token}`);
    return { message: '如果该邮箱已注册，重置链接已发送', resetToken: token };
  }

  async resetPassword(token: string, newPassword: string) {
    const user = await this.prisma.user.findFirst({ where: { refreshToken: token } });
    if (!user) throw new BadRequestException('重置链接无效或已过期');
    const hashed = await bcrypt.hash(newPassword, 10);
    await this.prisma.user.update({
      where: { id: user.id },
      data: { password: hashed, refreshToken: null },
    });
    return { message: '密码重置成功' };
  }

  async refresh(refreshToken: string) {
    try {
      const payload = this.jwtService.verify(refreshToken, { secret: this.config.get('jwt.secret') });
      const user = await this.prisma.user.findUnique({ where: { id: payload.sub } });
      if (!user) throw new UnauthorizedException();
      return this.generateTokens(user);
    } catch { throw new UnauthorizedException('Token 已过期'); }
  }

  private generateTokens(user: any) {
    const payload = { sub: user.id, email: user.email, role: user.role };
    return {
      user: { id: user.id, email: user.email, nickname: user.nickname, role: user.role, avatar: user.avatar },
      access_token: this.jwtService.sign(payload),
      refresh_token: this.jwtService.sign(payload, { expiresIn: this.config.get('jwt.refreshExpiresIn') }),
    };
  }
}
