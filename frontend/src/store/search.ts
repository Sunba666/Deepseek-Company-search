import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { JobFilters } from "@/types";

interface SearchState { filters: JobFilters; searchHistory: string[]; setFilters: (f: Partial<JobFilters>) => void; resetFilters: () => void; addSearchHistory: (q: string) => void; }
const defaults: JobFilters = { page: 1, limit: 20, sort: "published_at", order: "desc" };
export const useSearchStore = create<SearchState>()(persist((set) => ({ filters: defaults, searchHistory: [], setFilters: (f) => set((s) => ({ filters: { ...s.filters, ...f, page: 1 } })), resetFilters: () => set({ filters: defaults }), addSearchHistory: (q) => set((s) => ({ searchHistory: [q, ...s.searchHistory.filter((x) => x !== q)].slice(0, 20) })), }), { name: "jobnav-search" }));
