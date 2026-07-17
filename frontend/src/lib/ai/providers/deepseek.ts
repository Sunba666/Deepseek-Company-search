import type { AIProvider, AICompletionRequest, AICompletionResponse, AIProviderConfig } from "./types";

export class DeepSeekProvider implements AIProvider {
  readonly name = "deepseek" as const;
  private config: AIProviderConfig;

  constructor(config: AIProviderConfig) {
    this.config = { maxRetries: 3, ...config };
  }

  async complete(req: AICompletionRequest): Promise<AICompletionResponse> {
    const body = {
      model: req.model || this.config.model,
      messages: req.messages,
      temperature: req.temperature ?? 0.7,
      max_tokens: req.maxTokens ?? 4096,
      stream: false,
    };

    const res = await fetch(this.config.baseUrl || "https://api.deepseek.com/v1/chat/completions", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": "Bearer " + this.config.apiKey },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error("DeepSeek API error: " + res.status);

    const json = await res.json();
    return {
      content: json.choices[0].message.content,
      model: json.model,
      usage: json.usage ? { promptTokens: json.usage.prompt_tokens, completionTokens: json.usage.completion_tokens, totalTokens: json.usage.total_tokens } : undefined,
    };
  }

  async *stream(req: AICompletionRequest): AsyncGenerator<string, void, unknown> {
    const body = {
      model: req.model || this.config.model,
      messages: req.messages,
      temperature: req.temperature ?? 0.7,
      max_tokens: req.maxTokens ?? 4096,
      stream: true,
    };

    const res = await fetch(this.config.baseUrl || "https://api.deepseek.com/v1/chat/completions", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": "Bearer " + this.config.apiKey },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error("DeepSeek stream error: " + res.status);

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
          const json = JSON.parse(data);
          const content = json.choices?.[0]?.delta?.content;
          if (content) yield content;
        } catch {}
      }
    }
  }
}
