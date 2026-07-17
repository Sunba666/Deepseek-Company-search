import { Controller, Get, Post, Body } from '@nestjs/common';
import { AnalyticsService } from './analytics.service';
import { Public } from '../../common/decorators/public.decorator';
import { JwtAuthGuard } from '../../common/guards/jwt-auth.guard';
import { UseGuards } from '@nestjs/common';

@Controller('api/v1/analytics')
export class AnalyticsController {
  constructor(private analyticsService: AnalyticsService) {}
  @Public() @Post('track')
  track(@Body() body: any) { return this.analyticsService.track(body); }
  @UseGuards(JwtAuthGuard) @Get('dashboard')
  getDashboard() { return this.analyticsService.getDashboard(); }
}
