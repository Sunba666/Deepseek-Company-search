import { Controller, Get, Query } from '@nestjs/common';
import { SearchService } from './search.service';
import { Public } from '../../common/decorators/public.decorator';

@Controller('api/v1/search')
export class SearchController {
  constructor(private searchService: SearchService) {}
  @Public() @Get()
  search(@Query('q') q: string) { return this.searchService.search(q); }
  @Public() @Get('ai')
  aiSearch(@Query('q') q: string) { return this.searchService.aiSearch(q); }
}
