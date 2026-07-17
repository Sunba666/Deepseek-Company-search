export interface AITool {
  name: string;
  description: string;
  parameters: Record<string, { type: string; description: string; required?: boolean }>;
  execute: (args: Record<string, unknown>) => Promise<string>;
}

const tools: AITool[] = [
  {
    name: "search_jobs",
    description: "搜索岗位",
    parameters: {
      q: { type: "string", description: "搜索关键词", required: true },
      city: { type: "string", description: "城市" },
      category: { type: "string", description: "岗位分类" },
    },
    execute: async (args) => {
      // TODO: call job search API
      return JSON.stringify({ success: true, message: "搜索到 N 个岗位", jobs: [] });
    },
  },
  {
    name: "get_company_info",
    description: "获取公司信息",
    parameters: {
      name: { type: "string", description: "公司名称", required: true },
    },
    execute: async (args) => {
      return JSON.stringify({ success: true, message: "公司信息", company: {} });
    },
  },
  {
    name: "analyze_jd",
    description: "分析 JD",
    parameters: {
      jd_content: { type: "string", description: "JD 内容", required: true },
    },
    execute: async (args) => {
      return JSON.stringify({ success: true, message: "JD 分析结果" });
    },
  },
  {
    name: "get_referrals",
    description: "查询内推信息",
    parameters: {
      company: { type: "string", description: "公司名称" },
      job: { type: "string", description: "岗位名称" },
    },
    execute: async (args) => {
      return JSON.stringify({ success: true, message: "内推信息", referrals: [] });
    },
  },
];

export function getTools(): AITool[] { return tools; }

export function getTool(name: string): AITool | undefined {
  return tools.find((t) => t.name === name);
}

export async function executeTool(name: string, args: Record<string, unknown>): Promise<string> {
  const tool = getTool(name);
  if (!tool) throw new Error("Unknown tool: " + name);
  return tool.execute(args);
}
