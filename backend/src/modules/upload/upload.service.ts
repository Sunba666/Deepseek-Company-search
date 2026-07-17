import { Injectable, BadRequestException } from '@nestjs/common';
import { extname } from 'path';
import * as fs from 'fs';
import * as path from 'path';

@Injectable()
export class UploadService {
  private uploadDir = './uploads';

  constructor() { if (!fs.existsSync(this.uploadDir)) fs.mkdirSync(this.uploadDir, { recursive: true }); }

  async uploadFile(file: Express.Multer.File): Promise<string> {
    const allowed = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png'];
    const ext = extname(file.originalname).toLowerCase();
    if (!allowed.includes(ext)) throw new BadRequestException('不支持的文件格式');
    const filename = `${Date.now()}-${Math.random().toString(36).slice(2)}${ext}`;
    const filepath = path.join(this.uploadDir, filename);
    fs.writeFileSync(filepath, file.buffer);
    return `/uploads/${filename}`;
  }
}
