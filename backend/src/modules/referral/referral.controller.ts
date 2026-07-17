import { Controller, Get, Param, Query, Post, Body } from '@nestjs/common';
import { ReferralService } from './referral.service';
import { Public } from '../../common/decorators/public.decorator';

@Controller('api/v1/referrals')
export class ReferralController {
  constructor(private referralService: ReferralService) {}
  @Public() @Get()
  findAll(@Query() q: any) { return this.referralService.findAll(q); }
  @Public() @Get(':id') findById(@Param('id') id: string) { return this.referralService.findById(id); }
  @Public() @Get('code/:code') findByCode(@Param('code') code: string) { return this.referralService.findByCode(code); }
  @Post(':id/expired') reportExpired(@Param('id') id: string) { return this.referralService.reportExpired(id); }
}
