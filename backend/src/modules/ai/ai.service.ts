import { Injectable, Logger, NotFoundException } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { PrismaService } from '../../prisma/prisma.service';

interface AiMessage { role: 'system' | 'user' | 'assistant'; content: string; }
interface AiRequest { messages: AiMessage[]; model?: string; temperature?: number; maxTokens?: number; stream?: boolean; }

@Injectable()
export class AiService {
  private readonly logger = new Logger(AiService.name);
  private provider: string; private model: string; private apiKey: string;

  constructor(private config: ConfigService, private prisma: PrismaService) {
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
      for (const line of decoder.decode(value).split('\n').filter((l) => l.startsWith('data: '))) {
        const data = line.slice(6);
        if (data === '[DONE]') return;
        try { const c = JSON.parse(data).choices?.[0]?.delta?.content; if (c) yield c; } catch {}
      }
    }
  }

  // ===== Conversation Persistence =====
  async createConversation(userId: string, title?: string) {
    return this.prisma.aIConversation.create({
      data: { userId, title: title || '新对话' },
    });
  }

  async listConversations(userId: string) {
    return this.prisma.aIConversation.findMany({
      where: { userId },
      orderBy: { updatedAt: 'desc' },
      include: { _count: { select: { messages: true } } },
    });
  }

  async getConversation(id: string) {
    const conv = await this.prisma.aIConversation.findUnique({
      where: { id },
      include: { messages: { orderBy: { createdAt: 'asc' } } },
    });
    if (!conv) throw new NotFoundException('对话不存在');
    return conv;
  }

  async deleteConversation(id: string) {
    await this.prisma.aIMessage.deleteMany({ where: { conversationId: id } });
    return this.prisma.aIConversation.delete({ where: { id } });
  }

  async toggleStarConversation(id: string) {
    const conv = await this.prisma.aIConversation.findUnique({ where: { id } });
    if (!conv) throw new NotFoundException('对话不存在');
    return this.prisma.aIConversation.update({
      where: { id }, data: { isStarred: !conv.isStarred },
    });
  }

  async saveMessage(conversationId: string, data: { role: string; content: string; tokenCount?: number; modelUsed?: string }) {
    return this.prisma.aIMessage.create({
      data: { ...data, conversationId },
    });
  }

  // ===== Chat with history saving =====
  async chatAndSave(conversationId: string, message: string) {
    const conv = await this.getConversation(conversationId);
    const history = conv.messages.map(m => ({ role: m.role as 'user' | 'assistant' | 'system', content: m.content }));
    const systemPrompt = { role: 'system' as const, content: '你是JobNav AI求职助手。你帮助求职者分析岗位、优化简历、推荐工作和准备面试。回答专业、简洁、有用。' };
    const result = await this.complete({ messages: [systemPrompt, ...history, { role: 'user', content: message }] });

    await this.saveMessage(conversationId, { role: 'user', content: message });
    await this.saveMessage(conversationId, { role: 'assistant', content: result.content, tokenCount: result.usage?.total_tokens, modelUsed: result.model });
    await this.prisma.aIConversation.update({ where: { id: conversationId }, data: { title: history.length === 0 ? message.substring(0, 30) : undefined } });

    return result;
  }

  // ===== Resume Analysis =====
  async analyzeResume(resumeText: string, skills?: string[]) {
    const prompt = `你是一个专业的求职顾问。请分析以下简历，提供结构化建议。

简历内容：
${resumeText}
${skills && skills.length > 0 ? `
已标注技能：${skills.join(', ')}` : ''}

请输出：
## 简历摘要
## 核心优势
## 改进建议（列表形式，每个建议附带说明）
## 岗位推荐方向
## 技能提升建议`;

    return this.complete({
      messages: [
        { role: 'system', content: '你是一个资深的HR和职业规划专家，擅长简历分析和优化。输出使用Markdown格式。' },
        { role: 'user', content: prompt },
      ],
    });
  }

  // ===== Mock Interview =====
  async mockInterview(params: { jobTitle: string; company?: string; skills?: string[]; question?: string; history?: { question: string; answer: string }[] }) {
    const { jobTitle, company, skills, question, history } = params;

    if (!question) {
      // Generate first question
      const prompt = `你是一个面试官，正在面试一个${jobTitle}岗位${company ? '（' + company + '）' : ''}的候选人。
${skills && skills.length > 0 ? `候选人技能：${skills.join(', ')}` : ''}
请为这个候选人出第一道面试题，包括考察方向说明。问题要有深度，考察实际能力。`;
      const result = await this.complete({
        messages: [{ role: 'system', content: '你是一个专业的技术面试官。每次只问一个问题。' }, { role: 'user', content: prompt }],
      });
      return { type: 'question', content: result.content, round: 1, total: 5 };
    }

    // Evaluate answer and ask next question
    const prevQuestions = history?.map((h, i) => `第${i + 1}轮：Q: ${h.question}\nA: ${h.answer}`).join('\n\n') || '';
    const currentRound = (history?.length || 0) + 1;
    const isLast = currentRound >= 5;

    const prompt = `你是一个面试官。正在进行${jobTitle}岗位的面试。
${company ? '公司：' + company : ''}

历史记录：
${prevQuestions}

候选人对当前问题的回答：
${question}

${isLast
  ? '这是最后一轮。请对候选人的整体表现进行评分（1-10分）和综合评价，包括：1.技术能力 2.沟通表达 3.问题解决能力 4.总体评分。'
  : '请先对候选人的回答给出简短反馈（优点和改进点），然后提出下一个面试问题。'}`;

    const result = await this.complete({
      messages: [{ role: 'system', content: '你是一个专业且严格的技术面试官。反馈要具体、有建设性。' }, { role: 'user', content: prompt }],
    });

    if (isLast) {
      return { type: 'evaluation', content: result.content, round: currentRound, total: 5 };
    }
    return { type: 'question', content: result.content, round: currentRound, total: 5 };
  }

  // ===== JD Analysis with structured output =====
  async analyzeJD(jdContent: string, resumeSummary?: string) {
    const prompt = `你是一个求职顾问。请分析以下JD：
${jdContent}
${resumeSummary ? `\n用户简历摘要：${resumeSummary}` : ''}
请输出结构化分析：
1.匹配度评分（0-100）
2.已具备技能
3.缺失技能
4.学习建议
5.简历优化建议`;
    return this.complete({ messages: [{ role: 'system', content: '你是一个专业的求职分析AI。' }, { role: 'user', content: prompt }] });
  }

  async recommendJobs(skills: string, experience: string, city: string, jobs: string) {
    const prompt = `根据以下信息推荐最适合的岗位：\n技能：${skills}\n经验：${experience}\n城市：${city}\n\n可选岗位：${jobs}\n请按匹配度排序输出推荐结果。`;
    return this.complete({ messages: [{ role: 'system', content: '你是一个AI求职顾问，分析用户背景并推荐最适合的岗位。' }, { role: 'user', content: prompt }] });
  }

  // ===== Search History Tracking =====
  async saveSearch(userId: string, data: { query: string; searchType?: string; resultCount?: number; clickedJobId?: string }) {
    return this.prisma.searchHistory.create({
      data: { userId, query: data.query, searchType: data.searchType || 'keyword', resultCount: data.resultCount, clickedJobId: data.clickedJobId },
    });
  }

  async getSearchHistory(userId: string, limit = 10) {
    return this.prisma.searchHistory.findMany({
      where: { userId }, orderBy: { createdAt: 'desc' }, take: limit,
    });
  }

  // ===== Personalized Recommendation Engine =====
  async personalizedRecommend(userId: string) {
    // 1. Fetch user profile
    const user = await this.prisma.user.findUnique({ where: { id: userId } });
    const skills = user?.skills || [];
    const city = user?.currentCity || '';
    const yearsExp = user?.yearsExp || 0;
    const salaryMin = user?.salaryMin || 0;
    const salaryMax = user?.salaryMax || 0;

    // 2. Fetch favorites (companies & jobs)
    const favorites = await this.prisma.favorite.findMany({
      where: { userId },
      include: { 
        ...({} as any),
      },
    });
    const favJobIds = favorites.filter(f => f.targetType === 'job').map(f => f.targetId);
    const favCompanyIds = favorites.filter(f => f.targetType === 'company').map(f => f.targetId);

    // 3. Fetch search history
    const recentSearches = await this.getSearchHistory(userId, 8);
    const searchKeywords = recentSearches.map(s => s.query).filter(Boolean);

    // 4. Fetch applications (to exclude already-applied jobs)
    const applications = await this.prisma.application.findMany({
      where: { userId, deletedAt: null },
      select: { jobId: true },
    });
    const appliedJobIds = new Set(applications.map(a => a.jobId));

    // 5. Fetch available jobs (exclude already applied)
    const availableJobs = await this.prisma.job.findMany({
      where: {
        isActive: true,
        id: { notIn: Array.from(appliedJobIds) },
        ...(city ? { city: { contains: city } } : {}),
      },
      take: 20,
      orderBy: { publishedAt: 'desc' },
      include: { company: { select: { id: true, name: true, slug: true, industry: true } } },
    });

    // 6. Fetch companies for recommendation
    const companies = await this.prisma.company.findMany({
      take: 10,
      orderBy: { hiringCount: 'desc' },
      select: { id: true, name: true, slug: true, industry: true, city: true, scale: true, stage: true, hiringCount: true },
    });

    // 7. Build AI prompt
    const jobList = availableJobs.slice(0, 15).map(j =>
      `- ${j.title} | ${j.company?.name || ''} | ${j.city} | ${j.salaryMin || '?'}K-${j.salaryMax || '?'}K | ${(j.skills || []).join(', ')}`
    ).join('\n');

    const companyList = companies.slice(0, 8).map(c =>
      `- ${c.name} | ${c.industry} | ${c.city} | ${c.stage} | 在招${c.hiringCount}人`
    ).join('\n');

    const prompt = `你是一个AI求职顾问。请根据用户的背景信息，推荐最合适的岗位和公司，并提供学习建议。

## 用户背景
- 技能：${skills.join(', ') || '未填写'}
- 城市：${city || '不限'}
- 经验：${yearsExp}年
- 期望薪资：${salaryMin}K-${salaryMax}K
- 近期搜索：${searchKeywords.slice(0, 5).join(', ') || '无'}
- 收藏公司数：${favCompanyIds.length}
- 收藏岗位数：${favJobIds.length}

## 可选岗位（${availableJobs.length}个）
${jobList || '暂无匹配岗位'}

## 热门公司
${companyList || '暂无'}

请按以下格式输出（使用JSON，不要加markdown代码块标记）：
{
  "jobRecommendations": [
    { "jobTitle": "...", "company": "...", "matchReason": "...", "matchScore": 0-100, "actionable": true/false }
  ],
  "companyRecommendations": [
    { "companyName": "...", "industry": "...", "reason": "...", "priority": "high|medium|low" }
  ],
  "learningSuggestions": [
    { "skill": "...", "importance": "high|medium|low", "resources": ["..."] }
  ],
  "summary": "一段总体推荐说明"
}`;

    const result = await this.complete({
      messages: [
        { role: 'system', content: '你是JobNav AI的推荐引擎。你总是输出纯JSON，不包含markdown代码块标记。分析用户背景后输出结构化的推荐结果。' },
        { role: 'user', content: prompt },
      ],
    });

    // Parse the JSON response
    try {
      const jsonStr = result.content.replace(/\```json?\n?/g, '').replace(/\```\n?/g, '').trim();
      const parsed = JSON.parse(jsonStr);

      // Save search history entry for recommendation
      await this.saveSearch(userId, { query: '个性化推荐', searchType: 'ai_recommend', resultCount: parsed.jobRecommendations?.length || 0 });

      return {
        recommendations: parsed,
        raw: result.content,
        stats: {
          totalJobs: availableJobs.length,
          userSkills: skills.length,
          recentSearches: searchKeywords.length,
        },
      };
    } catch (e) {
      // If parsing fails, return raw content
      return { recommendations: null, raw: result.content, stats: { totalJobs: availableJobs.length } };
    }
  }

}
