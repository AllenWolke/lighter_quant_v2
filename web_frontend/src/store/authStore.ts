import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { User, LoginRequest, LoginResponse } from '../types';

interface AuthState {
  // 用户信息
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  // 认证方法
  login: (credentials: LoginRequest) => Promise<boolean>;
  logout: () => void;
  register: (userData: any) => Promise<boolean>;
  updateUser: (userData: Partial<User>) => void;
  refreshToken: () => Promise<boolean>;
  
  // 状态更新方法
  setUser: (user: User | null) => void;
  setLoading: (loading: boolean) => void;
  setAuthenticated: (authenticated: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  devtools(
    persist(
      (set, get) => ({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        
        login: async (credentials: LoginRequest) => {
          try {
            set({ isLoading: true });
            
            const response = await fetch('/api/auth/login', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify(credentials),
            });
            
            if (!response.ok) {
              throw new Error('登录失败');
            }
            
            const data: LoginResponse = await response.json();
            
            // 存储token
            localStorage.setItem('token', data.accessToken);
            
            set({
              user: data.user,
              isAuthenticated: true,
              isLoading: false,
            });
            
            return true;
          } catch (error) {
            console.error('登录错误:', error);
            set({ isLoading: false });
            return false;
          }
        },
        
        logout: () => {
          localStorage.removeItem('token');
          set({
            user: null,
            isAuthenticated: false,
          });
        },
        
        register: async (userData: any) => {
          try {
            set({ isLoading: true });
            
            const response = await fetch('/api/auth/register', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify(userData),
            });
            
            if (!response.ok) {
              throw new Error('注册失败');
            }
            
            set({ isLoading: false });
            return true;
          } catch (error) {
            console.error('注册错误:', error);
            set({ isLoading: false });
            return false;
          }
        },
        
        updateUser: (userData: Partial<User>) => {
          const currentUser = get().user;
          if (currentUser) {
            set({
              user: { ...currentUser, ...userData }
            });
          }
        },
        
        refreshToken: async () => {
          try {
            const token = localStorage.getItem('token');
            if (!token) {
              return false;
            }
            
            const response = await fetch('/api/auth/refresh', {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${token}`,
              },
            });
            
            if (!response.ok) {
              throw new Error('Token刷新失败');
            }
            
            const data: LoginResponse = await response.json();
            localStorage.setItem('token', data.accessToken);
            
            set({
              user: data.user,
              isAuthenticated: true,
            });
            
            return true;
          } catch (error) {
            console.error('Token刷新错误:', error);
            get().logout();
            return false;
          }
        },
        
        setUser: (user) => set({ user }),
        setLoading: (loading) => set({ isLoading: loading }),
        setAuthenticated: (authenticated) => set({ isAuthenticated: authenticated }),
      }),
      {
        name: 'auth-store',
        partialize: (state) => ({
          user: state.user,
          isAuthenticated: state.isAuthenticated,
        }),
      }
    ),
    {
      name: 'auth-store',
    }
  )
);
