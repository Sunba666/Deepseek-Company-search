import { Injectable, Logger } from '@nestjs/common';
@Injectable()
export class QueueService {
  private readonly logger = new Logger(QueueService.name);
  async addJob(name: string, data: any) { this.logger.log('Job queued: ' + name); return { queued: true, name, data }; }
  async getStats() { return { queued: 0, waiting: 0, active: 0, completed: 0, failed: 0 }; }
}
