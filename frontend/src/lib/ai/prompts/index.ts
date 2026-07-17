export interface PromptTemplate {
  id: string;
  name: string;
  version: string;
  template: string;
  variables: string[];
  description: string;
}

const PROMPTS: Record<string, PromptTemplate> = {
  "jd-analysis": {
    id: "jd-analysis", name: "JD 分析", version: "1.0",
    template: `你是一个专业的求职顾问。请分析以下 JD，输出结构化的分析结果。

JD 内容：
{jd_content}

用户简历摘要：
{resume_summary}

请按以下格式输出：
1. 匹配度（百分比）：分析用户与岗位的匹配程度
2. 已具备技能：列出用户已具备的匹配技能
3. 缺失技能：列出用户还不具备但岗位要求的技能
4. 学习建议：针对缺失技能给出具体学习建议
5. 简历优化建议：针对该岗位给出简历优化建议
6. 薪资分析：该岗位的市场薪资范围`,
    variables: ["jd_content", "resume_summary"],
    description: "分析 JD 与用户的匹配度",
  },
  "job-recommend": {
    id: "job-recommend", name: "岗位推荐", version: "1.0",
    template: `你是一个 AI 求职顾问。根据以下用户信息，推荐最适合的岗位。

用户信息：
- 技能：{skills}
- 经验：{experience}年
- 学历：{education}
- 城市：{city}
- 期望薪资：{salary_min}-{salary_max}K

平台在招岗位列表：
{jobs}

请输出：
1. 按匹配度从高到低推荐 5-8 个岗位
2. 每个岗位给出匹配度百分比和推荐理由
3. 技能缺口分析
4. 学习建议
5. 推荐投递顺序`,
    variables: ["skills", "experience", "education", "city", "salary_min", "salary_max", "jobs"],
    description: "基于用户信息推荐适合的岗位",
  },
  "copilot-general": {
    id: "copilot-general", name: "通用助手", version: "1.0",
    template: `你是 JobNav AI 求职助手，一个专业的求职辅助 AI。你可以：
1. 推荐岗位
2. 分析 JD
3. 提供内推建议
4. 优化简历
5. 职业规划建议

当前用户上下文：
- 浏览页面：{current_page}
- 收藏岗位数：{favorite_count}
- 投递记录数：{application_count}

请专业、简洁地回应用户的问题。如果是岗位推荐类问题，请主动询问用户偏好。`,
    variables: ["current_page", "favorite_count", "application_count"],
    description: "通用 AI 求职助手对话",
  },
  "resume-analysis": {
    id: "resume-analysis", name: "简历分析", version: "1.0",
    template: `你是一个专业的简历分析师。请分析以下简历内容，输出优化建议。

简历内容：
{resume_content}

目标岗位（可选）：
{target_job}

请按以下格式输出：
1. ATS 评分（百分比）
2. 关键词匹配分析
3. 格式和结构建议
4. 内容优化建议（逐条列出）
5. 推荐的技能关键词（用于提高 ATS 通过率）`,
    variables: ["resume_content", "target_job"],
    description: "分析简历并提供优化建议",
  },
  "company-analysis": {
    id: "company-analysis", name: "公司分析", version: "1.0",
    template: `你是一个公司研究分析师。请根据以下公司信息，输出 AI 公司画像。

公司信息：
{company_info}

请按以下格式输出：
1. 综合评分（1-10）
2. 薪资评分
3. 文化评分
4. 成长评分
5. 稳定评分
6. 招聘趋势分析
7. 优点列表
8. 缺点列表
9. 求职建议`,
    variables: ["company_info"],
    description: "分析公司并生成 AI 画像",
  },
};

export function getPrompt(id: string, variables: Record<string, string>): string {
  const prompt = PROMPTS[id];
  if (!prompt) throw new Error("Unknown prompt: " + id);
  let result = prompt.template;
  for (const [key, value] of Object.entries(variables)) {
    result = result.replace("{" + key + "}", value);
  }
  return result;
}

export function listPrompts(): PromptTemplate[] {
  return Object.values(PROMPTS);
}

export function getPromptInfo(id: string): PromptTemplate | undefined {
  return PROMPTS[id];
}
