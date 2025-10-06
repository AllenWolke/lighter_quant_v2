"""
数据处理工具
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta


class DataUtils:
    """数据处理工具类"""
    
    @staticmethod
    def calculate_sma(prices: List[float], period: int) -> List[float]:
        """
        计算简单移动平均线
        
        Args:
            prices: 价格列表
            period: 周期
            
        Returns:
            移动平均线列表
        """
        if len(prices) < period:
            return []
            
        sma = []
        for i in range(period - 1, len(prices)):
            sma.append(np.mean(prices[i - period + 1:i + 1]))
            
        return sma
        
    @staticmethod
    def calculate_ema(prices: List[float], period: int, alpha: Optional[float] = None) -> List[float]:
        """
        计算指数移动平均线
        
        Args:
            prices: 价格列表
            period: 周期
            alpha: 平滑因子，如果为None则自动计算
            
        Returns:
            指数移动平均线列表
        """
        if len(prices) < period:
            return []
            
        if alpha is None:
            alpha = 2.0 / (period + 1)
            
        ema = [prices[0]]
        for i in range(1, len(prices)):
            ema.append(alpha * prices[i] + (1 - alpha) * ema[-1])
            
        return ema
        
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> List[float]:
        """
        计算RSI指标
        
        Args:
            prices: 价格列表
            period: 周期
            
        Returns:
            RSI值列表
        """
        if len(prices) < period + 1:
            return []
            
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        rsi = []
        for i in range(period, len(prices)):
            avg_gain = np.mean(gains[i-period:i])
            avg_loss = np.mean(losses[i-period:i])
            
            if avg_loss == 0:
                rsi.append(100)
            else:
                rs = avg_gain / avg_loss
                rsi.append(100 - (100 / (1 + rs)))
                
        return rsi
        
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, 
                                 std_dev: float = 2.0) -> Tuple[List[float], List[float], List[float]]:
        """
        计算布林带
        
        Args:
            prices: 价格列表
            period: 周期
            std_dev: 标准差倍数
            
        Returns:
            (上轨, 中轨, 下轨)
        """
        if len(prices) < period:
            return [], [], []
            
        sma = DataUtils.calculate_sma(prices, period)
        if not sma:
            return [], [], []
            
        upper_band = []
        lower_band = []
        
        for i in range(period - 1, len(prices)):
            period_prices = prices[i - period + 1:i + 1]
            std = np.std(period_prices)
            mean = sma[i - period + 1]
            
            upper_band.append(mean + std_dev * std)
            lower_band.append(mean - std_dev * std)
            
        return upper_band, sma, lower_band
        
    @staticmethod
    def calculate_macd(prices: List[float], fast_period: int = 12, 
                      slow_period: int = 26, signal_period: int = 9) -> Tuple[List[float], List[float], List[float]]:
        """
        计算MACD指标
        
        Args:
            prices: 价格列表
            fast_period: 快线周期
            slow_period: 慢线周期
            signal_period: 信号线周期
            
        Returns:
            (MACD线, 信号线, 柱状图)
        """
        if len(prices) < slow_period:
            return [], [], []
            
        ema_fast = DataUtils.calculate_ema(prices, fast_period)
        ema_slow = DataUtils.calculate_ema(prices, slow_period)
        
        # 确保两个EMA长度一致
        min_len = min(len(ema_fast), len(ema_slow))
        ema_fast = ema_fast[-min_len:]
        ema_slow = ema_slow[-min_len:]
        
        macd_line = [ema_fast[i] - ema_slow[i] for i in range(len(ema_fast))]
        
        if len(macd_line) < signal_period:
            return macd_line, [], []
            
        signal_line = DataUtils.calculate_ema(macd_line, signal_period)
        
        # 计算柱状图
        histogram = []
        for i in range(len(signal_line)):
            histogram.append(macd_line[i + len(macd_line) - len(signal_line)] - signal_line[i])
            
        return macd_line, signal_line, histogram
        
    @staticmethod
    def calculate_atr(highs: List[float], lows: List[float], closes: List[float], 
                     period: int = 14) -> List[float]:
        """
        计算ATR指标
        
        Args:
            highs: 最高价列表
            lows: 最低价列表
            closes: 收盘价列表
            period: 周期
            
        Returns:
            ATR值列表
        """
        if len(highs) < period + 1:
            return []
            
        true_ranges = []
        for i in range(1, len(highs)):
            tr1 = highs[i] - lows[i]
            tr2 = abs(highs[i] - closes[i-1])
            tr3 = abs(lows[i] - closes[i-1])
            true_ranges.append(max(tr1, tr2, tr3))
            
        atr = []
        for i in range(period - 1, len(true_ranges)):
            atr.append(np.mean(true_ranges[i - period + 1:i + 1]))
            
        return atr
        
    @staticmethod
    def detect_support_resistance(prices: List[float], window: int = 5, 
                                 threshold: float = 0.02) -> Tuple[List[float], List[float]]:
        """
        检测支撑位和阻力位
        
        Args:
            prices: 价格列表
            window: 窗口大小
            threshold: 阈值
            
        Returns:
            (支撑位列表, 阻力位列表)
        """
        if len(prices) < window * 2:
            return [], []
            
        support_levels = []
        resistance_levels = []
        
        for i in range(window, len(prices) - window):
            # 检查是否为局部最低点（支撑位）
            is_support = True
            for j in range(i - window, i + window + 1):
                if j != i and prices[j] <= prices[i]:
                    is_support = False
                    break
                    
            if is_support:
                support_levels.append(prices[i])
                
            # 检查是否为局部最高点（阻力位）
            is_resistance = True
            for j in range(i - window, i + window + 1):
                if j != i and prices[j] >= prices[i]:
                    is_resistance = False
                    break
                    
            if is_resistance:
                resistance_levels.append(prices[i])
                
        return support_levels, resistance_levels
        
    @staticmethod
    def calculate_volatility(prices: List[float], period: int = 20) -> List[float]:
        """
        计算波动率
        
        Args:
            prices: 价格列表
            period: 周期
            
        Returns:
            波动率列表
        """
        if len(prices) < period + 1:
            return []
            
        returns = [prices[i] / prices[i-1] - 1 for i in range(1, len(prices))]
        volatility = []
        
        for i in range(period - 1, len(returns)):
            period_returns = returns[i - period + 1:i + 1]
            volatility.append(np.std(period_returns) * np.sqrt(252))  # 年化波动率
            
        return volatility
        
    @staticmethod
    def resample_data(data: List[Dict[str, Any]], target_interval: str) -> List[Dict[str, Any]]:
        """
        重采样数据
        
        Args:
            data: 原始数据
            target_interval: 目标间隔（如'1H', '4H', '1D'）
            
        Returns:
            重采样后的数据
        """
        if not data:
            return []
            
        # 转换为DataFrame
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        df.set_index('timestamp', inplace=True)
        
        # 重采样
        resampled = df.resample(target_interval).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        
        # 转换回列表
        result = []
        for timestamp, row in resampled.iterrows():
            result.append({
                'timestamp': int(timestamp.timestamp()),
                'open': row['open'],
                'high': row['high'],
                'low': row['low'],
                'close': row['close'],
                'volume': row['volume']
            })
            
        return result
