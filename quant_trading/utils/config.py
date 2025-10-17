"""
配置管理
"""

import yaml
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Config:
    """配置类"""
    
    # Lighter配置
    lighter_config: Dict[str, Any]
    
    # 交易配置
    trading_config: Dict[str, Any]
    
    # 风险配置
    risk_config: Dict[str, Any]
    
    # 通知配置
    notifications_config: Dict[str, Any]
    
    # 数据源配置
    data_sources: Dict[str, Any]
    
    # 策略配置
    strategies: Dict[str, Any]
    
    # 日志配置
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # 便捷属性访问
    @property
    def lighter_base_url(self) -> str:
        """获取Lighter基础URL"""
        return self.lighter_config.get("base_url", "https://testnet.zklighter.elliot.ai")
    
    @property
    def lighter_api_key_private_key(self) -> str:
        """获取Lighter API密钥私钥"""
        return self.lighter_config.get("api_key_private_key", "")
    
    @property
    def lighter_account_index(self) -> int:
        """获取Lighter账户索引"""
        return self.lighter_config.get("account_index", 0)
    
    @property
    def lighter_api_key_index(self) -> int:
        """获取Lighter API密钥索引"""
        return self.lighter_config.get("api_key_index", 0)
    
    @property
    def trading(self) -> Dict[str, Any]:
        """获取交易配置（便捷访问）"""
        return self.trading_config
    
    @property
    def risk_management(self) -> Dict[str, Any]:
        """获取风险管理配置（便捷访问）"""
        return self.risk_config
    
    @property
    def notifications(self) -> Dict[str, Any]:
        """获取通知配置（便捷访问）"""
        return self.notifications_config
    
    @classmethod
    def from_file(cls, config_path: str) -> 'Config':
        """
        从配置文件加载配置
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            配置对象
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
            
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
            
        return cls(
            lighter_config=config_data.get("lighter", {}),
            trading_config=config_data.get("trading", {}),
            risk_config=config_data.get("risk_management", config_data.get("risk", {})),
            notifications_config=config_data.get("notifications", {}),
            data_sources=config_data.get("data_sources", {}),
            strategies=config_data.get("strategies", {}),
            log_level=config_data.get("logging", config_data.get("log", {})).get("level", "INFO"),
            log_file=config_data.get("logging", config_data.get("log", {})).get("file")
        )
        
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'Config':
        """
        从字典创建配置
        
        Args:
            config_dict: 配置字典
            
        Returns:
            配置对象
        """
        return cls(
            lighter_config=config_dict.get("lighter", {}),
            trading_config=config_dict.get("trading", {}),
            risk_config=config_dict.get("risk", {}),
            notifications_config=config_dict.get("notifications", {}),
            data_sources=config_dict.get("data_sources", {}),
            strategies=config_dict.get("strategies", {}),
            log_level=config_dict.get("log", {}).get("level", "INFO"),
            log_file=config_dict.get("log", {}).get("file")
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "lighter": self.lighter_config,
            "trading": self.trading_config,
            "risk_management": self.risk_config,
            "notifications": self.notifications_config,
            "data_sources": self.data_sources,
            "strategies": self.strategies,
            "log": {
                "level": self.log_level,
                "file": self.log_file
            }
        }
        
    def save_to_file(self, config_path: str):
        """保存配置到文件"""
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, allow_unicode=True)
            
    def validate(self) -> bool:
        """验证配置"""
        required_lighter_keys = ["base_url", "api_key_private_key", "account_index", "api_key_index"]
        
        for key in required_lighter_keys:
            if key not in self.lighter_config:
                raise ValueError(f"缺少必需的lighter配置: {key}")
                
        return True
        
    @classmethod
    def create_default(cls) -> 'Config':
        """创建默认配置"""
        return cls(
            lighter_config={
                "base_url": "https://testnet.zklighter.elliot.ai",
                "api_key_private_key": "",
                "account_index": 0,
                "api_key_index": 0
            },
            trading_config={
                "tick_interval": 1.0,  # 秒
                "max_concurrent_strategies": 5
            },
            risk_config={
                "max_position_size": 0.1,
                "max_daily_loss": 0.05,
                "max_drawdown": 0.15,
                "max_leverage": 10.0,
                "max_orders_per_minute": 10,
                "max_open_orders": 20
            },
            notifications_config={
                "enabled": False,
                "email": {
                    "enabled": False
                }
            },
            data_sources={
                "primary": "lighter"
            },
            strategies={},
            log_level="INFO"
        )
