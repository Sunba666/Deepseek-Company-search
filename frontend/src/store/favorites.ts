import { create } from "zustand";
import { persist } from "zustand/middleware";

interface FavoriteState { jobIds: string[]; companyIds: string[]; toggleJob: (id: string) => void; toggleCompany: (id: string) => void; isJobFavorited: (id: string) => boolean; isCompanyFavorited: (id: string) => boolean; }
export const useFavoriteStore = create<FavoriteState>()(persist((set, get) => ({ jobIds: [], companyIds: [], toggleJob: (id) => set((s) => ({ jobIds: s.jobIds.includes(id) ? s.jobIds.filter((j) => j !== id) : [...s.jobIds, id] })), toggleCompany: (id) => set((s) => ({ companyIds: s.companyIds.includes(id) ? s.companyIds.filter((c) => c !== id) : [...s.companyIds, id] })), isJobFavorited: (id) => get().jobIds.includes(id), isCompanyFavorited: (id) => get().companyIds.includes(id), }), { name: "jobnav-favorites" }));
