import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { Application } from "@/types";

interface AppState { applications: Application[]; setApplications: (a: Application[]) => void; addApplication: (a: Application) => void; updateStatus: (id: string, s: Application["status"]) => void; }
export const useApplicationStore = create<AppState>()(persist((set) => ({ applications: [], setApplications: (a) => set({ applications: a }), addApplication: (a) => set((s) => ({ applications: [a, ...s.applications] })), updateStatus: (id, s) => set((state) => ({ applications: state.applications.map((a) => a.id === id ? { ...a, status: s } : a) })), }), { name: "jobnav-applications" }));
