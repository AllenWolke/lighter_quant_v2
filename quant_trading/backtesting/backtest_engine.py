"""
回测引擎
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from ..utils.config import Config
from ..utils.logger import setup_logger
from ..strategies.base_strategy import BaseStrategy
from .backtest_result import BacktestResult


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, config: Config):
        """
        初始化回测引擎
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.logger = setup_logger("BacktestEngine", config.log_level)
        
        # 回测数据
        self.historical_data: Dict[int, pd.DataFrame] = {}
        
        # 回测状态
        self.current_time = None
        self.start_time = None
        self.end_time = None
        self.initial_capital = 10000.0
        self.current_capital = self.initial_capital
        
        # 交易记录
        self.trades: List[Dict[str, Any]] = []
        self.equity_curve: List[float] = []
        
    def load_historical_data(self, market_id: int, data: List[Dict[str, Any]]):
        """
        加载历史数据
        
        Args:
            market_id: 市场ID
            data: 历史数据列表
        """
        if not data:
            return
            
        # 转换为DataFrame
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        df.set_index('timestamp', inplace=True)
        df.sort_index(inplace=True)
        
        self.historical_data[market_id] = df
        self.logger.info(f"加载市场 {market_id} 历史数据: {len(df)} 条记录")
        
    async def run_backtest(self, strategy: BaseStrategy, 
                          start_date: datetime, end_date: datetime) -> BacktestResult:
        """
        运行回测
        
        Args:
            strategy: 策略实例
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            回测结果
        """
        self.logger.info(f"开始回测: {strategy.name}, {start_date} - {end_date}")
        
        self.start_time = start_date
        self.end_time = end_date
        self.current_time = start_date
        self.current_capital = self.initial_capital
        self.trades = []
        self.equity_curve = [self.initial_capital]
        
        try:
            # 初始化策略
            await strategy.initialize()
            
            # 运行回测循环
            while self.current_time < end_date:
                # 获取当前时间点的市场数据
                market_data = self._get_market_data_at_time(self.current_time)
                
                if market_data:
                    # 执行策略
                    await strategy.process_market_data(market_data)
                    
                # 更新权益曲线
                self.equity_curve.append(self.current_capital)
                
                # 推进时间
                self.current_time += timedelta(minutes=1)
                
            # 停止策略
            await strategy.stop()
            
            # 生成回测结果
            result = self._generate_backtest_result(strategy)
            
            self.logger.info(f"回测完成: 总收益 {result.total_return:.2%}, 夏普比率 {result.sharpe_ratio:.2f}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"回测运行错误: {e}")
            raise
            
    def _get_market_data_at_time(self, current_time: datetime) -> Optional[Dict[int, Dict[str, Any]]]:
        """获取指定时间的市场数据"""
        market_data = {}
        
        for market_id, df in self.historical_data.items():
            # 找到当前时间之前的最新数据
            available_data = df[df.index <= current_time]
            
            if len(available_data) < 20:  # 至少需要20个数据点
                continue
                
            # 获取最近的数据
            recent_data = available_data.tail(20)
            
            market_data[market_id] = {
                "candlesticks": [
                    {
                        "timestamp": int(ts.timestamp()),
                        "open": row["open"],
                        "high": row["high"],
                        "low": row["low"],
                        "close": row["close"],
                        "volume": row["volume"]
                    }
                    for ts, row in recent_data.iterrows()
                ],
                "order_book": None,  # 回测中不模拟订单簿
                "trades": []
            }
            
        return market_data if market_data else None
        
    def _generate_backtest_result(self, strategy: BaseStrategy) -> BacktestResult:
        """生成回测结果"""
        # 计算收益率
        returns = []
        for i in range(1, len(self.equity_curve)):
            ret = (self.equity_curve[i] - self.equity_curve[i-1]) / self.equity_curve[i-1]
            returns.append(ret)
            
        # 计算各种指标
        total_return = (self.current_capital - self.initial_capital) / self.initial_capital
        annual_return = (1 + total_return) ** (252 / len(returns)) - 1 if returns else 0
        
        # 计算夏普比率
        sharpe_ratio = 0
        if returns and np.std(returns) > 0:
            sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252)
            
        # 计算最大回撤
        max_dd, dd_start, dd_end = self._calculate_max_drawdown(self.equity_curve)
        
        # 计算胜率
        trade_returns = [trade.get("pnl", 0) for trade in self.trades]
        win_rate = len([r for r in trade_returns if r > 0]) / len(trade_returns) if trade_returns else 0
        
        return BacktestResult(
            strategy_name=strategy.name,
            start_date=self.start_time,
            end_date=self.end_time,
            initial_capital=self.initial_capital,
            final_capital=self.current_capital,
            total_return=total_return,
            annual_return=annual_return,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_dd,
            win_rate=win_rate,
            total_trades=len(self.trades),
            equity_curve=self.equity_curve,
            trades=self.trades
        )
        
    def _calculate_max_drawdown(self, equity_curve: List[float]) -> tuple[float, int, int]:
        """计算最大回撤"""
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
        
    def record_trade(self, trade_info: Dict[str, Any]):
        """记录交易"""
        trade_info["timestamp"] = self.current_time
        self.trades.append(trade_info)
        
        # 更新资金
        pnl = trade_info.get("pnl", 0)
        self.current_capital += pnl
        
    def get_current_capital(self) -> float:
        """获取当前资金"""
        return self.current_capital
        
    def get_equity_curve(self) -> List[float]:
        """获取权益曲线"""
        return self.equity_curve.copy()
