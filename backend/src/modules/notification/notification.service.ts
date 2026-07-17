import { Injectable } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';

@Injectable()
export class NotificationService {
  constructor(private prisma: PrismaService) {}

  async findAll(userId: string, unreadOnly = false) {
    const where: any = { userId };
    if (unreadOnly) where.isRead = false;
    return this.prisma.notification.findMany({ where, orderBy: { createdAt: 'desc' }, take: 50 });
  }

  async markRead(userId: string, ids?: string[]) {
    const where: any = { userId };
    if (ids?.length) where.id = { in: ids };
    return this.prisma.notification.updateMany({ where, data: { isRead: true, readAt: new Date() } });
  }

  async unreadCount(userId: string) {
    return { count: await this.prisma.notification.count({ where: { userId, isRead: false } }) };
  }

  async create(userId: string, data: { type: string; title: string; body?: string; link?: string }) {
    return this.prisma.notification.create({ data: { userId, ...data } });
  }
}
