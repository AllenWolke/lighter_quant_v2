import axios from 'axios';
import { 
  Position, 
  Order, 
  MarketData, 
  KlineData, 
  TradingStats, 
  AccountInfo 
} from '../types/trading';

// 创建axios实例
const api = axios.create({
  baseURL: '/api/trading',
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

// 交易API
export const tradingApi = {
  // 获取账户信息
  getAccountInfo: (): Promise<AccountInfo> => {
    return api.get('/account');
  },

  // 获取交易统计
  getTradingStats: (days: number = 30): Promise<TradingStats> => {
    return api.get('/stats', { params: { days } });
  },

  // 获取持仓列表
  getPositions: (): Promise<Position[]> => {
    return api.get('/positions');
  },

  // 获取订单列表
  getOrders: (params?: {
    symbol?: string;
    status?: string;
    limit?: number;
    offset?: number;
  }): Promise<Order[]> => {
    return api.get('/orders', { params });
  },

  // 获取交易历史
  getTrades: (params?: {
    symbol?: string;
    limit?: number;
    offset?: number;
  }): Promise<any[]> => {
    return api.get('/trades', { params });
  },

  // 创建订单
  createOrder: (orderData: {
    symbol: string;
    side: 'buy' | 'sell';
    orderType: 'market' | 'limit' | 'stop_loss' | 'take_profit';
    quantity: number;
    price?: number;
    stopPrice?: number;
  }): Promise<Order> => {
    return api.post('/orders', orderData);
  },

  // 取消订单
  cancelOrder: (orderId: number): Promise<{ message: string }> => {
    return api.delete(`/orders/${orderId}`);
  },

  // 获取市场数据
  getMarketData: (symbol: string, timeframe: string = '1m'): Promise<MarketData> => {
    return api.get(`/market-data/${symbol}`, {
      params: { timeframe }
    });
  },

  // 获取K线数据
  getKlines: (symbol: string, timeframe: string = '1m', limit: number = 200): Promise<{ data: KlineData[] }> => {
    return api.get(`/klines/${symbol}`, {
      params: { timeframe, limit }
    });
  },

  // 获取行情数据
  getTicker: (symbol: string): Promise<any> => {
    return api.get(`/ticker/${symbol}`);
  },

  // 获取订单簿
  getOrderbook: (symbol: string, limit: number = 20): Promise<any> => {
    return api.get(`/orderbook/${symbol}`, {
      params: { limit }
    });
  },

  // 获取交易对列表
  getSymbols: (): Promise<string[]> => {
    return api.get('/symbols');
  },

  // 开始交易
  startTrading: (): Promise<{ message: string }> => {
    return api.post('/start-trading');
  },

  // 停止交易
  stopTrading: (): Promise<{ message: string }> => {
    return api.post('/stop-trading');
  },

  // 紧急停止
  emergencyStop: (): Promise<{ message: string }> => {
    return api.post('/emergency-stop');
  },
};
