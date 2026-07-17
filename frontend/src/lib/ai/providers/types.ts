export type AIModelProvider = "openai" | "anthropic" | "gemini" | "deepseek" | "zhipu" | "moonshot" | "openrouter";

export interface AIMessage {
  role: "system" | "user" | "assistant";
  content: string;
}

export interface AICompletionRequest {
  messages: AIMessage[];
  model?: string;
  temperature?: number;
  maxTokens?: number;
  stream?: boolean;
}

export interface AICompletionResponse {
  content: string;
  model: string;
  usage?: { promptTokens: number; completionTokens: number; totalTokens: number };
}

export interface AIProviderConfig {
  apiKey: string;
  baseUrl?: string;
  model: string;
  maxRetries?: number;
}

export interface AIProvider {
  readonly name: AIModelProvider;
  complete(req: AICompletionRequest): Promise<AICompletionResponse>;
  stream(req: AICompletionRequest): AsyncGenerator<string, void, unknown>;
}
