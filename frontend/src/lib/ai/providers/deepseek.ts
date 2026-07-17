import type { AIProvider, AICompletionRequest, AICompletionResponse, AIProviderConfig } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3001/api/v1";

export class DeepSeekProvider implements AIProvider {
  readonly name = "deepseek" as const;
  private config: AIProviderConfig;

  constructor(config: AIProviderConfig) {
    this.config = { maxRetries: 3, ...config };
  }

  async complete(req: AICompletionRequest): Promise<AICompletionResponse> {
    const res = await fetch(API_BASE + "/ai/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        messages: req.messages,
        model: req.model || this.config.model,
        temperature: req.temperature ?? 0.7,
        maxTokens: req.maxTokens ?? 4096,
      }),
    });
    if (!res.ok) {
      const errBody = await res.text().catch(() => "");
      throw new Error(`AI API error: ${res.status} ${errBody}`);
    }
    const json = await res.json();
    const data = json.data ?? json;
    return { content: data.content, model: data.model, usage: data.usage };
  }

  async *stream(req: AICompletionRequest): AsyncGenerator<string, void, unknown> {
    const res = await fetch(API_BASE + "/ai/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        messages: req.messages,
        model: req.model || this.config.model,
        temperature: req.temperature ?? 0.7,
        maxTokens: req.maxTokens ?? 4096,
      }),
    });
    if (!res.ok) throw new Error("AI stream error: " + res.status);

    const reader = res.body?.getReader();
    if (!reader) throw new Error("No response body");
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value);
      const lines = chunk.split("\n").filter((l) => l.startsWith("data: "));
      for (const line of lines) {
        const data = line.slice(6);
        if (data === "[DONE]") return;
        try {
          const parsed = JSON.parse(data);
          if (parsed.content) yield parsed.content;
        } catch {}
      }
    }
  }
}
