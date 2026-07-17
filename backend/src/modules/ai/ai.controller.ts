import { Controller, Post, Body, Get, Param, Delete, Res, Patch } from '@nestjs/common';
import type { Response } from 'express';
import { AiService } from './ai.service';
import { Public } from '../../common/decorators/public.decorator';

@Controller('api/v1/ai')
export class AiController {
  constructor(private aiService: AiService) {}

  // Chat & Stream
  @Public() @Post('chat')
  async chat(@Body() body: { messages: any[] }) {
    return this.aiService.complete({ messages: body.messages });
  }

  @Public() @Post('stream')
  async stream(@Body() body: { messages: any[] }, @Res() res: Response) {
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    try {
      const generator = this.aiService.stream({ messages: body.messages });
      for await (const chunk of generator) { res.write(`data: ${JSON.stringify({ content: chunk })}\n\n`); }
      res.write('data: [DONE]\n\n');
    } catch (err: any) { res.write(`data: ${JSON.stringify({ error: err.message })}\n\n`); }
    res.end();
  }

  // Conversations
  @Public() @Post('conversations')
  createConversation(@Body() body: { userId: string; title?: string }) {
    return this.aiService.createConversation(body.userId || 'anonymous', body.title);
  }

  @Public() @Get('conversations/:userId')
  listConversations(@Param('userId') userId: string) {
    return this.aiService.listConversations(userId || 'anonymous');
  }

  @Public() @Get('conversation/:id')
  getConversation(@Param('id') id: string) {
    return this.aiService.getConversation(id);
  }

  @Public() @Delete('conversation/:id')
  deleteConversation(@Param('id') id: string) {
    return this.aiService.deleteConversation(id);
  }

  @Public() @Patch('conversation/:id/star')
  toggleStar(@Param('id') id: string) {
    return this.aiService.toggleStarConversation(id);
  }

  @Public() @Post('conversation/:id/chat')
  chatInConversation(@Param('id') id: string, @Body() body: { message: string }) {
    return this.aiService.chatAndSave(id, body.message);
  }

  // Resume Analysis
  @Public() @Post('analyze-resume')
  analyzeResume(@Body() body: { resume_text: string; skills?: string[] }) {
    return this.aiService.analyzeResume(body.resume_text, body.skills);
  }

  // Mock Interview
  @Public() @Post('mock-interview')
  mockInterview(@Body() body: {
    job_title: string; company?: string; skills?: string[];
    question?: string; history?: { question: string; answer: string }[];
  }) {
    return this.aiService.mockInterview({
      jobTitle: body.job_title, company: body.company, skills: body.skills,
      question: body.question, history: body.history,
    });
  }

  // JD Analysis
  @Public() @Post('analyze-jd')
  analyzeJD(@Body() body: { jd_content: string; resume_summary?: string }) {
    return this.aiService.analyzeJD(body.jd_content, body.resume_summary);
  }

  // Recommend Jobs
  @Public() @Post('recommend-jobs')
  recommendJobs(@Body() body: { skills: string; experience: string; city: string; jobs: string }) {
    return this.aiService.recommendJobs(body.skills, body.experience, body.city, body.jobs);
  }

  // ===== Personalized Recommendation =====
  @Public() @Post("personalized-recommend")
  personalizedRecommend(@Body() body: { userId: string }) {
    return this.aiService.personalizedRecommend(body.userId || "anonymous");
  }

  // ===== Search History =====
  @Public() @Post("save-search")
  saveSearch(@Body() body: { userId: string; query: string; searchType?: string; resultCount?: number }) {
    return this.aiService.saveSearch(body.userId || "anonymous", body);
  }

  @Public() @Post("search-history")
  getSearchHistory(@Body() body: { userId: string }) {
    return this.aiService.getSearchHistory(body.userId || "anonymous");
  }
}
