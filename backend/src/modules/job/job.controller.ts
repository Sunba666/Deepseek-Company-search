import { Controller, Get, Param, Query } from '@nestjs/common';
import { JobService } from './job.service';
import { Public } from '../../common/decorators/public.decorator';

@Controller('api/v1/jobs')
export class JobController {
  constructor(private jobService: JobService) {}
  @Public() @Get()
  findAll(@Query() q: any) { return this.jobService.findAll(q); }
  @Public() @Get('search')
  search(@Query('q') q: string) { return this.jobService.search(q); }
  @Public() @Get(':id')
  findById(@Param('id') id: string) { return this.jobService.findById(id); }
}
