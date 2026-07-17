import { Controller, Get, Patch, Param, Query, Body, UseGuards } from '@nestjs/common';
import { AdminService } from './admin.service';
import { JwtAuthGuard } from '../../common/guards/jwt-auth.guard';
import { RolesGuard } from '../../common/guards/roles.guard';
import { Roles } from '../../common/decorators/roles.decorator';

@Controller('api/v1/admin')
@UseGuards(JwtAuthGuard, RolesGuard)
@Roles('admin', 'super_admin')
export class AdminController {
  constructor(private adminService: AdminService) {}

  @Get('dashboard') getDashboard() { return this.adminService.getDashboard(); }
  @Get('users') listUsers(@Query('page') page?: string, @Query('limit') limit?: string) { return this.adminService.listUsers(parseInt(page || '1'), parseInt(limit || '20')); }
  @Patch('users/:id/role') updateUserRole(@Param('id') id: string, @Body('role') role: string) { return this.adminService.updateUserRole(id, role); }
  @Patch('users/:id/toggle-status') toggleUserStatus(@Param('id') id: string) { return this.adminService.toggleUserStatus(id); }
  @Get('jobs') listJobs(@Query('page') page?: string, @Query('limit') limit?: string) { return this.adminService.listJobs(parseInt(page || '1'), parseInt(limit || '20')); }
  @Patch('jobs/:id/toggle-status') toggleJobStatus(@Param('id') id: string) { return this.adminService.toggleJobStatus(id); }
  @Get('ai-config') getAIConfig() { return this.adminService.getAIConfig(); }
  @Get('logs') getLogs(@Query('page') page?: string, @Query('limit') limit?: string) { return this.adminService.getLogs(parseInt(page || '1'), parseInt(limit || '50')); }
}
