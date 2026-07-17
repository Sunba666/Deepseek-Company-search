import { Injectable } from '@nestjs/common';

@Injectable()
export class EventsGateway {
  private clients = new Map<string, any>();
  addClient(userId: string, client: any) { this.clients.set(userId, client); }
  removeClient(userId: string) { this.clients.delete(userId); }
  async emit(userId: string, event: string, data: any) { const c = this.clients.get(userId); if (c) c.emit(event, data); }
  async broadcast(event: string, data: any) { for (const c of this.clients.values()) c.emit(event, data); }
}
