import { Controller, Get, Post, Patch, Param, Query, Body } from '@nestjs/common';
import { ApplicationService } from './application.service';
import { Public } from '../../common/decorators/public.decorator';

@Controller('api/v1/applications')
export class ApplicationController {
  constructor(private appService: ApplicationService) {}

  @Public() @Get()
  findAll(@Query() q: any) { return this.appService.findAll('anonymous', q); }

  @Public() @Get('stats')
  getStats() { return this.appService.getStats('anonymous'); }

  @Public() @Get(':id')
  findById(@Param('id') id: string) { return this.appService.findById('anonymous', id); }

  @Public() @Post()
  create(@Body() b: any) { return this.appService.create('anonymous', b); }

  @Public() @Patch(':id/status')
  updateStatus(@Param('id') id: string, @Body('status') s: string) { return this.appService.updateStatus('anonymous', id, s); }

  @Public() @Patch(':id/notes')
  updateNotes(@Param('id') id: string, @Body() b: any) { return this.appService.updateNotes('anonymous', id, b); }

  // Interview records
  @Public() @Get(':id/interviews')
  getInterviews(@Param('id') id: string) { return this.appService.getInterviews(id); }

  @Public() @Post(':id/interviews')
  addInterview(@Param('id') id: string, @Body() b: any) { return this.appService.addInterview(id, b); }
}
