// 通用类型定义
export interface ApiResponse<T = any> {
  success: boolean;
  data: T;
  message?: string;
  code?: number;
}

export interface PaginationParams {
  page?: number;
  pageSize?: number;
  limit?: number;
  offset?: number;
}

export interface PaginationResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// 用户相关类型
export interface User {
  id: number;
  username: string;
  email: string;
  fullName?: string;
  isActive: boolean;
  isSuperuser: boolean;
  createdAt: string;
  updatedAt: string;
  lastLogin?: string;
  preferences?: Record<string, any>;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  accessToken: string;
  tokenType: string;
  expiresIn: number;
  user: User;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  fullName?: string;
}

// 交易相关类型
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
  strategyId?: number;
  createdAt: string;
  updatedAt: string;
  closedAt?: string;
  remark?: string;
}

export interface Order {
  id: number;
  symbol: string;
  side: 'buy' | 'sell';
  orderType: 'market' | 'limit' | 'stop_loss' | 'take_profit';
  quantity: number;
  price?: number;
  stopPrice?: number;
  takeProfitPrice?: number;
  filledQuantity: number;
  remainingQuantity: number;
  status: 'pending' | 'partially_filled' | 'filled' | 'cancelled' | 'rejected';
  strategyId?: number;
  orderId: string;
  createdAt: string;
  updatedAt: string;
  cancelledAt?: string;
  remark?: string;
}

export interface Trade {
  id: number;
  symbol: string;
  side: 'buy' | 'sell';
  orderType: 'market' | 'limit' | 'stop_loss' | 'take_profit';
  quantity: number;
  price: number;
  fee: number;
  pnl: number;
  status: 'pending' | 'filled' | 'cancelled' | 'rejected';
  strategyId?: number;
  orderId: string;
  createdAt: string;
  updatedAt: string;
  filledAt?: string;
  remark?: string;
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

// 策略相关类型
export interface Strategy {
  id: number;
  name: string;
  strategyType: 'ut_bot' | 'mean_reversion' | 'momentum' | 'arbitrage' | 'custom';
  description?: string;
  isActive: boolean;
  isEnabled: boolean;
  createdAt: string;
  updatedAt: string;
  lastRunAt?: string;
  totalTrades: number;
  winningTrades: number;
  totalPnl: number;
  maxDrawdown: number;
  sharpeRatio: number;
  parameters?: StrategyParameter[];
}

export interface StrategyParameter {
  id: number;
  strategyId: number;
  parameterName: string;
  parameterValue: string;
  parameterType: 'int' | 'float' | 'bool' | 'string';
  description?: string;
  createdAt: string;
  updatedAt: string;
}

export interface StrategyCreateRequest {
  name: string;
  strategyType: string;
  description?: string;
  parameters?: Record<string, any>;
}

export interface StrategyUpdateRequest {
  name?: string;
  description?: string;
  isActive?: boolean;
  isEnabled?: boolean;
  parameters?: Record<string, any>;
}

// 通知相关类型
export interface Notification {
  id: number;
  notificationType: 'trade_executed' | 'stop_loss' | 'take_profit' | 'system_error' | 'risk_limit';
  title: string;
  message: string;
  level: 'info' | 'warning' | 'error' | 'critical';
  isRead: boolean;
  isSent: boolean;
  sentAt?: string;
  createdAt: string;
  data?: Record<string, any>;
}

export type NotificationType = 'trade_executed' | 'stop_loss' | 'take_profit' | 'system_error' | 'risk_limit';
export type NotificationLevel = 'info' | 'warning' | 'error' | 'critical';

// WebSocket相关类型
export interface WebSocketMessage {
  type: string;
  data?: any;
  timestamp?: number;
}

export interface MarketDataMessage extends WebSocketMessage {
  type: 'market_data';
  data: MarketData;
}

export interface TradeMessage extends WebSocketMessage {
  type: 'trade';
  data: Trade;
}

export interface OrderMessage extends WebSocketMessage {
  type: 'order';
  data: Order;
}

export interface PositionMessage extends WebSocketMessage {
  type: 'position';
  data: Position;
}

export interface NotificationMessage extends WebSocketMessage {
  type: 'notification';
  data: Notification;
}

// 图表相关类型
export interface ChartConfig {
  symbol: string;
  timeframe: string;
  indicators?: string[];
  theme?: 'light' | 'dark';
}

export interface TechnicalIndicator {
  name: string;
  type: 'overlay' | 'oscillator';
  parameters: Record<string, any>;
  color?: string;
  visible: boolean;
}

// 表单相关类型
export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'number' | 'select' | 'checkbox' | 'textarea';
  required?: boolean;
  placeholder?: string;
  options?: Array<{ label: string; value: any }>;
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
    message?: string;
  };
}

// 路由相关类型
export interface RouteConfig {
  path: string;
  component: React.ComponentType;
  exact?: boolean;
  protected?: boolean;
  roles?: string[];
}

// 主题相关类型
export interface Theme {
  name: string;
  colors: {
    primary: string;
    secondary: string;
    success: string;
    warning: string;
    error: string;
    background: string;
    surface: string;
    text: string;
    textSecondary: string;
  };
}

// 配置相关类型
export interface AppConfig {
  apiUrl: string;
  wsUrl: string;
  appName: string;
  version: string;
  theme: Theme;
  features: {
    trading: boolean;
    strategies: boolean;
    notifications: boolean;
    analytics: boolean;
  };
}
