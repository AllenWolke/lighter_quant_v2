import axios from 'axios';
import { LoginRequest, LoginResponse, RegisterRequest, User } from '../types';

// 创建axios实例
const api = axios.create({
  baseURL: '/api/auth',
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
      // 未授权，清除token并跳转到登录页
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// 认证API
export const authApi = {
  // 用户登录
  login: (credentials: LoginRequest): Promise<LoginResponse> => {
    return api.post('/login', credentials);
  },

  // 用户注册
  register: (userData: RegisterRequest): Promise<{ message: string }> => {
    return api.post('/register', userData);
  },

  // 用户登出
  logout: (): Promise<{ message: string }> => {
    return api.post('/logout');
  },

  // 刷新token
  refreshToken: (): Promise<LoginResponse> => {
    return api.post('/refresh');
  },

  // 获取当前用户信息
  getCurrentUser: (): Promise<User> => {
    return api.get('/me');
  },

  // 更新用户信息
  updateUser: (userData: Partial<User>): Promise<User> => {
    return api.put('/me', userData);
  },

  // 修改密码
  changePassword: (data: {
    currentPassword: string;
    newPassword: string;
  }): Promise<{ message: string }> => {
    return api.post('/change-password', data);
  },

  // 重置密码
  resetPassword: (email: string): Promise<{ message: string }> => {
    return api.post('/reset-password', { email });
  },

  // 验证邮箱
  verifyEmail: (token: string): Promise<{ message: string }> => {
    return api.post('/verify-email', { token });
  },

  // 重新发送验证邮件
  resendVerificationEmail: (): Promise<{ message: string }> => {
    return api.post('/resend-verification');
  },
};
