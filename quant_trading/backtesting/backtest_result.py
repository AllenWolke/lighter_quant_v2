"""
回测结果
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt


@dataclass
class BacktestResult:
    """回测结果"""
    
    # 基本信息
    strategy_name: str
    start_date: datetime
    end_date: datetime
    
    # 资金信息
    initial_capital: float
    final_capital: float
    total_return: float
    annual_return: float
    
    # 风险指标
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    
    # 交易信息
    total_trades: int
    
    # 详细数据
    equity_curve: List[float]
    trades: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "strategy_name": self.strategy_name,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "initial_capital": self.initial_capital,
            "final_capital": self.final_capital,
            "total_return": self.total_return,
            "annual_return": self.annual_return,
            "sharpe_ratio": self.sharpe_ratio,
            "max_drawdown": self.max_drawdown,
            "win_rate": self.win_rate,
            "total_trades": self.total_trades
        }
        
    def print_summary(self):
        """打印回测摘要"""
        print(f"\n=== {self.strategy_name} 回测结果 ===")
        print(f"回测期间: {self.start_date.strftime('%Y-%m-%d')} - {self.end_date.strftime('%Y-%m-%d')}")
        print(f"初始资金: ${self.initial_capital:,.2f}")
        print(f"最终资金: ${self.final_capital:,.2f}")
        print(f"总收益率: {self.total_return:.2%}")
        print(f"年化收益率: {self.annual_return:.2%}")
        print(f"夏普比率: {self.sharpe_ratio:.2f}")
        print(f"最大回撤: {self.max_drawdown:.2%}")
        print(f"胜率: {self.win_rate:.2%}")
        print(f"总交易次数: {self.total_trades}")
        
    def plot_equity_curve(self, save_path: Optional[str] = None):
        """绘制权益曲线"""
        plt.figure(figsize=(12, 6))
        plt.plot(self.equity_curve)
        plt.title(f"{self.strategy_name} - 权益曲线")
        plt.xlabel("时间")
        plt.ylabel("资金")
        plt.grid(True)
        
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()
            
    def plot_drawdown(self, save_path: Optional[str] = None):
        """绘制回撤曲线"""
        # 计算回撤
        peak = self.equity_curve[0]
        drawdowns = []
        
        for value in self.equity_curve:
            if value > peak:
                peak = value
            drawdowns.append((peak - value) / peak)
            
        plt.figure(figsize=(12, 6))
        plt.fill_between(range(len(drawdowns)), drawdowns, 0, alpha=0.3, color='red')
        plt.plot(drawdowns, color='red')
        plt.title(f"{self.strategy_name} - 回撤曲线")
        plt.xlabel("时间")
        plt.ylabel("回撤")
        plt.grid(True)
        
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()
            
    def get_monthly_returns(self) -> pd.DataFrame:
        """获取月度收益率"""
        if not self.equity_curve:
            return pd.DataFrame()
            
        # 创建日期索引，长度与equity_curve匹配
        dates = pd.date_range(start=self.start_date, periods=len(self.equity_curve), freq='D')
        equity_series = pd.Series(self.equity_curve, index=dates)
        
        # 计算月度收益率
        monthly_returns = equity_series.resample('ME').last().pct_change().dropna()
        
        return monthly_returns.to_frame('monthly_return')
        
    def get_trade_analysis(self) -> Dict[str, Any]:
        """获取交易分析"""
        if not self.trades:
            return {}
            
        trade_returns = [trade.get("pnl", 0) for trade in self.trades]
        
        analysis = {
            "total_trades": len(self.trades),
            "winning_trades": len([r for r in trade_returns if r > 0]),
            "losing_trades": len([r for r in trade_returns if r < 0]),
            "win_rate": len([r for r in trade_returns if r > 0]) / max(1, len(trade_returns)),
            "avg_win": sum([r for r in trade_returns if r > 0]) / max(1, len([r for r in trade_returns if r > 0])),
            "avg_loss": sum([r for r in trade_returns if r < 0]) / max(1, len([r for r in trade_returns if r < 0])),
            "profit_factor": abs(sum([r for r in trade_returns if r > 0]) / sum([r for r in trade_returns if r < 0])) if sum([r for r in trade_returns if r < 0]) != 0 else float('inf'),
            "max_win": max(trade_returns) if trade_returns else 0,
            "max_loss": min(trade_returns) if trade_returns else 0
        }
        
        return analysis
