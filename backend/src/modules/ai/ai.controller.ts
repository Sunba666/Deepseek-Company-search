import { Controller, Post, Body, Res, HttpCode, HttpStatus, UseGuards } from '@nestjs/common';
import type { Response } from 'express';
import { AiService } from './ai.service';
import { Public } from '../../common/decorators/public.decorator';

@Controller('api/v1/ai')
export class AiController {
  constructor(private aiService: AiService) {}

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

  @Public() @Post('analyze-jd')
  analyzeJD(@Body() body: { jd_content: string; resume_summary?: string }) { return this.aiService.analyzeJD(body.jd_content, body.resume_summary); }

  @Public() @Post('recommend-jobs')
  recommendJobs(@Body() body: { skills: string; experience: string; city: string; jobs: string }) { return this.aiService.recommendJobs(body.skills, body.experience, body.city, body.jobs); }
}
