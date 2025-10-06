"""
数学工具
"""

import math
import numpy as np
from typing import List, Tuple, Optional


class MathUtils:
    """数学工具类"""
    
    @staticmethod
    def calculate_percentage_change(old_value: float, new_value: float) -> float:
        """
        计算百分比变化
        
        Args:
            old_value: 旧值
            new_value: 新值
            
        Returns:
            百分比变化
        """
        if old_value == 0:
            return 0
        return (new_value - old_value) / old_value * 100
        
    @staticmethod
    def calculate_compound_return(returns: List[float]) -> float:
        """
        计算复合收益率
        
        Args:
            returns: 收益率列表
            
        Returns:
            复合收益率
        """
        if not returns:
            return 0
            
        compound_return = 1.0
        for ret in returns:
            compound_return *= (1 + ret)
            
        return compound_return - 1
        
    @staticmethod
    def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
        """
        计算夏普比率
        
        Args:
            returns: 收益率列表
            risk_free_rate: 无风险利率
            
        Returns:
            夏普比率
        """
        if not returns:
            return 0
            
        excess_returns = [r - risk_free_rate for r in returns]
        mean_excess_return = np.mean(excess_returns)
        std_excess_return = np.std(excess_returns)
        
        if std_excess_return == 0:
            return 0
            
        return mean_excess_return / std_excess_return
        
    @staticmethod
    def calculate_max_drawdown(equity_curve: List[float]) -> Tuple[float, int, int]:
        """
        计算最大回撤
        
        Args:
            equity_curve: 权益曲线
            
        Returns:
            (最大回撤, 回撤开始位置, 回撤结束位置)
        """
        if not equity_curve:
            return 0, 0, 0
            
        peak = equity_curve[0]
        max_dd = 0
        dd_start = 0
        dd_end = 0
        
        for i, value in enumerate(equity_curve):
            if value > peak:
                peak = value
                dd_start = i
            else:
                dd = (peak - value) / peak
                if dd > max_dd:
                    max_dd = dd
                    dd_end = i
                    
        return max_dd, dd_start, dd_end
        
    @staticmethod
    def calculate_calmar_ratio(returns: List[float], max_drawdown: float) -> float:
        """
        计算卡尔玛比率
        
        Args:
            returns: 收益率列表
            max_drawdown: 最大回撤
            
        Returns:
            卡尔玛比率
        """
        if not returns or max_drawdown == 0:
            return 0
            
        annual_return = np.mean(returns) * 252  # 假设252个交易日
        return annual_return / max_drawdown
        
    @staticmethod
    def calculate_sortino_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
        """
        计算索提诺比率
        
        Args:
            returns: 收益率列表
            risk_free_rate: 无风险利率
            
        Returns:
            索提诺比率
        """
        if not returns:
            return 0
            
        excess_returns = [r - risk_free_rate for r in returns]
        mean_excess_return = np.mean(excess_returns)
        
        # 只考虑负收益的标准差
        negative_returns = [r for r in excess_returns if r < 0]
        if not negative_returns:
            return 0
            
        downside_deviation = np.std(negative_returns)
        
        if downside_deviation == 0:
            return 0
            
        return mean_excess_return / downside_deviation
        
    @staticmethod
    def calculate_information_ratio(portfolio_returns: List[float], 
                                   benchmark_returns: List[float]) -> float:
        """
        计算信息比率
        
        Args:
            portfolio_returns: 组合收益率
            benchmark_returns: 基准收益率
            
        Returns:
            信息比率
        """
        if len(portfolio_returns) != len(benchmark_returns):
            return 0
            
        active_returns = [p - b for p, b in zip(portfolio_returns, benchmark_returns)]
        mean_active_return = np.mean(active_returns)
        tracking_error = np.std(active_returns)
        
        if tracking_error == 0:
            return 0
            
        return mean_active_return / tracking_error
        
    @staticmethod
    def calculate_win_rate(trades: List[float]) -> Tuple[float, int, int]:
        """
        计算胜率
        
        Args:
            trades: 交易盈亏列表
            
        Returns:
            (胜率, 盈利交易数, 总交易数)
        """
        if not trades:
            return 0, 0, 0
            
        winning_trades = [t for t in trades if t > 0]
        total_trades = len(trades)
        winning_count = len(winning_trades)
        
        win_rate = winning_count / total_trades if total_trades > 0 else 0
        
        return win_rate, winning_count, total_trades
        
    @staticmethod
    def calculate_profit_factor(trades: List[float]) -> float:
        """
        计算盈利因子
        
        Args:
            trades: 交易盈亏列表
            
        Returns:
            盈利因子
        """
        if not trades:
            return 0
            
        gross_profit = sum(t for t in trades if t > 0)
        gross_loss = abs(sum(t for t in trades if t < 0))
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0
            
        return gross_profit / gross_loss
        
    @staticmethod
    def calculate_average_win_loss(trades: List[float]) -> Tuple[float, float]:
        """
        计算平均盈利和平均亏损
        
        Args:
            trades: 交易盈亏列表
            
        Returns:
            (平均盈利, 平均亏损)
        """
        if not trades:
            return 0, 0
            
        winning_trades = [t for t in trades if t > 0]
        losing_trades = [t for t in trades if t < 0]
        
        avg_win = np.mean(winning_trades) if winning_trades else 0
        avg_loss = abs(np.mean(losing_trades)) if losing_trades else 0
        
        return avg_win, avg_loss
        
    @staticmethod
    def calculate_kelly_criterion(win_rate: float, avg_win: float, avg_loss: float) -> float:
        """
        计算凯利公式
        
        Args:
            win_rate: 胜率
            avg_win: 平均盈利
            avg_loss: 平均亏损
            
        Returns:
            凯利比例
        """
        if avg_loss == 0:
            return 0
            
        kelly = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
        
        return max(0, min(kelly, 1))  # 限制在0-1之间
        
    @staticmethod
    def calculate_volatility_adjusted_position_size(volatility: float, 
                                                   target_volatility: float = 0.02,
                                                   base_position_size: float = 0.1) -> float:
        """
        计算波动率调整的仓位大小
        
        Args:
            volatility: 当前波动率
            target_volatility: 目标波动率
            base_position_size: 基础仓位大小
            
        Returns:
            调整后的仓位大小
        """
        if volatility == 0:
            return base_position_size
            
        adjustment_factor = target_volatility / volatility
        adjusted_size = base_position_size * adjustment_factor
        
        return max(0.01, min(adjusted_size, 0.5))  # 限制在1%-50%之间
        
    @staticmethod
    def calculate_correlation(series1: List[float], series2: List[float]) -> float:
        """
        计算相关系数
        
        Args:
            series1: 序列1
            series2: 序列2
            
        Returns:
            相关系数
        """
        if len(series1) != len(series2) or len(series1) < 2:
            return 0
            
        return np.corrcoef(series1, series2)[0, 1]
        
    @staticmethod
    def calculate_beta(portfolio_returns: List[float], 
                      market_returns: List[float]) -> float:
        """
        计算贝塔系数
        
        Args:
            portfolio_returns: 组合收益率
            market_returns: 市场收益率
            
        Returns:
            贝塔系数
        """
        if len(portfolio_returns) != len(market_returns) or len(portfolio_returns) < 2:
            return 0
            
        covariance = np.cov(portfolio_returns, market_returns)[0, 1]
        market_variance = np.var(market_returns)
        
        if market_variance == 0:
            return 0
            
        return covariance / market_variance
