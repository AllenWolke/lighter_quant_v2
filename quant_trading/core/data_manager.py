"""
数据管理器
负责获取和管理市场数据
支持多种数据源
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import lighter
from lighter.api.candlestick_api import CandlestickApi
from lighter.api.order_api import OrderApi
from lighter.api.account_api import AccountApi

from ..utils.config import Config
from ..utils.logger import setup_logger
from ..data_sources import LighterDataSource, TradingViewDataSource


class DataManager:
    """数据管理器"""
    
    def __init__(self, api_client: lighter.ApiClient, config: Config):
        """
        初始化数据管理器
        
        Args:
            api_client: lighter API客户端
            config: 配置对象
        """
        self.api_client = api_client
        self.config = config
        self.logger = setup_logger("DataManager", config.log_level)
        
        # API实例
        self.candlestick_api = CandlestickApi(api_client)
        self.order_api = OrderApi(api_client)
        self.account_api = AccountApi(api_client)
        
        # 数据源
        self.data_sources: Dict[str, Any] = {}
        self.primary_data_source = "lighter"  # 默认主数据源
        
        # 数据缓存
        self.market_data_cache: Dict[int, Dict[str, Any]] = {}
        self.order_book_cache: Dict[int, Dict[str, Any]] = {}
        self.account_cache: Optional[Dict[str, Any]] = None
        
        # 数据更新时间
        self.last_update_time: Dict[str, datetime] = {}
        
        # API 限流控制
        self.api_semaphore = asyncio.Semaphore(3)  # 最多同时3个API请求
        self.last_api_call_time = datetime.now()
        self.min_api_interval = 0.1  # API调用最小间隔（秒）
        
    async def initialize(self):
        """初始化数据管理器"""
        self.logger.info("初始化数据管理器...")
        
        # 初始化数据源
        await self._initialize_data_sources()
        
        # 获取初始市场数据
        await self._load_initial_data()
        
        self.logger.info("数据管理器初始化完成")
        
    async def _initialize_data_sources(self):
        """初始化数据源"""
        try:
            # 初始化Lighter数据源
            from ..data_sources import LighterDataSource, TradingViewDataSource
            
            lighter_config = {
                "api_client": self.api_client
            }
            self.data_sources["lighter"] = LighterDataSource(lighter_config)
            await self.data_sources["lighter"].initialize()
            self.logger.info("Lighter数据源已初始化")
            
            # 初始化TradingView数据源
            tv_config = self.config.data_sources.get("tradingview", {})
            self.logger.info(f"TradingView配置: enabled={tv_config.get('enabled', False)}")
            
            if tv_config.get("enabled", False):
                try:
                    self.data_sources["tradingview"] = TradingViewDataSource(tv_config)
                    await self.data_sources["tradingview"].initialize()
                    self.logger.info("✅ TradingView数据源已成功启用")
                except Exception as e:
                    self.logger.error(f"TradingView数据源初始化失败: {e}")
                    import traceback
                    self.logger.error(traceback.format_exc())
            else:
                self.logger.warning("⚠️ TradingView数据源未启用！检查config.yaml中tradingview.enabled配置")
            
            # 设置主数据源
            self.primary_data_source = self.config.data_sources.get("primary", "lighter")
            self.logger.info(f"主数据源设置为: {self.primary_data_source}")
            self.logger.info(f"可用数据源列表: {list(self.data_sources.keys())}")
            
            # 验证主数据源是否可用
            if self.primary_data_source not in self.data_sources:
                self.logger.error(f"⚠️ 主数据源 '{self.primary_data_source}' 不可用，回退到 'lighter'")
                self.primary_data_source = "lighter"
            
        except Exception as e:
            self.logger.error(f"初始化数据源失败: {e}")
            raise
        
    async def _load_initial_data(self):
        """加载初始数据"""
        try:
            # 获取市场列表
            markets = await self.order_api.order_books()
            self.logger.info(f"发现 {len(markets.order_books)} 个市场")
            
            # 为每个市场初始化数据缓存
            for market in markets.order_books:
                market_id = market.market_id
                self.market_data_cache[market_id] = {
                    "market_info": market,
                    "candlesticks": [],
                    "order_book": None,
                    "trades": []
                }
                
        except Exception as e:
            self.logger.error(f"加载初始数据失败: {e}")
            raise
            
    async def get_latest_data(self, extra_markets: List[int] = None) -> Dict[int, Dict[str, Any]]:
        """
        获取最新市场数据
        
        Args:
            extra_markets: 额外需要更新的市场ID列表（例如用户临时选择的市场）
        
        Returns:
            市场数据字典
        """
        try:
            # 获取需要更新的市场ID
            required_markets = set()
            
            # 1. 从策略配置中获取
            if hasattr(self.config, 'strategies') and self.config.strategies:
                for strategy_name, strategy_config in self.config.strategies.items():
                    if strategy_config.get("enabled", False):
                        if "market_id" in strategy_config:
                            required_markets.add(strategy_config["market_id"])
                        if "market_id_1" in strategy_config:
                            required_markets.add(strategy_config["market_id_1"])
                        if "market_id_2" in strategy_config:
                            required_markets.add(strategy_config["market_id_2"])
            
            # 2. 从配置文件的额外市场列表获取（可选）
            if hasattr(self.config, 'data_sources') and self.config.data_sources:
                extra_markets_config = self.config.data_sources.get("extra_markets", [])
                if extra_markets_config:
                    required_markets.update(extra_markets_config)
                    self.logger.debug(f"从配置添加额外市场: {extra_markets_config}")
            
            # 3. 从参数添加额外市场（例如用户临时选择的市场）
            if extra_markets:
                required_markets.update(extra_markets)
                self.logger.debug(f"从参数添加额外市场: {extra_markets}")
            
            # 4. 如果没有配置的市场，使用默认市场列表
            if not required_markets:
                required_markets = {0, 1, 2}  # 默认更新ETH, BTC, SOL
                if not hasattr(self, '_warned_no_markets'):
                    self.logger.warning(f"未找到配置的市场，使用默认市场: {sorted(required_markets)}")
                    self._warned_no_markets = True
            
            self.logger.debug(f"需要更新的市场: {sorted(required_markets)}")
            
            # 只更新需要的市场
            for market_id in required_markets:
                if market_id not in self.market_data_cache:
                    # 初始化市场缓存
                    self.market_data_cache[market_id] = {
                        "market_info": None,
                        "candlesticks": [],
                        "order_book": None,
                        "trades": [],
                        "last_price": 0
                    }
                
                await self._update_market_data(market_id)
                
            return self.market_data_cache
            
        except Exception as e:
            self.logger.error(f"获取最新数据失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return self.market_data_cache
            
    async def get_data_from_source(self, source_name: str, symbol: str, 
                                  data_type: str = "candlesticks", **kwargs) -> Any:
        """
        从指定数据源获取数据
        
        Args:
            source_name: 数据源名称
            symbol: 交易对符号
            data_type: 数据类型 (candlesticks, current_price, order_book, trades)
            **kwargs: 其他参数
            
        Returns:
            数据
        """
        try:
            if source_name not in self.data_sources:
                self.logger.error(f"数据源 {source_name} 不存在")
                return None
                
            data_source = self.data_sources[source_name]
            
            if data_type == "candlesticks":
                return await data_source.get_candlesticks(
                    symbol, 
                    kwargs.get("timeframe", "1m"),
                    kwargs.get("limit", 100)
                )
            elif data_type == "current_price":
                return await data_source.get_current_price(symbol)
            elif data_type == "order_book":
                return await data_source.get_order_book(symbol)
            elif data_type == "trades":
                return await data_source.get_trades(symbol, kwargs.get("limit", 50))
            else:
                self.logger.error(f"不支持的数据类型: {data_type}")
                return None
                
        except Exception as e:
            self.logger.error(f"从数据源 {source_name} 获取数据失败: {e}")
            return None
            
    async def get_tradingview_data(self, symbol: str, data_type: str = "candlesticks", **kwargs) -> Any:
        """
        从TradingView获取数据
        
        Args:
            symbol: 交易对符号
            data_type: 数据类型
            **kwargs: 其他参数
            
        Returns:
            数据
        """
        return await self.get_data_from_source("tradingview", symbol, data_type, **kwargs)
        
    def get_available_data_sources(self) -> List[str]:
        """获取可用的数据源列表"""
        return list(self.data_sources.keys())
        
    def set_primary_data_source(self, source_name: str):
        """设置主数据源"""
        if source_name in self.data_sources:
            self.primary_data_source = source_name
            self.logger.info(f"主数据源已设置为: {source_name}")
        else:
            self.logger.error(f"数据源 {source_name} 不存在")
            
    async def _update_market_data(self, market_id: int):
        """更新指定市场的数据"""
        try:
            current_time = datetime.now()
            
            # 更新K线数据
            if self._should_update_data("candlesticks", market_id):
                await self._update_candlesticks(market_id)
                self.last_update_time[f"candlesticks_{market_id}"] = current_time
                
            # 更新订单簿数据
            if self._should_update_data("order_book", market_id):
                await self._update_order_book(market_id)
                self.last_update_time[f"order_book_{market_id}"] = current_time
                
            # 更新交易数据
            if self._should_update_data("trades", market_id):
                await self._update_trades(market_id)
                self.last_update_time[f"trades_{market_id}"] = current_time
                
        except Exception as e:
            self.logger.error(f"更新市场 {market_id} 数据失败: {e}")
            
    def _get_symbol_for_market(self, market_id: int) -> str:
        """
        获取市场对应的交易对符号
        
        Args:
            market_id: 市场ID
            
        Returns:
            交易对符号（如ETHUSDT）
        """
        # 首先尝试从config的market_id_mapping获取
        if hasattr(self.config, 'data_sources') and self.config.data_sources:
            market_mapping = self.config.data_sources.get('market_id_mapping', {})
            if market_id in market_mapping:
                base_symbol = market_mapping[market_id]
                # 添加USDT后缀
                symbol = f"{base_symbol}USDT"
                self.logger.debug(f"从配置映射: 市场 {market_id} → {symbol}")
                return symbol
        
        # 从市场数据缓存中获取市场信息
        if market_id in self.market_data_cache:
            market_info = self.market_data_cache[market_id].get("market_info")
            if market_info and hasattr(market_info, 'symbol'):
                base_symbol = market_info.symbol
                # 确保添加USDT后缀
                if not base_symbol.endswith('USDT'):
                    symbol = f"{base_symbol}USDT"
                else:
                    symbol = base_symbol
                self.logger.debug(f"从缓存获取: 市场 {market_id} → {symbol}")
                return symbol
        
        # 使用完整的默认映射（基于Lighter实际市场ID，共92个市场）
        default_symbols = {
            # 主流币种 (Market ID 0-10)
            0: "ETHUSDT",       # ETH 以太坊
            1: "BTCUSDT",       # BTC 比特币
            2: "SOLUSDT",       # SOL Solana
            3: "DOGEUSDT",      # DOGE 狗狗币
            4: "1000PEPEUSDT",  # PEPE (注意：Binance是1000倍)
            5: "WIFUSDT",       # WIF Dogwifhat
            6: "WLDUSDT",       # WLD Worldcoin
            7: "XRPUSDT",       # XRP Ripple
            8: "LINKUSDT",      # LINK Chainlink
            9: "AVAXUSDT",      # AVAX Avalanche
            10: "NEARUSDT",     # NEAR NEAR Protocol
            # Layer 1/2 (Market ID 11-20)
            11: "DOTUSDT",      # DOT Polkadot
            12: "TONUSDT",      # TON Toncoin
            13: "TAOUSDT",      # TAO Bittensor
            14: "MATICUSDT",    # POL (Binance仍用MATIC)
            15: "TRUMPUSDT",    # TRUMP Trump Coin
            16: "SUIUSDT",      # SUI Sui
            17: "1000SHIBUSDT", # SHIB (1000倍)
            18: "1000BONKUSDT", # BONK (1000倍)
            19: "1000FLOKIUSDT", # FLOKI (1000倍)
            20: "BERAUSDT",     # BERA Berachain
            # Meme/AI (Market ID 21-30)
            21: "FARTCOINUSDT", # FARTCOIN
            22: "AI16ZUSDT",    # AI16Z
            23: "POPCATUSDT",   # POPCAT
            24: "HYPEUSDT",     # HYPE
            25: "BNBUSDT",      # BNB Binance Coin
            26: "JUPUSDT",      # JUP Jupiter
            27: "AAVEUSDT",     # AAVE Aave
            28: "MKRUSDT",      # MKR Maker
            29: "ENAUSDT",      # ENA Ethena
            30: "UNIUSDT",      # UNI Uniswap
            # DeFi/其他 (Market ID 31-50)
            31: "APTUSDT",      # APT Aptos
            32: "SEIUSDT",      # SEI Sei
            33: "KAITOUSDT",    # KAITO
            34: "IPUSDT",       # IP
            35: "LTCUSDT",      # LTC Litecoin
            36: "CRVUSDT",      # CRV Curve
            37: "PENDLEUSDT",   # PENDLE Pendle
            38: "ONDOUSDT",     # ONDO Ondo
            39: "ADAUSDT",      # ADA Cardano
            40: "SUSDT",        # S
            41: "VIRTUALUSDT",  # VIRTUAL
            42: "SPXUSDT",      # SPX
            43: "TRXUSDT",      # TRX TRON
            44: "SYRUPUSDT",    # SYRUP
            45: "PUMPUSDT",     # PUMP
            46: "LDOUSDT",      # LDO Lido
            47: "PENGUUSDT",    # PENGU
            48: "PAXGUSDT",     # PAXG PAX Gold
            49: "EIGENUSDT",    # EIGEN
            50: "ARBUSDT",      # ARB Arbitrum
            # 新币种 (Market ID 51-70)
            51: "RESOLVUSDT",   # RESOLV
            52: "GRASSUSDT",    # GRASS
            53: "ZORAUSDT",     # ZORA
            54: "LAUNCHCOINUSDT", # LAUNCHCOIN
            55: "OPUSDT",       # OP Optimism
            56: "ZKUSDT",       # ZK
            57: "PROVEUSDT",    # PROVE
            58: "BCHUSDT",      # BCH Bitcoin Cash
            59: "HBARUSDT",     # HBAR Hedera
            60: "ZROUSDT",      # ZRO LayerZero
            61: "GMXUSDT",      # GMX
            62: "DYDXUSDT",     # DYDX
            63: "MNTUSDT",      # MNT Mantle
            64: "ETHFIUSDT",    # ETHFI
            65: "AEROUSDT",     # AERO
            66: "USELESSUSDT",  # USELESS
            67: "TIAUSDT",      # TIA Celestia
            68: "MORPHOUSDT",   # MORPHO
            69: "VVVUSDT",      # VVV
            70: "YZYUSDT",      # YZY
            # 最新币种 (Market ID 71-91)
            71: "XPLUSDT",      # XPL
            72: "WLFIUSDT",     # WLFI
            73: "CROUSDT",      # CRO Cronos
            74: "NMRUSDT",      # NMR Numerai
            75: "DOLOUSDT",     # DOLO
            76: "LINEAUSDT",    # LINEA
            77: "XMRUSDT",      # XMR Monero
            78: "PYTHUSDT",     # PYTH
            79: "SKYUSDT",      # SKY
            80: "MYXUSDT",      # MYX
            81: "1000TOSHIUSDT", # TOSHI (1000倍)
            82: "AVNTUSDT",     # AVNT
            83: "ASTERUSDT",    # ASTER
            84: "OGUSDT",       # 0G (Binance可能用OG)
            85: "STBLUSDT",     # STBL
            86: "APEXUSDT",     # APEX
            87: "FFUSDT",       # FF
            88: "2ZUSDT",       # 2Z
            89: "EDENUSDT",     # EDEN
            90: "ZECUSDT",      # ZEC Zcash
            91: "MONUSDT",      # MON
        }
        
        symbol = default_symbols.get(market_id, "ETHUSDT")
        self.logger.debug(f"使用默认映射: 市场 {market_id} → {symbol}")
        return symbol
    
    def _should_update_data(self, data_type: str, market_id: int) -> bool:
        """检查是否需要更新数据"""
        key = f"{data_type}_{market_id}"
        last_update = self.last_update_time.get(key)
        
        if last_update is None:
            return True
            
        # 根据数据类型设置更新间隔
        intervals = {
            "candlesticks": timedelta(seconds=60),  # 1分钟
            "order_book": timedelta(seconds=5),     # 5秒
            "trades": timedelta(seconds=10)         # 10秒
        }
        
        interval = intervals.get(data_type, timedelta(seconds=30))
        return datetime.now() - last_update > interval
        
    async def _rate_limit(self):
        """API 限流控制"""
        async with self.api_semaphore:
            now = datetime.now()
            time_since_last_call = (now - self.last_api_call_time).total_seconds()
            if time_since_last_call < self.min_api_interval:
                await asyncio.sleep(self.min_api_interval - time_since_last_call)
            self.last_api_call_time = datetime.now()
    
    async def _update_candlesticks(self, market_id: int):
        """更新K线数据"""
        try:
            await self._rate_limit()  # 限流
            
            self.logger.info(f"[DataManager] 开始更新市场 {market_id} 的K线数据")
            self.logger.info(f"[DataManager] 当前主数据源: {self.primary_data_source}")
            self.logger.info(f"[DataManager] 可用数据源: {list(self.data_sources.keys())}")
            
            # 使用主数据源获取K线数据
            if self.primary_data_source != "lighter" and self.primary_data_source in self.data_sources:
                # 使用TradingView或其他数据源
                try:
                    data_source = self.data_sources[self.primary_data_source]
                    
                    # 获取市场符号（简化处理：使用market_id作为符号）
                    # 实际应该从市场信息中获取正确的符号
                    symbol = self._get_symbol_for_market(market_id)
                    self.logger.info(f"[DataManager] 市场 {market_id} 映射到符号: {symbol}")
                    
                    candlesticks_data = await data_source.get_candlesticks(
                        symbol=symbol,
                        timeframe="1m",
                        limit=100  # 获取100条K线数据
                    )
                    
                    if candlesticks_data:
                        self.market_data_cache[market_id]["candlesticks"] = candlesticks_data
                        # 更新last_price为最新K线的收盘价
                        if len(candlesticks_data) > 0:
                            self.market_data_cache[market_id]["last_price"] = candlesticks_data[-1].get("close", 0)
                            self.logger.debug(f"[DataManager] 市场 {market_id} last_price 更新为: {self.market_data_cache[market_id]['last_price']}")
                        self.logger.info(f"[DataManager] 从 {self.primary_data_source} 获取到 {len(candlesticks_data)} 条K线数据 (市场 {market_id})")
                        return
                    else:
                        self.logger.warning(f"[DataManager] {self.primary_data_source} 返回空数据")
                except Exception as e:
                    self.logger.warning(f"从 {self.primary_data_source} 获取K线数据失败 (市场 {market_id}): {e}，回退到Lighter")
                    import traceback
                    self.logger.warning(traceback.format_exc())
            
            # 回退到Lighter数据源
            end_time = int(datetime.now().timestamp())
            start_time = end_time - 3600  # 获取最近1小时的数据
            
            candlesticks = await self.candlestick_api.candlesticks(
                market_id=market_id,
                resolution="1m",
                start_timestamp=start_time,
                end_timestamp=end_time,
                count_back=60
            )
            
            if candlesticks and candlesticks.candlesticks:
                candlesticks_list = [
                    {
                        "timestamp": c.timestamp,
                        "open": float(c.open),
                        "high": float(c.high),
                        "low": float(c.low),
                        "close": float(c.close),
                        "volume": float(c.volume0)  # 使用 volume0
                    } for c in candlesticks.candlesticks
                ]
                self.market_data_cache[market_id]["candlesticks"] = candlesticks_list
                # 更新last_price为最新K线的收盘价
                if len(candlesticks_list) > 0:
                    self.market_data_cache[market_id]["last_price"] = candlesticks_list[-1]["close"]
                    self.logger.debug(f"[DataManager] 市场 {market_id} last_price 更新为: {self.market_data_cache[market_id]['last_price']}")
                
        except Exception as e:
            self.logger.error(f"更新K线数据失败 (市场 {market_id}): {e}")
            
    async def _update_order_book(self, market_id: int):
        """更新订单簿数据"""
        try:
            await self._rate_limit()  # 限流
            
            # 使用 order_book_orders 而不是 order_book_details
            order_book = await self.order_api.order_book_orders(market_id=market_id, limit=20)
            
            if order_book:
                # OrderBookOrders 直接有 bids 和 asks 属性
                bids = [(float(bid.price), float(bid.remaining_base_amount)) for bid in order_book.bids]
                asks = [(float(ask.price), float(ask.remaining_base_amount)) for ask in order_book.asks]
                
                self.market_data_cache[market_id]["order_book"] = {
                    "bids": bids,
                    "asks": asks,
                    "timestamp": datetime.now().timestamp()
                }
                
                # 从订单簿更新last_price（使用中间价）
                if bids and asks:
                    best_bid = bids[0][0] if len(bids) > 0 else 0
                    best_ask = asks[0][0] if len(asks) > 0 else 0
                    if best_bid > 0 and best_ask > 0:
                        mid_price = (best_bid + best_ask) / 2
                        # 只在没有last_price时更新（K线数据优先）
                        if self.market_data_cache[market_id].get("last_price", 0) == 0:
                            self.market_data_cache[market_id]["last_price"] = mid_price
                            self.logger.debug(f"[DataManager] 市场 {market_id} 从订单簿更新 last_price: {mid_price}")
                
        except Exception as e:
            self.logger.error(f"更新订单簿失败 (市场 {market_id}): {e}")
            
    async def _update_trades(self, market_id: int):
        """更新交易数据"""
        try:
            await self._rate_limit()  # 限流
            
            trades = await self.order_api.recent_trades(market_id=market_id, limit=20)  # 减少limit以避免429
            
            if trades and trades.trades:
                trades_list = [
                    {
                        "timestamp": t.timestamp,
                        "price": float(t.price),
                        "amount": float(t.size),  # 使用 size 而不是 amount
                        "side": "buy" if t.is_maker_ask else "sell"  # 根据 is_maker_ask 判断方向
                    } for t in trades.trades
                ]
                self.market_data_cache[market_id]["trades"] = trades_list
                
                # 从最新交易更新last_price
                if len(trades_list) > 0:
                    latest_trade_price = trades_list[-1]["price"]
                    # 只在没有last_price时更新（K线和订单簿优先）
                    if self.market_data_cache[market_id].get("last_price", 0) == 0:
                        self.market_data_cache[market_id]["last_price"] = latest_trade_price
                        self.logger.debug(f"[DataManager] 市场 {market_id} 从最新交易更新 last_price: {latest_trade_price}")
                
        except Exception as e:
            self.logger.error(f"更新交易数据失败 (市场 {market_id}): {e}")
            
    async def get_account_data(self) -> Optional[Dict[str, Any]]:
        """获取账户数据"""
        try:
            account = await self.account_api.account(
                by="index", 
                value=str(self.config.lighter_config["account_index"])
            )
            
            if account:
                self.account_cache = {
                    "account_index": account.account_index,
                    "l1_address": account.l1_address,
                    "positions": account.positions,
                    "balance": account.balance,
                    "timestamp": datetime.now().timestamp()
                }
                
            return self.account_cache
            
        except Exception as e:
            self.logger.error(f"获取账户数据失败: {e}")
            return self.account_cache
            
    def get_market_data(self, market_id: int) -> Optional[Dict[str, Any]]:
        """获取指定市场的数据"""
        return self.market_data_cache.get(market_id)
        
    def get_candlesticks(self, market_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """获取K线数据"""
        market_data = self.get_market_data(market_id)
        if market_data and "candlesticks" in market_data:
            return market_data["candlesticks"][-limit:]
        return []
        
    def get_order_book(self, market_id: int) -> Optional[Dict[str, Any]]:
        """获取订单簿数据"""
        market_data = self.get_market_data(market_id)
        if market_data and "order_book" in market_data:
            return market_data["order_book"]
        return None
        
    def get_trades(self, market_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """获取交易数据"""
        market_data = self.get_market_data(market_id)
        if market_data and "trades" in market_data:
            return market_data["trades"][-limit:]
        return []
