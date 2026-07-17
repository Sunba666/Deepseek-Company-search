import { create } from "zustand";
interface CopilotState { isOpen: boolean; toggleOpen: () => void; setOpen: (o: boolean) => void; }
export const useCopilotStore = create<CopilotState>()((set) => ({ isOpen: false, toggleOpen: () => set((s) => ({ isOpen: !s.isOpen })), setOpen: (o) => set({ isOpen: o }) }));
