import axios from 'axios';
import { Position } from '../types';

// 创建axios实例
const api = axios.create({
  baseURL: '/api/positions',
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

// 持仓API
export const positionApi = {
  // 获取持仓列表
  getPositions: (params?: {
    symbol?: string;
    isActive?: boolean;
    limit?: number;
    offset?: number;
  }): Promise<Position[]> => {
    return api.get('/', { params });
  },

  // 获取持仓详情
  getPosition: (id: number): Promise<Position> => {
    return api.get(`/${id}`);
  },

  // 获取持仓统计
  getPositionStats: (): Promise<{
    totalPositions: number;
    activePositions: number;
    totalUnrealizedPnl: number;
    totalMargin: number;
    averageLeverage: number;
    riskLevel: 'low' | 'medium' | 'high';
  }> => {
    return api.get('/stats');
  },

  // 关闭持仓
  closePosition: (id: number, params?: {
    quantity?: number;
    price?: number;
    reason?: string;
  }): Promise<{ message: string }> => {
    return api.post(`/${id}/close`, params);
  },

  // 批量关闭持仓
  closeAllPositions: (params?: {
    symbol?: string;
    reason?: string;
  }): Promise<{ message: string; closedCount: number }> => {
    return api.post('/close-all', params);
  },

  // 更新持仓止损止盈
  updateStopLoss: (id: number, stopLossPrice: number): Promise<{ message: string }> => {
    return api.patch(`/${id}/stop-loss`, { stopLossPrice });
  },

  updateTakeProfit: (id: number, takeProfitPrice: number): Promise<{ message: string }> => {
    return api.patch(`/${id}/take-profit`, { takeProfitPrice });
  },

  // 获取持仓历史
  getPositionHistory: (params?: {
    symbol?: string;
    startDate?: string;
    endDate?: string;
    limit?: number;
    offset?: number;
  }): Promise<{
    positions: Position[];
    total: number;
    page: number;
    pageSize: number;
  }> => {
    return api.get('/history', { params });
  },

  // 获取持仓盈亏分析
  getPnlAnalysis: (params?: {
    symbol?: string;
    startDate?: string;
    endDate?: string;
  }): Promise<{
    dailyPnl: Array<{
      date: string;
      pnl: number;
      trades: number;
    }>;
    totalPnl: number;
    averageDailyPnl: number;
    bestDay: {
      date: string;
      pnl: number;
    };
    worstDay: {
      date: string;
      pnl: number;
    };
  }> => {
    return api.get('/pnl-analysis', { params });
  },

  // 获取风险分析
  getRiskAnalysis: (): Promise<{
    portfolioValue: number;
    totalMargin: number;
    marginRatio: number;
    maxDrawdown: number;
    var95: number;
    var99: number;
    riskLevel: 'low' | 'medium' | 'high';
    recommendations: string[];
  }> => {
    return api.get('/risk-analysis');
  },
};
