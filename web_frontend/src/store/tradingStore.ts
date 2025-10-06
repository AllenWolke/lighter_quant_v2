import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

// 类型定义
export interface Position {
  id: number;
  symbol: string;
  side: 'long' | 'short';
  quantity: number;
  entryPrice: number;
  currentPrice: number;
  unrealizedPnl: number;
  pnlRatio: number;
  margin: number;
  leverage: number;
  stopLossPrice?: number;
  takeProfitPrice?: number;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface Order {
  id: number;
  symbol: string;
  side: 'buy' | 'sell';
  orderType: 'market' | 'limit' | 'stop_loss' | 'take_profit';
  quantity: number;
  price?: number;
  stopPrice?: number;
  filledQuantity: number;
  remainingQuantity: number;
  status: 'pending' | 'partially_filled' | 'filled' | 'cancelled' | 'rejected';
  orderId: string;
  createdAt: string;
  updatedAt: string;
}

export interface MarketData {
  symbol: string;
  price: number;
  change24h: number;
  changePercent24h: number;
  volume24h: number;
  high24h: number;
  low24h: number;
  timestamp: string;
}

export interface KlineData {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface TradingStats {
  totalTrades: number;
  winningTrades: number;
  losingTrades: number;
  winRate: number;
  totalPnl: number;
  totalPnlPercent: number;
  maxDrawdown: number;
  sharpeRatio: number;
  avgTradePnl: number;
  bestTrade: number;
  worstTrade: number;
}

export interface AccountInfo {
  balance: number;
  availableBalance: number;
  marginBalance: number;
  unrealizedPnl: number;
  totalPnl: number;
  marginRatio: number;
  riskLevel: 'low' | 'medium' | 'high';
}

export type TradingStatus = 'stopped' | 'running' | 'paused';

// 交易状态接口
interface TradingState {
  // 基础设置
  selectedSymbol: string | null;
  selectedStrategy: number | null;
  strategyParams: Record<string, any>;
  
  // 交易状态
  tradingStatus: TradingStatus;
  isTradingEnabled: boolean;
  
  // 数据
  positions: Position[];
  orders: Order[];
  marketData: MarketData | null;
  klineData: KlineData[];
  tradingStats: TradingStats | null;
  accountInfo: AccountInfo | null;
  
  // 设置更新方法
  updateSelectedSymbol: (symbol: string | null) => void;
  updateSelectedStrategy: (strategyId: number | null) => void;
  updateStrategyParams: (params: Record<string, any>) => void;
  updateTradingStatus: (status: TradingStatus) => void;
  updateTradingEnabled: (enabled: boolean) => void;
  
  // 数据更新方法
  updatePositions: (positions: Position[]) => void;
  updateOrders: (orders: Order[]) => void;
  updateMarketData: (data: MarketData | null) => void;
  updateKlineData: (data: KlineData[]) => void;
  updateTradingStats: (stats: TradingStats | null) => void;
  updateAccountInfo: (info: AccountInfo | null) => void;
  
  // 添加/更新单个数据
  addPosition: (position: Position) => void;
  updatePosition: (id: number, updates: Partial<Position>) => void;
  removePosition: (id: number) => void;
  
  addOrder: (order: Order) => void;
  updateOrder: (id: number, updates: Partial<Order>) => void;
  removeOrder: (id: number) => void;
  
  // 重置方法
  resetTradingState: () => void;
}

// 初始状态
const initialState = {
  selectedSymbol: null,
  selectedStrategy: null,
  strategyParams: {},
  tradingStatus: 'stopped' as TradingStatus,
  isTradingEnabled: false,
  positions: [],
  orders: [],
  marketData: null,
  klineData: [],
  tradingStats: null,
  accountInfo: null,
};

// 创建交易状态管理
export const useTradingStore = create<TradingState>()(
  devtools(
    (set, get) => ({
      ...initialState,
      
      // 设置更新方法
      updateSelectedSymbol: (symbol) => set({ selectedSymbol: symbol }),
      updateSelectedStrategy: (strategyId) => set({ selectedStrategy: strategyId }),
      updateStrategyParams: (params) => set({ strategyParams: params }),
      updateTradingStatus: (status) => set({ tradingStatus: status }),
      updateTradingEnabled: (enabled) => set({ isTradingEnabled: enabled }),
      
      // 数据更新方法
      updatePositions: (positions) => set({ positions }),
      updateOrders: (orders) => set({ orders }),
      updateMarketData: (data) => set({ marketData: data }),
      updateKlineData: (data) => set({ klineData: data }),
      updateTradingStats: (stats) => set({ tradingStats: stats }),
      updateAccountInfo: (info) => set({ accountInfo: info }),
      
      // 添加/更新单个数据
      addPosition: (position) => set((state) => ({
        positions: [...state.positions, position]
      })),
      
      updatePosition: (id, updates) => set((state) => ({
        positions: state.positions.map(pos => 
          pos.id === id ? { ...pos, ...updates } : pos
        )
      })),
      
      removePosition: (id) => set((state) => ({
        positions: state.positions.filter(pos => pos.id !== id)
      })),
      
      addOrder: (order) => set((state) => ({
        orders: [...state.orders, order]
      })),
      
      updateOrder: (id, updates) => set((state) => ({
        orders: state.orders.map(order => 
          order.id === id ? { ...order, ...updates } : order
        )
      })),
      
      removeOrder: (id) => set((state) => ({
        orders: state.orders.filter(order => order.id !== id)
      })),
      
      // 重置方法
      resetTradingState: () => set(initialState),
    }),
    {
      name: 'trading-store',
    }
  )
);
