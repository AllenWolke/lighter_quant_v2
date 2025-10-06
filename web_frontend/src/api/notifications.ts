import axios from 'axios';
import { Notification, NotificationType, NotificationLevel } from '../types';

// 创建axios实例
const api = axios.create({
  baseURL: '/api/notifications',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// 通知API
export const notificationApi = {
  // 获取通知列表
  getNotifications: (params?: {
    type?: NotificationType;
    level?: NotificationLevel;
    isRead?: boolean;
    limit?: number;
    offset?: number;
  }): Promise<{
    notifications: Notification[];
    total: number;
    unreadCount: number;
  }> => {
    return api.get('/', { params });
  },

  // 获取通知详情
  getNotification: (id: number): Promise<Notification> => {
    return api.get(`/${id}`);
  },

  // 标记通知为已读
  markAsRead: (id: number): Promise<{ message: string }> => {
    return api.patch(`/${id}/read`);
  },

  // 批量标记为已读
  markAllAsRead: (params?: {
    type?: NotificationType;
    level?: NotificationLevel;
  }): Promise<{ message: string; updatedCount: number }> => {
    return api.patch('/mark-all-read', params);
  },

  // 删除通知
  deleteNotification: (id: number): Promise<{ message: string }> => {
    return api.delete(`/${id}`);
  },

  // 批量删除通知
  deleteNotifications: (ids: number[]): Promise<{ message: string; deletedCount: number }> => {
    return api.delete('/batch', { data: { ids } });
  },

  // 获取未读通知数量
  getUnreadCount: (): Promise<{ count: number }> => {
    return api.get('/unread-count');
  },

  // 获取通知设置
  getSettings: (): Promise<{
    emailEnabled: boolean;
    pushEnabled: boolean;
    types: NotificationType[];
    levels: NotificationLevel[];
    quietHours: {
      enabled: boolean;
      start: string;
      end: string;
    };
  }> => {
    return api.get('/settings');
  },

  // 更新通知设置
  updateSettings: (settings: {
    emailEnabled?: boolean;
    pushEnabled?: boolean;
    types?: NotificationType[];
    levels?: NotificationLevel[];
    quietHours?: {
      enabled: boolean;
      start: string;
      end: string;
    };
  }): Promise<{ message: string }> => {
    return api.put('/settings', settings);
  },

  // 测试通知
  testNotification: (type: NotificationType, level: NotificationLevel): Promise<{ message: string }> => {
    return api.post('/test', { type, level });
  },

  // 获取通知统计
  getStats: (params?: {
    startDate?: string;
    endDate?: string;
  }): Promise<{
    totalNotifications: number;
    unreadNotifications: number;
    notificationsByType: Record<NotificationType, number>;
    notificationsByLevel: Record<NotificationLevel, number>;
    dailyStats: Array<{
      date: string;
      count: number;
    }>;
  }> => {
    return api.get('/stats', { params });
  },
};
