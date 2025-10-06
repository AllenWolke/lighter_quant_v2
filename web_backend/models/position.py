"""
持仓模型
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base


class Position(Base):
    """持仓模型"""
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    side = Column(String(10), nullable=False)  # long, short
    quantity = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    unrealized_pnl = Column(Float, default=0.0)  # 未实现盈亏
    pnl_ratio = Column(Float, default=0.0)  # 盈亏比例
    margin = Column(Float, default=0.0)  # 保证金
    leverage = Column(Float, default=1.0)  # 杠杆倍数
    stop_loss_price = Column(Float)  # 止损价格
    take_profit_price = Column(Float)  # 止盈价格
    is_active = Column(Boolean, default=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    closed_at = Column(DateTime(timezone=True))
    remark = Column(Text)
    
    # 关联关系
    user = relationship("User", back_populates="positions")
    strategy = relationship("Strategy")
    
    def __repr__(self):
        return f"<Position(id={self.id}, symbol='{self.symbol}', side='{self.side}', quantity={self.quantity})>"
