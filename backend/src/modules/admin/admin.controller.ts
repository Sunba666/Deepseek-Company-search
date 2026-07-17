import { Controller, Get, Patch, Post, Param, Query, Body } from '@nestjs/common';
import { AdminService } from './admin.service';
import { Public } from '../../common/decorators/public.decorator';

@Controller('api/v1/admin')
export class AdminController {
  constructor(private adminService: AdminService) {}

  @Public() @Get('dashboard') getDashboard() { return this.adminService.getDashboard(); }
  @Public() @Get('users') listUsers(@Query('page') page?: string, @Query('limit') limit?: string) { return this.adminService.listUsers(parseInt(page || '1'), parseInt(limit || '20')); }
  @Public() @Patch('users/:id/role') updateUserRole(@Param('id') id: string, @Body('role') role: string) { return this.adminService.updateUserRole(id, role); }
  @Public() @Patch('users/:id/toggle-status') toggleUserStatus(@Param('id') id: string) { return this.adminService.toggleUserStatus(id); }
  @Public() @Get('jobs') listJobs(@Query('page') page?: string, @Query('limit') limit?: string) { return this.adminService.listJobs(parseInt(page || '1'), parseInt(limit || '20')); }
  @Public() @Patch('jobs/:id/toggle-status') toggleJobStatus(@Param('id') id: string) { return this.adminService.toggleJobStatus(id); }
  @Public() @Get('ai-config') getAIConfig() { return this.adminService.getAIConfig(); }
  @Public() @Get('logs') getLogs(@Query('page') page?: string, @Query('limit') limit?: string) { return this.adminService.getLogs(parseInt(page || '1'), parseInt(limit || '50')); }

  // Enterprise: create job
  @Public() @Post('jobs')
  createJob(@Body() body: any) { return this.adminService.createJob(body); }
}
