import { Controller, Get, Post, Patch, Param, Query, Body, UseGuards } from '@nestjs/common';
import { ApplicationService } from './application.service';
import { JwtAuthGuard } from '../../common/guards/jwt-auth.guard';
import { CurrentUser } from '../../common/decorators/current-user.decorator';

@Controller('api/v1/applications')
@UseGuards(JwtAuthGuard)
export class ApplicationController {
  constructor(private appService: ApplicationService) {}
  @Get() findAll(@CurrentUser('id') uid: string, @Query() q: any) { return this.appService.findAll(uid, q); }
  @Post() create(@CurrentUser('id') uid: string, @Body() b: any) { return this.appService.create(uid, b); }
  @Patch(':id/status') updateStatus(@CurrentUser('id') uid: string, @Param('id') id: string, @Body('status') s: string) { return this.appService.updateStatus(uid, id, s); }
  @Get('stats') getStats(@CurrentUser('id') uid: string) { return this.appService.getStats(uid); }
}
