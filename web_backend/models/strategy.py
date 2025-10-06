"""
策略模型
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base


class Strategy(Base):
    """策略模型"""
    __tablename__ = "strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    strategy_type = Column(String(50), nullable=False)  # ut_bot, mean_reversion, momentum, arbitrage
    description = Column(Text)
    is_active = Column(Boolean, default=False)
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_run_at = Column(DateTime(timezone=True))
    
    # 策略统计
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    total_pnl = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    
    # 关联关系
    user = relationship("User", back_populates="strategies")
    parameters = relationship("StrategyParameter", back_populates="strategy", cascade="all, delete-orphan")
    trades = relationship("Trade", back_populates="strategy")
    orders = relationship("Order", back_populates="strategy")
    
    def __repr__(self):
        return f"<Strategy(id={self.id}, name='{self.name}', type='{self.strategy_type}')>"


class StrategyParameter(Base):
    """策略参数模型"""
    __tablename__ = "strategy_parameters"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False)
    parameter_name = Column(String(100), nullable=False)
    parameter_value = Column(Text, nullable=False)  # JSON格式存储参数值
    parameter_type = Column(String(20), nullable=False)  # int, float, bool, string
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系
    strategy = relationship("Strategy", back_populates="parameters")
    
    def __repr__(self):
        return f"<StrategyParameter(id={self.id}, strategy_id={self.strategy_id}, name='{self.parameter_name}')>"
