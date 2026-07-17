import type { AIProvider, AICompletionRequest, AICompletionResponse, AIProviderConfig } from "./types";

export class OpenAIProvider implements AIProvider {
  readonly name = "openai" as const;
  private config: AIProviderConfig;
  constructor(config: AIProviderConfig) { this.config = { maxRetries: 3, ...config }; }

  async complete(req: AICompletionRequest): Promise<AICompletionResponse> {
    const res = await fetch(this.config.baseUrl || "https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": "Bearer " + this.config.apiKey },
      body: JSON.stringify({ model: req.model || this.config.model, messages: req.messages, temperature: req.temperature ?? 0.7, max_tokens: req.maxTokens ?? 4096 }),
    });
    if (!res.ok) throw new Error("OpenAI API error: " + res.status);
    const json = await res.json();
    return { content: json.choices[0].message.content, model: json.model };
  }

  async *stream(req: AICompletionRequest): AsyncGenerator<string, void, unknown> {
    const res = await fetch(this.config.baseUrl || "https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": "Bearer " + this.config.apiKey },
      body: JSON.stringify({ model: req.model || this.config.model, messages: req.messages, temperature: req.temperature ?? 0.7, max_tokens: req.maxTokens ?? 4096, stream: true }),
    });
    if (!res.ok) throw new Error("OpenAI stream error: " + res.status);
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
        try { const json = JSON.parse(data); const c = json.choices?.[0]?.delta?.content; if (c) yield c; } catch {}
      }
    }
  }
}
