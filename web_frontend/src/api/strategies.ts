import axios from 'axios';
import { Strategy, StrategyParameter, StrategyCreateRequest, StrategyUpdateRequest } from '../types';

// 创建axios实例
const api = axios.create({
  baseURL: '/api/strategies',
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

// 策略API
export const strategyApi = {
  // 获取策略列表
  getStrategies: (params?: {
    strategyType?: string;
    isActive?: boolean;
    limit?: number;
    offset?: number;
  }): Promise<Strategy[]> => {
    return api.get('/', { params });
  },

  // 获取策略详情
  getStrategy: (id: number): Promise<Strategy> => {
    return api.get(`/${id}`);
  },

  // 创建策略
  createStrategy: (strategyData: StrategyCreateRequest): Promise<Strategy> => {
    return api.post('/', strategyData);
  },

  // 更新策略
  updateStrategy: (id: number, strategyData: StrategyUpdateRequest): Promise<Strategy> => {
    return api.put(`/${id}`, strategyData);
  },

  // 删除策略
  deleteStrategy: (id: number): Promise<{ message: string }> => {
    return api.delete(`/${id}`);
  },

  // 启用/禁用策略
  toggleStrategy: (id: number, enabled: boolean): Promise<{ message: string }> => {
    return api.patch(`/${id}/toggle`, { enabled });
  },

  // 获取策略参数
  getStrategyParameters: (id: number): Promise<StrategyParameter[]> => {
    return api.get(`/${id}/parameters`);
  },

  // 更新策略参数
  updateStrategyParameters: (id: number, parameters: Record<string, any>): Promise<{ message: string }> => {
    return api.put(`/${id}/parameters`, { parameters });
  },

  // 获取策略性能统计
  getStrategyStats: (id: number, days: number = 30): Promise<{
    totalTrades: number;
    winningTrades: number;
    winRate: number;
    totalPnl: number;
    maxDrawdown: number;
    sharpeRatio: number;
  }> => {
    return api.get(`/${id}/stats`, { params: { days } });
  },

  // 回测策略
  backtestStrategy: (id: number, params: {
    startDate: string;
    endDate: string;
    initialCapital: number;
    symbol: string;
  }): Promise<{
    results: any;
    trades: any[];
    performance: any;
  }> => {
    return api.post(`/${id}/backtest`, params);
  },

  // 获取可用策略类型
  getStrategyTypes: (): Promise<Array<{
    type: string;
    name: string;
    description: string;
    parameters: Array<{
      name: string;
      type: string;
      description: string;
      required: boolean;
      defaultValue: any;
    }>;
  }>> => {
    return api.get('/types');
  },

  // 复制策略
  copyStrategy: (id: number, newName: string): Promise<Strategy> => {
    return api.post(`/${id}/copy`, { name: newName });
  },

  // 导出策略配置
  exportStrategy: (id: number): Promise<{
    config: any;
    parameters: any;
  }> => {
    return api.get(`/${id}/export`);
  },

  // 导入策略配置
  importStrategy: (config: any): Promise<Strategy> => {
    return api.post('/import', config);
  },
};
