import { Controller, Get, Param, Query } from '@nestjs/common';
import { CompanyService } from './company.service';
import { Public } from '../../common/decorators/public.decorator';

@Controller('api/v1/companies')
export class CompanyController {
  constructor(private companyService: CompanyService) {}

  @Public()
  @Get()
  findAll(@Query('page') page?: string, @Query('limit') limit?: string, @Query('industry') industry?: string, @Query('city') city?: string) {
    return this.companyService.findAll({ page: page ? parseInt(page) : 1, limit: limit ? parseInt(limit) : 20, industry, city });
  }

  @Public()
  @Get(':slug')
  findBySlug(@Param('slug') slug: string) { return this.companyService.findBySlug(slug); }

  @Public()
  @Get(':slug/jobs')
  getJobs(@Param('slug') slug: string, @Query('category') category?: string) { return this.companyService.getJobs(slug, { category }); }
}
