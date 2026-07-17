import { NestFactory } from '@nestjs/core';
import { ValidationPipe, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import helmet from 'helmet';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  const config = app.get(ConfigService);
  const logger = new Logger('Bootstrap');

  // === Startup Config Check ===
  const aiKey = config.get("ai.apiKey") || process.env.AI_API_KEY || "";
  if (!aiKey || aiKey.startsWith("sk-your-")) {
    logger.warn("AI_API_KEY is missing or using placeholder - AI features will fail with 401");
    logger.warn("  Set a valid API key in backend/.env: AI_API_KEY=sk-xxx");
  } else {
    logger.log("AI_API_KEY loaded: " + aiKey.slice(0, 8) + "...");
  }
  // ===========================

  // Security
  app.use(helmet());
  app.enableCors({ origin: config.get('app.corsOrigin'), credentials: true });

  // Validation
  app.useGlobalPipes(new ValidationPipe({ whitelist: true, forbidNonWhitelisted: true, transform: true }));

  // Swagger
  const swaggerConfig = new DocumentBuilder()
    .setTitle('JobNav AI API')
    .setDescription('AI 求职导航平台 API 文档')
    .setVersion('1.0')
    .addBearerAuth()
    .build();
  const document = SwaggerModule.createDocument(app, swaggerConfig);
  SwaggerModule.setup('api/docs', app, document);

  const port = config.get('app.port');
  await app.listen(port);
  logger.log(`Server running on http://localhost:${port}`);
  logger.log(`API docs: http://localhost:${port}/api/docs`);
}
bootstrap();
