import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication, ValidationPipe } from '@nestjs/common';
import request from 'supertest';
import { AppModule } from '../src/app.module';

describe('JobNav AI API (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({ imports: [AppModule] }).compile();
    app = moduleFixture.createNestApplication();
    app.useGlobalPipes(new ValidationPipe({ whitelist: true }));
    await app.init();
  });

  afterAll(async () => { await app.close(); });

  describe('Auth', () => {
    it('POST /api/v1/auth/register', async () => {
      const res = await request(app.getHttpServer()).post('/api/v1/auth/register').send({ email: 'test@test.com', password: 'Test123!', nickname: 'Tester' });
      expect(res.status).toBe(201);
      expect(res.body.code).toBe(0);
      expect(res.body.data.access_token).toBeDefined();
    });

    it('POST /api/v1/auth/login', async () => {
      const res = await request(app.getHttpServer()).post('/api/v1/auth/login').send({ email: 'test@test.com', password: 'Test123!' });
      expect(res.status).toBe(200);
      expect(res.body.data.access_token).toBeDefined();
    });
  });

  describe('Companies', () => {
    it('GET /api/v1/companies', async () => {
      const res = await request(app.getHttpServer()).get('/api/v1/companies');
      expect(res.status).toBe(200);
      expect(res.body.code).toBe(0);
    });
  });

  describe('Jobs', () => {
    it('GET /api/v1/jobs', async () => {
      const res = await request(app.getHttpServer()).get('/api/v1/jobs');
      expect(res.status).toBe(200);
      expect(res.body.data).toBeInstanceOf(Array);
    });
  });

  describe('Health', () => {
    it('GET /api/v1/health', async () => {
      const res = await request(app.getHttpServer()).get('/api/v1/health');
      expect(res.status).toBe(200);
      expect(res.body.status).toBe('ok');
    });
  });
});
