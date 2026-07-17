import { Injectable, Logger } from '@nestjs/common';
import Redis from 'ioredis';

@Injectable()
export class RedisService {
  private readonly logger = new Logger(RedisService.name);
  public client: Redis;
  private hits = 0; private misses = 0;

  constructor() {
    const url = process.env.REDIS_URL || 'redis://localhost:6379';
    this.client = new Redis(url);
    this.client.on('connect', () => this.logger.log('Redis connected'));
    this.client.on('error', (err) => this.logger.warn('Redis error: ' + err.message));
  }

  async get(key: string): Promise<string | null> {
    try { const v = await this.client.get(key); if (v) this.hits++; else this.misses++; return v; } catch { this.misses++; return null; }
  }

  async set(key: string, value: string, ttlSeconds?: number): Promise<void> {
    try { if (ttlSeconds) await this.client.setex(key, ttlSeconds, value); else await this.client.set(key, value); } catch {}
  }

  async del(key: string): Promise<void> { try { await this.client.del(key); } catch {} }

  getStats() { return { hits: this.hits, misses: this.misses, hitRate: this.hits + this.misses > 0 ? (this.hits / (this.hits + this.misses) * 100).toFixed(1) + '%' : 'N/A' }; }
}
