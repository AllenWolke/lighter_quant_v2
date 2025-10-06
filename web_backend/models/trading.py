"""
交易相关模型
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base


class Trade(Base):
    """交易记录模型"""
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    side = Column(String(10), nullable=False)  # buy, sell
    order_type = Column(String(20), nullable=False)  # market, limit, stop_loss, take_profit
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    fee = Column(Float, default=0.0)
    pnl = Column(Float, default=0.0)  # 已实现盈亏
    status = Column(String(20), default="pending")  # pending, filled, cancelled, rejected
    strategy_id = Column(Integer, ForeignKey("strategies.id"))
    order_id = Column(String(100), unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    filled_at = Column(DateTime(timezone=True))
    remark = Column(Text)
    
    # 关联关系
    user = relationship("User", back_populates="trades")
    strategy = relationship("Strategy", back_populates="trades")
    
    def __repr__(self):
        return f"<Trade(id={self.id}, symbol='{self.symbol}', side='{self.side}', quantity={self.quantity})>"


class Order(Base):
    """订单模型"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    side = Column(String(10), nullable=False)  # buy, sell
    order_type = Column(String(20), nullable=False)  # market, limit, stop_loss, take_profit
    quantity = Column(Float, nullable=False)
    price = Column(Float)
    stop_price = Column(Float)  # 止损价格
    take_profit_price = Column(Float)  # 止盈价格
    filled_quantity = Column(Float, default=0.0)
    remaining_quantity = Column(Float, nullable=False)
    status = Column(String(20), default="pending")  # pending, partially_filled, filled, cancelled, rejected
    strategy_id = Column(Integer, ForeignKey("strategies.id"))
    order_id = Column(String(100), unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    cancelled_at = Column(DateTime(timezone=True))
    remark = Column(Text)
    
    # 关联关系
    user = relationship("User", back_populates="orders")
    strategy = relationship("Strategy", back_populates="orders")
    
    def __repr__(self):
        return f"<Order(id={self.id}, symbol='{self.symbol}', side='{self.side}', quantity={self.quantity})>"
