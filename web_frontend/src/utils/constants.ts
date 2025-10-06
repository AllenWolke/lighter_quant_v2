// 应用常量配置

// API配置
export const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  WS_URL: process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws',
  TIMEOUT: 10000,
};

// 交易对配置
export const SYMBOLS = [
  { value: 'ETH/USDT', label: 'ETH/USDT', base: 'ETH', quote: 'USDT' },
  { value: 'BTC/USDT', label: 'BTC/USDT', base: 'BTC', quote: 'USDT' },
  { value: 'BNB/USDT', label: 'BNB/USDT', base: 'BNB', quote: 'USDT' },
  { value: 'ADA/USDT', label: 'ADA/USDT', base: 'ADA', quote: 'USDT' },
  { value: 'SOL/USDT', label: 'SOL/USDT', base: 'SOL', quote: 'USDT' },
  { value: 'DOT/USDT', label: 'DOT/USDT', base: 'DOT', quote: 'USDT' },
  { value: 'MATIC/USDT', label: 'MATIC/USDT', base: 'MATIC', quote: 'USDT' },
  { value: 'AVAX/USDT', label: 'AVAX/USDT', base: 'AVAX', quote: 'USDT' },
];

// 时间周期配置
export const TIMEFRAMES = [
  { value: '1m', label: '1分钟', seconds: 60 },
  { value: '5m', label: '5分钟', seconds: 300 },
  { value: '15m', label: '15分钟', seconds: 900 },
  { value: '30m', label: '30分钟', seconds: 1800 },
  { value: '1h', label: '1小时', seconds: 3600 },
  { value: '4h', label: '4小时', seconds: 14400 },
  { value: '1d', label: '1天', seconds: 86400 },
];

// 策略类型配置
export const STRATEGY_TYPES = [
  { 
    value: 'ut_bot', 
    label: 'UT Bot策略', 
    description: '基于TradingView UT Bot信号的交易策略',
    parameters: [
      { name: 'atr_period', type: 'int', label: 'ATR周期', default: 14, min: 1, max: 100 },
      { name: 'atr_multiplier', type: 'float', label: 'ATR倍数', default: 2.0, min: 0.1, max: 10.0 },
      { name: 'heikin_ashi', type: 'bool', label: '使用Heikin Ashi', default: true },
      { name: 'crossover_threshold', type: 'float', label: '交叉阈值', default: 0.01, min: 0.001, max: 0.1 },
    ]
  },
  { 
    value: 'mean_reversion', 
    label: '均值回归策略', 
    description: '价格偏离均值时的反向交易策略',
    parameters: [
      { name: 'ma_period', type: 'int', label: '移动平均周期', default: 20, min: 5, max: 200 },
      { name: 'deviation_threshold', type: 'float', label: '偏离阈值', default: 2.0, min: 0.5, max: 5.0 },
      { name: 'rsi_period', type: 'int', label: 'RSI周期', default: 14, min: 5, max: 50 },
      { name: 'rsi_oversold', type: 'float', label: 'RSI超卖线', default: 30, min: 10, max: 40 },
      { name: 'rsi_overbought', type: 'float', label: 'RSI超买线', default: 70, min: 60, max: 90 },
    ]
  },
  { 
    value: 'momentum', 
    label: '动量策略', 
    description: '跟随价格趋势的交易策略',
    parameters: [
      { name: 'ma_short', type: 'int', label: '短期均线', default: 10, min: 5, max: 50 },
      { name: 'ma_long', type: 'int', label: '长期均线', default: 30, min: 10, max: 100 },
      { name: 'volume_threshold', type: 'float', label: '成交量阈值', default: 1.5, min: 1.0, max: 5.0 },
      { name: 'trend_strength', type: 'float', label: '趋势强度', default: 0.6, min: 0.1, max: 1.0 },
    ]
  },
  { 
    value: 'arbitrage', 
    label: '套利策略', 
    description: '不同市场间价差套利策略',
    parameters: [
      { name: 'price_diff_threshold', type: 'float', label: '价差阈值', default: 0.01, min: 0.001, max: 0.1 },
      { name: 'min_profit', type: 'float', label: '最小利润', default: 0.005, min: 0.001, max: 0.05 },
      { name: 'max_position_size', type: 'float', label: '最大仓位', default: 1000, min: 100, max: 10000 },
      { name: 'execution_delay', type: 'int', label: '执行延迟(ms)', default: 100, min: 10, max: 1000 },
    ]
  },
];

// 订单类型配置
export const ORDER_TYPES = [
  { value: 'market', label: '市价单', description: '以当前市场价格立即成交' },
  { value: 'limit', label: '限价单', description: '以指定价格或更好的价格成交' },
  { value: 'stop_loss', label: '止损单', description: '当价格达到止损价格时触发市价单' },
  { value: 'take_profit', label: '止盈单', description: '当价格达到止盈价格时触发市价单' },
];

// 订单状态配置
export const ORDER_STATUS = [
  { value: 'pending', label: '待成交', color: 'processing' },
  { value: 'partially_filled', label: '部分成交', color: 'warning' },
  { value: 'filled', label: '已成交', color: 'success' },
  { value: 'cancelled', label: '已取消', color: 'default' },
  { value: 'rejected', label: '已拒绝', color: 'error' },
];

// 持仓方向配置
export const POSITION_SIDES = [
  { value: 'long', label: '多头', color: 'green' },
  { value: 'short', label: '空头', color: 'red' },
];

// 通知类型配置
export const NOTIFICATION_TYPES = [
  { value: 'trade_executed', label: '交易执行', description: '订单成交时通知' },
  { value: 'stop_loss', label: '止损触发', description: '止损订单触发时通知' },
  { value: 'take_profit', label: '止盈触发', description: '止盈订单触发时通知' },
  { value: 'system_error', label: '系统错误', description: '系统发生错误时通知' },
  { value: 'risk_limit', label: '风险限制', description: '触发风险限制时通知' },
];

// 通知级别配置
export const NOTIFICATION_LEVELS = [
  { value: 'info', label: '信息', color: 'blue' },
  { value: 'warning', label: '警告', color: 'orange' },
  { value: 'error', label: '错误', color: 'red' },
  { value: 'critical', label: '严重', color: 'purple' },
];

// 技术指标配置
export const TECHNICAL_INDICATORS = [
  { 
    value: 'ma5', 
    label: 'MA5', 
    type: 'overlay',
    color: '#ff7300',
    description: '5周期移动平均线'
  },
  { 
    value: 'ma10', 
    label: 'MA10', 
    type: 'overlay',
    color: '#00ff00',
    description: '10周期移动平均线'
  },
  { 
    value: 'ma20', 
    label: 'MA20', 
    type: 'overlay',
    color: '#0088fe',
    description: '20周期移动平均线'
  },
  { 
    value: 'ma50', 
    label: 'MA50', 
    type: 'overlay',
    color: '#ff00ff',
    description: '50周期移动平均线'
  },
  { 
    value: 'ema12', 
    label: 'EMA12', 
    type: 'overlay',
    color: '#00d4aa',
    description: '12周期指数移动平均线'
  },
  { 
    value: 'ema26', 
    label: 'EMA26', 
    type: 'overlay',
    color: '#722ed1',
    description: '26周期指数移动平均线'
  },
  { 
    value: 'macd', 
    label: 'MACD', 
    type: 'oscillator',
    color: '#1890ff',
    description: 'MACD指标'
  },
  { 
    value: 'rsi', 
    label: 'RSI', 
    type: 'oscillator',
    color: '#fa8c16',
    description: '相对强弱指数'
  },
  { 
    value: 'bollinger', 
    label: '布林带', 
    type: 'overlay',
    color: '#52c41a',
    description: '布林带指标'
  },
];

// 风险等级配置
export const RISK_LEVELS = [
  { value: 'low', label: '低风险', color: '#52c41a', description: '保守型投资' },
  { value: 'medium', label: '中风险', color: '#faad14', description: '平衡型投资' },
  { value: 'high', label: '高风险', color: '#ff4d4f', description: '激进型投资' },
];

// 图表配置
export const CHART_CONFIG = {
  COLORS: {
    primary: '#1890ff',
    success: '#52c41a',
    warning: '#faad14',
    error: '#ff4d4f',
    info: '#13c2c2',
    purple: '#722ed1',
    orange: '#fa8c16',
  },
  CANDLESTICK: {
    upColor: '#52c41a',
    downColor: '#ff4d4f',
    borderUpColor: '#52c41a',
    borderDownColor: '#ff4d4f',
    wickUpColor: '#52c41a',
    wickDownColor: '#ff4d4f',
  },
  GRID: {
    strokeDasharray: '3 3',
    stroke: '#f0f0f0',
  },
  AXIS: {
    stroke: '#666',
    fontSize: 12,
  },
};

// 分页配置
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  PAGE_SIZE_OPTIONS: ['10', '20', '50', '100'],
  SHOW_SIZE_CHANGER: true,
  SHOW_QUICK_JUMPER: true,
  SHOW_TOTAL: (total: number, range: [number, number]) => 
    `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
};

// 表格配置
export const TABLE_CONFIG = {
  SCROLL_Y: 400,
  SIZE: 'small' as const,
  BORDERED: false,
  SHOW_HEADER: true,
};

// 表单配置
export const FORM_CONFIG = {
  LAYOUT: 'vertical' as const,
  REQUIRED_MARK: true,
  COLON: true,
};

// 主题配置
export const THEME_CONFIG = {
  LIGHT: {
    name: 'light',
    colors: {
      primary: '#1890ff',
      secondary: '#722ed1',
      success: '#52c41a',
      warning: '#faad14',
      error: '#ff4d4f',
      background: '#ffffff',
      surface: '#fafafa',
      text: '#262626',
      textSecondary: '#8c8c8c',
    },
  },
  DARK: {
    name: 'dark',
    colors: {
      primary: '#177ddc',
      secondary: '#642ab5',
      success: '#49aa19',
      warning: '#d89614',
      error: '#dc4446',
      background: '#141414',
      surface: '#1f1f1f',
      text: '#ffffff',
      textSecondary: '#a6a6a6',
    },
  },
};

// 本地存储键名
export const STORAGE_KEYS = {
  TOKEN: 'token',
  USER: 'user',
  THEME: 'theme',
  LANGUAGE: 'language',
  SETTINGS: 'settings',
  TRADING_STATE: 'trading_state',
};

// 默认值配置
export const DEFAULTS = {
  LEVERAGE: 1,
  POSITION_SIZE: 100,
  STOP_LOSS_PERCENT: 2,
  TAKE_PROFIT_PERCENT: 4,
  MAX_POSITION_SIZE: 1000,
  MAX_LEVERAGE: 5,
  RISK_LEVEL: 'medium',
  TIMEFRAME: '1h',
  STRATEGY_TYPE: 'ut_bot',
  ORDER_TYPE: 'market',
  NOTIFICATION_LEVEL: 'info',
};

// 验证规则
export const VALIDATION_RULES = {
  USERNAME: {
    MIN_LENGTH: 3,
    MAX_LENGTH: 20,
    PATTERN: /^[a-zA-Z0-9_]+$/,
  },
  PASSWORD: {
    MIN_LENGTH: 6,
    MAX_LENGTH: 50,
  },
  EMAIL: {
    PATTERN: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  },
  AMOUNT: {
    MIN: 0.0001,
    MAX: 1000000,
    PRECISION: 4,
  },
  PRICE: {
    MIN: 0.0001,
    MAX: 1000000,
    PRECISION: 2,
  },
  PERCENTAGE: {
    MIN: 0,
    MAX: 100,
    PRECISION: 2,
  },
};

// 错误消息
export const ERROR_MESSAGES = {
  NETWORK_ERROR: '网络连接失败，请检查网络设置',
  UNAUTHORIZED: '登录已过期，请重新登录',
  FORBIDDEN: '没有权限执行此操作',
  NOT_FOUND: '请求的资源不存在',
  SERVER_ERROR: '服务器内部错误，请稍后重试',
  VALIDATION_ERROR: '输入数据格式不正确',
  TRADING_DISABLED: '交易功能已禁用',
  INSUFFICIENT_BALANCE: '账户余额不足',
  POSITION_LIMIT: '持仓数量已达上限',
  RISK_LIMIT: '触发风险限制',
};

// 成功消息
export const SUCCESS_MESSAGES = {
  LOGIN_SUCCESS: '登录成功',
  LOGOUT_SUCCESS: '退出成功',
  SAVE_SUCCESS: '保存成功',
  UPDATE_SUCCESS: '更新成功',
  DELETE_SUCCESS: '删除成功',
  ORDER_CREATED: '订单创建成功',
  ORDER_CANCELLED: '订单取消成功',
  POSITION_CLOSED: '持仓关闭成功',
  STRATEGY_STARTED: '策略启动成功',
  STRATEGY_STOPPED: '策略停止成功',
  NOTIFICATION_SENT: '通知发送成功',
};
