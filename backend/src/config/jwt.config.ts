import { registerAs } from '@nestjs/config';
export default registerAs('jwt', () => ({
  secret: process.env.JWT_SECRET || 'dev-secret',
  expiresIn: parseInt(process.env.JWT_EXPIRES_IN || '7200', 10),
  refreshExpiresIn: parseInt(process.env.JWT_REFRESH_EXPIRES_IN || '604800', 10),
}));
