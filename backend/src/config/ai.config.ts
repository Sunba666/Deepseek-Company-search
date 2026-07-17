import { registerAs } from '@nestjs/config';
export default registerAs('ai', () => ({
  provider: process.env.AI_PROVIDER || 'deepseek',
  model: process.env.AI_MODEL || 'deepseek-chat',
  apiKey: process.env.AI_API_KEY || '',
}));
