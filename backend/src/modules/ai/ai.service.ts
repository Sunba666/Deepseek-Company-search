import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';

interface AiMessage { role: 'system' | 'user' | 'assistant'; content: string; }
interface AiRequest { messages: AiMessage[]; model?: string; temperature?: number; maxTokens?: number; stream?: boolean; }

@Injectable()
export class AiService {
  private readonly logger = new Logger(AiService.name);
  private provider: string; private model: string; private apiKey: string;

  constructor(private config: ConfigService) {
    this.provider = this.config.get('ai.provider') || 'deepseek';
    this.model = this.config.get('ai.model') || 'deepseek-chat';
    this.apiKey = this.config.get('ai.apiKey') || '';
  }

  private getBaseUrl(): string {
    const urls: Record<string, string> = { deepseek: 'https://api.deepseek.com/v1', openai: 'https://api.openai.com/v1' };
    return urls[this.provider] || urls.deepseek;
  }

  async complete(req: AiRequest) {
    const start = Date.now();
    const res = await fetch(`${this.getBaseUrl()}/chat/completions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${this.apiKey || process.env.AI_API_KEY || ''}` },
      body: JSON.stringify({ model: req.model || this.model, messages: req.messages, temperature: req.temperature ?? 0.7, max_tokens: req.maxTokens ?? 4096 }),
    });
    if (!res.ok) throw new Error(`AI API error: ${res.status}`);
    const json = await res.json();
    this.logger.log(`AI complete: ${Date.now() - start}ms, tokens: ${json.usage?.total_tokens || '?'}`);
    return { content: json.choices[0].message.content, model: json.model, usage: json.usage };
  }

  async* stream(req: AiRequest): AsyncGenerator<string, void, unknown> {
    const res = await fetch(`${this.getBaseUrl()}/chat/completions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${this.apiKey || process.env.AI_API_KEY || ''}` },
      body: JSON.stringify({ model: req.model || this.model, messages: req.messages, temperature: req.temperature ?? 0.7, max_tokens: req.maxTokens ?? 4096, stream: true }),
    });
    if (!res.ok) throw new Error(`AI stream error: ${res.status}`);
    const reader = res.body?.getReader();
    if (!reader) throw new Error('No response body');
    const decoder = new TextDecoder();
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      for (const line of decoder.decode(value).split('\n').filter((l: string) => l.startsWith('data: '))) {
        const data = line.slice(6);
        if (data === '[DONE]') return;
        try { const c = JSON.parse(data).choices?.[0]?.delta?.content; if (c) yield c; } catch {}
      }
    }
  }

  async analyzeJD(jdContent: string, resumeSummary?: string) {
    const prompt = `你是一个求职顾问。请分析以下JD：
${jdContent}
${resumeSummary ? `\n用户简历摘要：${resumeSummary}` : ''}
请输出结构化分析：1.匹配度 2.已具备技能 3.缺失技能 4.学习建议 5.简历优化建议`;
    return this.complete({ messages: [{ role: 'system', content: '你是一个专业的求职分析AI。' }, { role: 'user', content: prompt }] });
  }

  async recommendJobs(skills: string, experience: string, city: string, jobs: string) {
    const prompt = `根据以下信息推荐最适合的岗位：\n技能：${skills}\n经验：${experience}\n城市：${city}\n\n可选岗位：${jobs}\n请按匹配度排序输出推荐结果。`;
    return this.complete({ messages: [{ role: 'system', content: '你是一个AI求职顾问，分析用户背景并推荐最适合的岗位。' }, { role: 'user', content: prompt }] });
  }
}
