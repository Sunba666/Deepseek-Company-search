import type { AIModelProvider, AIProvider, AIProviderConfig } from "./types";
import { DeepSeekProvider } from "./deepseek";
import { OpenAIProvider } from "./openai";

const providerConstructors: Record<string, new (config: AIProviderConfig) => AIProvider> = {
  deepseek: DeepSeekProvider,
  openai: OpenAIProvider,
};

let _currentProvider: AIProvider | null = null;
let _currentConfig: { provider: AIModelProvider; model: string } = { provider: "deepseek", model: "deepseek-chat" };

export function getAIProvider(): AIProvider {
  if (_currentProvider) return _currentProvider;
  const apiKey = typeof window !== "undefined" ? localStorage.getItem("ai_api_key") || "" : "";
  const Constructor = providerConstructors[_currentConfig.provider];
  if (!Constructor) throw new Error("Unknown provider: " + _currentConfig.provider);
  _currentProvider = new Constructor({ apiKey, model: _currentConfig.model });
  return _currentProvider;
}

export function setAIProvider(provider: AIModelProvider, model: string, apiKey?: string) {
  _currentProvider = null;
  _currentConfig = { provider, model };
  if (apiKey && typeof window !== "undefined") localStorage.setItem("ai_api_key", apiKey);
}

export function getCurrentConfig() { return _currentConfig; }

export { type AIModelProvider, type AIProvider, type AIProviderConfig, type AICompletionRequest, type AICompletionResponse, type AIMessage } from "./types";
