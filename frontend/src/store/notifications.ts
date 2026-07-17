import { create } from "zustand";
interface Notif { id: string; type: string; title: string; isRead: boolean; createdAt: string; }
interface NotifState { notifications: Notif[]; unreadCount: number; setNotifications: (n: Notif[]) => void; markRead: (id: string) => void; }
export const useNotificationStore = create<NotifState>()((set) => ({ notifications: [], unreadCount: 0, setNotifications: (n) => set({ notifications: n, unreadCount: n.filter((x) => !x.isRead).length }), markRead: (id) => set((s) => ({ notifications: s.notifications.map((n) => n.id === id ? { ...n, isRead: true } : n), unreadCount: s.unreadCount - 1 })), }));
