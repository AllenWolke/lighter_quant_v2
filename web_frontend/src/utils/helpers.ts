// 工具函数

import { format, parseISO, isValid } from 'date-fns';
import { zhCN } from 'date-fns/locale';

// 数字格式化
export const formatNumber = (
  value: number | string,
  options: {
    precision?: number;
    prefix?: string;
    suffix?: string;
    thousandSeparator?: boolean;
  } = {}
): string => {
  const {
    precision = 2,
    prefix = '',
    suffix = '',
    thousandSeparator = true,
  } = options;

  const num = typeof value === 'string' ? parseFloat(value) : value;
  
  if (isNaN(num)) return '0';

  let formatted = num.toFixed(precision);
  
  if (thousandSeparator) {
    formatted = formatted.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  }
  
  return `${prefix}${formatted}${suffix}`;
};

// 货币格式化
export const formatCurrency = (
  value: number | string,
  currency: string = 'USDT',
  precision: number = 2
): string => {
  return formatNumber(value, {
    precision,
    prefix: '$',
    suffix: ` ${currency}`,
    thousandSeparator: true,
  });
};

// 百分比格式化
export const formatPercentage = (
  value: number | string,
  precision: number = 2
): string => {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  return formatNumber(num, {
    precision,
    suffix: '%',
  });
};

// 日期时间格式化
export const formatDateTime = (
  date: string | Date,
  formatStr: string = 'yyyy-MM-dd HH:mm:ss'
): string => {
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    
    if (!isValid(dateObj)) {
      return '无效日期';
    }
    
    return format(dateObj, formatStr, { locale: zhCN });
  } catch (error) {
    console.error('日期格式化错误:', error);
    return '无效日期';
  }
};

// 相对时间格式化
export const formatRelativeTime = (date: string | Date): string => {
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - dateObj.getTime()) / 1000);
    
    if (diffInSeconds < 60) {
      return '刚刚';
    } else if (diffInSeconds < 3600) {
      const minutes = Math.floor(diffInSeconds / 60);
      return `${minutes}分钟前`;
    } else if (diffInSeconds < 86400) {
      const hours = Math.floor(diffInSeconds / 3600);
      return `${hours}小时前`;
    } else if (diffInSeconds < 2592000) {
      const days = Math.floor(diffInSeconds / 86400);
      return `${days}天前`;
    } else {
      return formatDateTime(dateObj, 'yyyy-MM-dd');
    }
  } catch (error) {
    console.error('相对时间格式化错误:', error);
    return '未知时间';
  }
};

// 颜色工具
export const getColorByValue = (
  value: number,
  options: {
    positiveColor?: string;
    negativeColor?: string;
    neutralColor?: string;
  } = {}
): string => {
  const {
    positiveColor = '#52c41a',
    negativeColor = '#ff4d4f',
    neutralColor = '#8c8c8c',
  } = options;

  if (value > 0) return positiveColor;
  if (value < 0) return negativeColor;
  return neutralColor;
};

// 状态颜色映射
export const getStatusColor = (status: string): string => {
  const statusColorMap: Record<string, string> = {
    // 订单状态
    pending: '#1890ff',
    partially_filled: '#faad14',
    filled: '#52c41a',
    cancelled: '#8c8c8c',
    rejected: '#ff4d4f',
    
    // 持仓状态
    active: '#52c41a',
    closed: '#8c8c8c',
    
    // 策略状态
    running: '#52c41a',
    stopped: '#8c8c8c',
    paused: '#faad14',
    
    // 风险等级
    low: '#52c41a',
    medium: '#faad14',
    high: '#ff4d4f',
    
    // 通知级别
    info: '#1890ff',
    warning: '#faad14',
    error: '#ff4d4f',
    critical: '#722ed1',
  };
  
  return statusColorMap[status] || '#8c8c8c';
};

// 计算盈亏百分比
export const calculatePnLPercentage = (
  entryPrice: number,
  currentPrice: number,
  side: 'long' | 'short'
): number => {
  if (side === 'long') {
    return ((currentPrice - entryPrice) / entryPrice) * 100;
  } else {
    return ((entryPrice - currentPrice) / entryPrice) * 100;
  }
};

// 计算盈亏金额
export const calculatePnLAmount = (
  entryPrice: number,
  currentPrice: number,
  quantity: number,
  side: 'long' | 'short'
): number => {
  if (side === 'long') {
    return (currentPrice - entryPrice) * quantity;
  } else {
    return (entryPrice - currentPrice) * quantity;
  }
};

// 计算胜率
export const calculateWinRate = (trades: Array<{ pnl: number }>): number => {
  if (trades.length === 0) return 0;
  const winningTrades = trades.filter(trade => trade.pnl > 0).length;
  return (winningTrades / trades.length) * 100;
};

// 计算夏普比率
export const calculateSharpeRatio = (
  returns: number[],
  riskFreeRate: number = 0.02
): number => {
  if (returns.length === 0) return 0;
  
  const avgReturn = returns.reduce((sum, ret) => sum + ret, 0) / returns.length;
  const variance = returns.reduce((sum, ret) => sum + Math.pow(ret - avgReturn, 2), 0) / returns.length;
  const stdDev = Math.sqrt(variance);
  
  if (stdDev === 0) return 0;
  
  return (avgReturn - riskFreeRate) / stdDev;
};

// 计算最大回撤
export const calculateMaxDrawdown = (equity: number[]): number => {
  if (equity.length === 0) return 0;
  
  let maxDrawdown = 0;
  let peak = equity[0];
  
  for (let i = 1; i < equity.length; i++) {
    if (equity[i] > peak) {
      peak = equity[i];
    } else {
      const drawdown = (peak - equity[i]) / peak;
      maxDrawdown = Math.max(maxDrawdown, drawdown);
    }
  }
  
  return maxDrawdown * 100;
};

// 生成随机ID
export const generateId = (length: number = 8): string => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
};

// 防抖函数
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

// 节流函数
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle: boolean;
  
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
};

// 深拷贝
export const deepClone = <T>(obj: T): T => {
  if (obj === null || typeof obj !== 'object') return obj;
  if (obj instanceof Date) return new Date(obj.getTime()) as any;
  if (obj instanceof Array) return obj.map(item => deepClone(item)) as any;
  if (typeof obj === 'object') {
    const clonedObj: any = {};
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        clonedObj[key] = deepClone(obj[key]);
      }
    }
    return clonedObj;
  }
  return obj;
};

// 数组去重
export const uniqueArray = <T>(array: T[], key?: keyof T): T[] => {
  if (!key) {
    return [...new Set(array)];
  }
  
  const seen = new Set();
  return array.filter(item => {
    const value = item[key];
    if (seen.has(value)) {
      return false;
    }
    seen.add(value);
    return true;
  });
};

// 数组分组
export const groupBy = <T, K extends keyof T>(
  array: T[],
  key: K
): Record<string, T[]> => {
  return array.reduce((groups, item) => {
    const group = String(item[key]);
    groups[group] = groups[group] || [];
    groups[group].push(item);
    return groups;
  }, {} as Record<string, T[]>);
};

// 数组排序
export const sortBy = <T>(
  array: T[],
  key: keyof T,
  direction: 'asc' | 'desc' = 'asc'
): T[] => {
  return [...array].sort((a, b) => {
    const aVal = a[key];
    const bVal = b[key];
    
    if (aVal < bVal) return direction === 'asc' ? -1 : 1;
    if (aVal > bVal) return direction === 'asc' ? 1 : -1;
    return 0;
  });
};

// 数组分页
export const paginate = <T>(
  array: T[],
  page: number,
  pageSize: number
): { data: T[]; total: number; page: number; pageSize: number; totalPages: number } => {
  const total = array.length;
  const totalPages = Math.ceil(total / pageSize);
  const startIndex = (page - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const data = array.slice(startIndex, endIndex);
  
  return {
    data,
    total,
    page,
    pageSize,
    totalPages,
  };
};

// 本地存储工具
export const storage = {
  get: <T>(key: string, defaultValue?: T): T | null => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue || null;
    } catch (error) {
      console.error('读取本地存储失败:', error);
      return defaultValue || null;
    }
  },
  
  set: <T>(key: string, value: T): void => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error('保存本地存储失败:', error);
    }
  },
  
  remove: (key: string): void => {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error('删除本地存储失败:', error);
    }
  },
  
  clear: (): void => {
    try {
      localStorage.clear();
    } catch (error) {
      console.error('清空本地存储失败:', error);
    }
  },
};

// URL参数工具
export const urlUtils = {
  getParams: (): Record<string, string> => {
    const params = new URLSearchParams(window.location.search);
    const result: Record<string, string> = {};
    params.forEach((value, key) => {
      result[key] = value;
    });
    return result;
  },
  
  setParam: (key: string, value: string): void => {
    const url = new URL(window.location.href);
    url.searchParams.set(key, value);
    window.history.replaceState({}, '', url.toString());
  },
  
  removeParam: (key: string): void => {
    const url = new URL(window.location.href);
    url.searchParams.delete(key);
    window.history.replaceState({}, '', url.toString());
  },
};

// 文件下载工具
export const downloadFile = (content: string, filename: string, mimeType: string = 'text/plain'): void => {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

// 复制到剪贴板
export const copyToClipboard = async (text: string): Promise<boolean> => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (error) {
    console.error('复制到剪贴板失败:', error);
    return false;
  }
};

// 验证工具
export const validators = {
  email: (email: string): boolean => {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return pattern.test(email);
  },
  
  phone: (phone: string): boolean => {
    const pattern = /^1[3-9]\d{9}$/;
    return pattern.test(phone);
  },
  
  url: (url: string): boolean => {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  },
  
  number: (value: string | number): boolean => {
    return !isNaN(Number(value));
  },
  
  positive: (value: number): boolean => {
    return value > 0;
  },
  
  range: (value: number, min: number, max: number): boolean => {
    return value >= min && value <= max;
  },
};

// 错误处理工具
export const errorHandler = {
  parse: (error: any): string => {
    if (typeof error === 'string') return error;
    if (error?.message) return error.message;
    if (error?.response?.data?.message) return error.response.data.message;
    if (error?.response?.statusText) return error.response.statusText;
    return '未知错误';
  },
  
  isNetworkError: (error: any): boolean => {
    return error?.code === 'NETWORK_ERROR' || error?.message?.includes('Network Error');
  },
  
  isAuthError: (error: any): boolean => {
    return error?.response?.status === 401;
  },
  
  isServerError: (error: any): boolean => {
    return error?.response?.status >= 500;
  },
};
