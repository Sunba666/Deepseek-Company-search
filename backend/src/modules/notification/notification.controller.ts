import { Controller, Get, Patch, Query, Body, UseGuards } from '@nestjs/common';
import { NotificationService } from './notification.service';
import { JwtAuthGuard } from '../../common/guards/jwt-auth.guard';
import { CurrentUser } from '../../common/decorators/current-user.decorator';

@Controller('api/v1/notifications')
@UseGuards(JwtAuthGuard)
export class NotificationController {
  constructor(private notifService: NotificationService) {}
  @Get() findAll(@CurrentUser('id') uid: string, @Query('unread_only') unread?: string) { return this.notifService.findAll(uid, unread === 'true'); }
  @Patch('read') markRead(@CurrentUser('id') uid: string, @Body('ids') ids?: string[]) { return this.notifService.markRead(uid, ids); }
  @Get('unread-count') unreadCount(@CurrentUser('id') uid: string) { return this.notifService.unreadCount(uid); }
}
