import zh from "./locales/zh-CN";
import en from "./locales/en";
export type SupportedLocale = "zh-CN" | "en";
export const locales: Record<SupportedLocale, typeof zh> = { "zh-CN": zh, en };
export const defaultLocale: SupportedLocale = "zh-CN";
export { zh, en };
