import { create } from "zustand";
import { persist } from "zustand/middleware";
export const useThemeStore = create<{ theme: "light" | "dark" | "system"; setTheme: (t: "light" | "dark" | "system") => void }>()(persist((set) => ({ theme: "system", setTheme: (t) => set({ theme: t }) }), { name: "jobnav-theme" }));
