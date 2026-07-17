import { Controller, Get, Patch, Post, Delete, Param, Body, UseGuards } from '@nestjs/common';
import { UserService } from './user.service';
import { Public } from '../../common/decorators/public.decorator';

@Controller('api/v1/users')
export class UserController {
  constructor(private userService: UserService) {}

  @Public() @Get('me')
  getProfile(@Body() body: any) { return this.userService.getProfile(body.userId || 'anonymous'); }

  @Public() @Patch('me')
  updateProfile(@Body() body: any) { return this.userService.updateProfile(body.userId || 'anonymous', body); }

  @Public() @Get('me/stats')
  getStats(@Body() body: any) { return this.userService.getStats(body.userId || 'anonymous'); }

  // Resume management
  @Public() @Get('me/resumes')
  listResumes(@Body() body: any) { return this.userService.listResumes(body.userId || 'anonymous'); }

  @Public() @Post('me/resumes')
  createResume(@Body() body: any) { return this.userService.createResume(body.userId || 'anonymous', body); }

  @Public() @Delete('me/resumes/:id')
  deleteResume(@Param('id') id: string, @Body() body: any) { return this.userService.deleteResume(id, body.userId || 'anonymous'); }

  // Avatar
  @Public() @Post('me/avatar')
  updateAvatar(@Body() body: any) { return this.userService.updateAvatar(body.userId || 'anonymous', body.avatarUrl); }
}
