import { Controller, Get, Patch, Body, UseGuards } from '@nestjs/common';
import { UserService } from './user.service';
import { JwtAuthGuard } from '../../common/guards/jwt-auth.guard';
import { CurrentUser } from '../../common/decorators/current-user.decorator';

@Controller('api/v1/users')
@UseGuards(JwtAuthGuard)
export class UserController {
  constructor(private userService: UserService) {}

  @Get('me')
  getProfile(@CurrentUser('id') userId: string) { return this.userService.getProfile(userId); }

  @Patch('me')
  updateProfile(@CurrentUser('id') userId: string, @Body() body: any) { return this.userService.updateProfile(userId, body); }

  @Get('me/stats')
  getStats(@CurrentUser('id') userId: string) { return this.userService.getStats(userId); }
}
