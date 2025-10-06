"""
Lighter量化交易框架
基于lighter交易所API的量化交易系统
"""

__version__ = "1.0.0"
__author__ = "Quant Trading Team"

from .core.trading_engine import TradingEngine
from .core.data_manager import DataManager
from .core.risk_manager import RiskManager
from .core.position_manager import PositionManager
from .strategies.base_strategy import BaseStrategy
from .utils.config import Config
from .utils.logger import setup_logger

__all__ = [
    "TradingEngine",
    "DataManager", 
    "RiskManager",
    "PositionManager",
    "BaseStrategy",
    "Config",
    "setup_logger"
]
