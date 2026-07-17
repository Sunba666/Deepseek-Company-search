import { Controller, Post, Body, HttpCode, HttpStatus, Patch, Param } from '@nestjs/common';
import { AuthService } from './auth.service';
import { Public } from '../../common/decorators/public.decorator';

@Controller('api/v1/auth')
export class AuthController {
  constructor(private authService: AuthService) {}

  @Public() @Post('register')
  async register(@Body() body: { email: string; password: string; nickname?: string }) {
    return this.authService.register(body);
  }

  @Public() @Post('login')
  @HttpCode(HttpStatus.OK)
  async login(@Body() body: { email: string; password: string }) {
    return this.authService.login(body.email, body.password);
  }

  @Public() @Post('refresh')
  @HttpCode(HttpStatus.OK)
  async refresh(@Body() body: { refresh_token: string }) {
    return this.authService.refresh(body.refresh_token);
  }

  @Public() @Post('change-password')
  @HttpCode(HttpStatus.OK)
  async changePassword(@Body() body: { userId: string; oldPassword: string; newPassword: string }) {
    return this.authService.changePassword(body.userId, body.oldPassword, body.newPassword);
  }

  @Public() @Post('forgot-password')
  @HttpCode(HttpStatus.OK)
  async forgotPassword(@Body() body: { email: string }) {
    return this.authService.forgotPassword(body.email);
  }

  @Public() @Post('reset-password')
  @HttpCode(HttpStatus.OK)
  async resetPassword(@Body() body: { token: string; newPassword: string }) {
    return this.authService.resetPassword(body.token, body.newPassword);
  }
}
