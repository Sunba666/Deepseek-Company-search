import { create } from "zustand";
import { persist } from "zustand/middleware";
import { getAIMemory, getAIProvider, getPrompt } from "@/lib/ai";
import type { AIModelProvider, AISession } from "@/lib/ai";

interface AIConfig {
  provider: AIModelProvider;
  model: string;
  temperature: number;
  maxTokens: number;
}

interface AIState {
  // Config
  config: AIConfig;
  setConfig: (config: Partial<AIConfig>) => void;

  // Sessions
  sessions: AISession[];
  currentSessionId: string | null;
  switchSession: (id: string) => void;
  createSession: () => void;
  deleteSession: (id: string) => void;
  renameSession: (id: string, title: string) => void;
  toggleStar: (id: string) => void;

  // Chat
  messages: { role: "user" | "assistant"; content: string }[];
  isProcessing: boolean;
  streamingContent: string;
  addMessage: (role: "user" | "assistant", content: string) => void;
  sendMessage: (content: string) => Promise<void>;
  stopGeneration: () => void;

  // Files
  uploadedFile: { name: string; content: string } | null;
  setUploadedFile: (file: { name: string; content: string } | null) => void;

  // Token usage
  totalTokens: number;
}

let abortController: AbortController | null = null;

export const useAIStore = create<AIState>()(
  persist(
    (set, get) => ({
      config: { provider: "deepseek", model: "deepseek-chat", temperature: 0.7, maxTokens: 4096 },
      setConfig: (partial) => set((s) => ({ config: { ...s.config, ...partial } })),

      sessions: [],
      currentSessionId: null,
      switchSession: (id) => {
        set({ currentSessionId: id });
        const mem = getAIMemory();
        mem.switchSession(id);
        set({ messages: mem.getMessages().map((m) => ({ role: m.role === "system" ? "assistant" : m.role, content: m.content } as { role: "user" | "assistant"; content: string })) });
      },
      createSession: () => {
        const mem = getAIMemory();
        const sess = mem.createSession();
        set({ sessions: mem.getAllSessions(), currentSessionId: sess.id, messages: [] });
      },
      deleteSession: (id) => {
        getAIMemory().deleteSession(id);
        const mem = getAIMemory();
        set({ sessions: mem.getAllSessions(), currentSessionId: mem.getAllSessions()[0]?.id || null, messages: [] });
      },
      renameSession: (id, title) => {
        getAIMemory().renameSession(id, title);
        set({ sessions: getAIMemory().getAllSessions() });
      },
      toggleStar: (id) => {
        getAIMemory().toggleStar(id);
        set({ sessions: getAIMemory().getAllSessions() });
      },

      messages: [],
      isProcessing: false,
      streamingContent: "",
      addMessage: (role, content) => {
        const mem = getAIMemory();
        mem.addMessage(role, content);
        set((s) => ({
          messages: [...s.messages, { role, content }],
          sessions: mem.getAllSessions(),
        }));
      },

      sendMessage: async (content) => {
        const state = get();
        if (state.isProcessing) return;

        const mem = getAIMemory();
        if (!mem.getCurrentSession()) mem.createSession();

        state.addMessage("user", content);
        set({ isProcessing: true, streamingContent: "" });

        abortController = new AbortController();
        try {
          const provider = getAIProvider();
          const history = get().messages.map((m) => ({ role: m.role as "user" | "assistant" | "system", content: m.content }));
          let systemContent = getPrompt("copilot-general", {
            current_page: typeof window !== "undefined" ? window.location.pathname : "",
            favorite_count: "0",
            application_count: "0",
          });

          const stream = provider.stream({
            messages: [{ role: "system", content: systemContent }, ...history],
            model: state.config.model,
            temperature: state.config.temperature,
            maxTokens: state.config.maxTokens,
          });

          let fullContent = "";
          for await (const chunk of stream) {
            fullContent += chunk;
            set({ streamingContent: fullContent });
          }

          state.addMessage("assistant", fullContent);
          set({ streamingContent: "", isProcessing: false });
        } catch (err: any) {
          if (err.name !== "AbortError") {
            state.addMessage("assistant", "抱歉，我遇到了一些问题：" + err.message);
          }
          set({ streamingContent: "", isProcessing: false });
        }
      },

      stopGeneration: () => {
        abortController?.abort();
        set({ isProcessing: false });
      },

      uploadedFile: null,
      setUploadedFile: (file) => set({ uploadedFile: file }),

      totalTokens: 0,
    }),
    { name: "jobnav-ai", partialize: (state) => ({ config: state.config }) }
  )
);
