#!/usr/bin/env python3
"""
Lighter量化交易程序启动脚本
提供交互式配置和启动功能
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from quant_trading import TradingEngine, Config
from quant_trading.strategies import MeanReversionStrategy, MomentumStrategy, ArbitrageStrategy, UTBotStrategy
from datetime import datetime, timedelta
import numpy as np


def print_banner():
    """打印程序横幅"""
    print("=" * 60)
    print("🚀 Lighter量化交易程序")
    print("=" * 60)
    print()


def get_user_config():
    """获取用户配置"""
    print("请配置Lighter交易所参数:")
    print()
    
    # 选择网络
    print("1. 选择网络:")
    print("   1) 测试网 (testnet.zklighter.elliot.ai)")
    print("   2) 主网 (mainnet.zklighter.elliot.ai)")
    
    while True:
        choice = input("请选择 (1-2): ").strip()
        if choice == "1":
            base_url = "https://testnet.zklighter.elliot.ai"
            break
        elif choice == "2":
            base_url = "https://mainnet.zklighter.elliot.ai"
            break
        else:
            print("无效选择，请重新输入")
    
    print()
    
    # 获取API参数
    api_key_private_key = input("请输入API密钥私钥: ").strip()
    if not api_key_private_key:
        print("❌ API密钥私钥不能为空")
        return None
        
    try:
        account_index = int(input("请输入账户索引: ").strip())
    except ValueError:
        print("❌ 账户索引必须是数字")
        return None
        
    try:
        api_key_index = int(input("请输入API密钥索引: ").strip())
    except ValueError:
        print("❌ API密钥索引必须是数字")
        return None
    
    print()
    
    # 选择策略
    print("2. 选择交易策略:")
    print("   1) 均值回归策略")
    print("   2) 动量策略")
    print("   3) 套利策略")
    print("   4) UT Bot策略")
    print("   5) 所有策略")
    
    while True:
        choice = input("请选择 (1-5): ").strip()
        if choice in ["1", "2", "3", "4", "5"]:
            strategy_choice = choice
            break
        else:
            print("无效选择，请重新输入")
    
    print()
    
    # 选择市场
    try:
        market_id = int(input("请输入市场ID (默认0): ").strip() or "0")
    except ValueError:
        market_id = 0
    
    print()
    
    # 风险确认
    print("3. 风险提示:")
    print("   ⚠️  量化交易存在风险，可能导致资金损失")
    print("   ⚠️  请确保您了解相关风险并谨慎操作")
    print("   ⚠️  建议先在测试网环境测试")
    print()
    
    confirm = input("是否确认继续? (y/N): ").strip().lower()
    if confirm != 'y':
        print("已取消启动")
        return None
    
    return {
        "base_url": base_url,
        "api_key_private_key": api_key_private_key,
        "account_index": account_index,
        "api_key_index": api_key_index,
        "strategy_choice": strategy_choice,
        "market_id": market_id
    }


def create_config(user_config):
    """创建配置对象"""
    # 从 config.yaml 读取基础配置（包含数据源和策略配置）
    import os
    if os.path.exists('config.yaml'):
        config = Config.from_file('config.yaml')
        print("✅ 已从 config.yaml 加载配置（包含TradingView数据源）")
    else:
        config = Config.create_default()
        print("⚠️  config.yaml 不存在，使用默认配置")
    
    # 更新Lighter配置（使用用户输入的值覆盖）
    config.lighter_config.update({
        "base_url": user_config["base_url"],
        "api_key_private_key": user_config["api_key_private_key"],
        "account_index": user_config["account_index"],
        "api_key_index": user_config["api_key_index"]
    })
    
    # 确保风险参数合理（如果config.yaml中没有，则使用这些值）
    if not config.risk_config.get("max_position_size"):
        config.risk_config.update({
            "max_position_size": 0.05,  # 最大仓位5%
            "max_daily_loss": 0.02,     # 最大日亏损2%
            "max_drawdown": 0.10,       # 最大回撤10%
            "max_orders_per_minute": 5, # 每分钟最大订单数
            "max_open_orders": 10,      # 最大开仓订单数
        })
    
    return config


async def test_lighter_connection_on_startup(config):
    """启动时测试 Lighter 连接"""
    print()
    print("=" * 60)
    print("🔍 测试 Lighter 交易所连接...")
    print("=" * 60)
    
    try:
        import lighter
        from lighter.api.order_api import OrderApi
        
        # 创建临时客户端测试
        api_client = lighter.ApiClient(
            configuration=lighter.Configuration(host=config.lighter_config["base_url"])
        )
        
        signer_client = lighter.SignerClient(
            url=config.lighter_config["base_url"],
            private_key=config.lighter_config["api_key_private_key"],
            account_index=config.lighter_config["account_index"],
            api_key_index=config.lighter_config["api_key_index"]
        )
        
        # 测试 API 连接
        order_api = OrderApi(api_client)
        markets = await order_api.order_books()
        
        if markets and hasattr(markets, 'order_books'):
            print(f"✅ API 连接成功 - 发现 {len(markets.order_books)} 个市场")
        else:
            print(f"⚠️  API 连接成功，但市场数据格式异常")
        
        # 测试 Signer 认证
        err = signer_client.check_client()
        if err is not None:
            print(f"❌ Signer 认证失败: {err}")
            print(f"   请检查 API 私钥配置")
            await api_client.close()
            await signer_client.close()
            return False
        else:
            print(f"✅ Signer 认证成功 - 可以提交订单")
        
        # 清理测试客户端
        await api_client.close()
        await signer_client.close()
        
        print("=" * 60)
        print("✅ 连接测试通过！开始启动交易系统...")
        print("=" * 60)
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        print(f"   请检查:")
        print(f"   1. 网络连接是否正常")
        print(f"   2. config.yaml 中的 base_url 是否正确")
        print(f"   3. API 私钥是否正确")
        print()
        
        # 询问是否继续
        confirm = input("连接测试失败，是否仍要继续启动？(y/N): ").strip().lower()
        return confirm == 'y'


async def monitor_connection_and_positions(engine, config):
    """每两分钟监控连接和持仓"""
    import lighter
    from lighter.api.order_api import OrderApi
    from lighter.api.account_api import AccountApi
    
    check_interval = 120  # 2分钟
    
    while engine.is_running:
        try:
            await asyncio.sleep(check_interval)
            
            if not engine.is_running:
                break
            
            print("\n" + "=" * 60)
            print(f"📊 定期监控检查 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 60)
            
            # ======= 需求① 检查连接状态 =======
            print("\n🔗 检查1: Lighter 交易所连接状态")
            print("-" * 60)
            try:
                # 测试 API 连接
                order_api = OrderApi(engine.api_client)
                markets = await order_api.order_books()
                
                if markets and hasattr(markets, 'order_books'):
                    market_count = len(markets.order_books)
                    print(f"✅ 连接正常 - API 可访问，发现 {market_count} 个市场")
                else:
                    print(f"⚠️  连接异常 - 市场数据格式不正确")
                
                # 测试 Signer 认证
                err = engine.signer_client.check_client()
                if err is not None:
                    print(f"❌ 认证失败: {err}")
                else:
                    print(f"✅ 认证正常 - 可以提交交易订单")
                    
            except Exception as e:
                print(f"❌ 连接检查失败: {e}")
                print(f"   建议: 检查网络连接或重启系统")
            
            # ======= 需求② 检查持仓和交易信号 =======
            print("\n💰 检查2: 账户持仓与交易信号分析")
            print("-" * 60)
            try:
                # 获取账户索引
                account_index = config.lighter_config["account_index"]
                
                # 从 API 获取真实账户信息
                from lighter.api.account_api import AccountApi
                account_api = AccountApi(engine.api_client)
                
                # 获取账户信息
                account_info = None
                blockchain_id = None
                
                try:
                    account_info = await account_api.account(by="index", value=str(account_index))
                    
                    # 处理返回的账户信息
                    # API 可能返回 DetailedAccounts (包含多个账户) 或单个 Account
                    actual_account = None
                    
                    if account_info:
                        # 检查是否是 DetailedAccounts (有 accounts 字段)
                        if hasattr(account_info, 'accounts') and account_info.accounts:
                            # 从 accounts 列表中找到匹配的账户
                            for acc in account_info.accounts:
                                if hasattr(acc, 'index') and acc.index == account_index:
                                    actual_account = acc
                                    break
                            
                            # 如果没找到匹配的，使用第一个账户
                            if not actual_account and len(account_info.accounts) > 0:
                                actual_account = account_info.accounts[0]
                        
                        # 检查是否直接是 Account 对象 (有 l1_address 字段)
                        elif hasattr(account_info, 'l1_address'):
                            actual_account = account_info
                    
                    # 提取账户信息
                    if actual_account and hasattr(actual_account, 'l1_address'):
                        blockchain_id = actual_account.l1_address
                        
                        # 打印详细的账户信息
                        print(f"\n📋 账户信息:")
                        print(f"  账户索引: {account_index}")
                        print(f"  L1地址 (完整): {blockchain_id}")
                        print(f"  L1地址 (简写): {blockchain_id[:10]}...{blockchain_id[-8:]}")
                        
                        # 打印其他可用的账户信息
                        if hasattr(actual_account, 'account_type'):
                            account_type_map = {0: "标准账户", 1: "子账户"}
                            acc_type = account_type_map.get(actual_account.account_type, f"未知({actual_account.account_type})")
                            print(f"  账户类型: {acc_type}")
                        
                        if hasattr(actual_account, 'status'):
                            status_map = {0: "正常", 1: "冻结", 2: "限制"}
                            acc_status = status_map.get(actual_account.status, f"未知({actual_account.status})")
                            print(f"  账户状态: {acc_status}")
                        
                        if hasattr(actual_account, 'total_order_count'):
                            print(f"  历史订单总数: {actual_account.total_order_count}")
                        
                        if hasattr(actual_account, 'pending_order_count'):
                            print(f"  待处理订单数: {actual_account.pending_order_count}")
                    else:
                        print(f"\n⚠️  无法获取账户L1地址")
                        if account_info:
                            # 提供调试信息
                            if hasattr(account_info, 'accounts'):
                                print(f"  返回了 DetailedAccounts，包含 {len(account_info.accounts)} 个账户")
                                if len(account_info.accounts) > 0:
                                    print(f"  第一个账户的字段: {dir(account_info.accounts[0])}")
                            else:
                                print(f"  账户信息已获取，但缺少 l1_address 字段")
                                print(f"  返回对象类型: {type(account_info).__name__}")
                                print(f"  可用字段: {[attr for attr in dir(account_info) if not attr.startswith('_')]}")
                except Exception as e:
                    print(f"\n⚠️  获取账户信息失败: {e}")
                    import traceback
                    print(f"  错误详情: {traceback.format_exc()}")
                
                # 获取账户余额（从 actual_account 对象直接提取）
                total_balance = 0
                available_balance = 0
                total_asset_value = 0
                
                if actual_account:
                    try:
                        # 从 DetailedAccount 对象提取余额信息
                        # 注意：API返回的已经是USDT格式，不是wei格式，直接转换为float即可
                        if hasattr(actual_account, 'collateral') and actual_account.collateral:
                            try:
                                # collateral 已经是USDT格式的字符串，直接转float
                                total_balance = float(actual_account.collateral)
                            except (ValueError, TypeError):
                                total_balance = 0
                        
                        if hasattr(actual_account, 'available_balance') and actual_account.available_balance:
                            try:
                                # available_balance 已经是USDT格式
                                available_balance = float(actual_account.available_balance)
                            except (ValueError, TypeError):
                                available_balance = 0
                        
                        if hasattr(actual_account, 'total_asset_value') and actual_account.total_asset_value:
                            try:
                                # total_asset_value 已经是USDT格式
                                total_asset_value = float(actual_account.total_asset_value)
                            except (ValueError, TypeError):
                                total_asset_value = 0
                        
                        print(f"\n💵 账户余额:")
                        print(f"  抵押品余额: {total_balance:.4f}")
                        print(f"  可用余额: {available_balance:.4f}")
                        if total_asset_value > 0:
                            print(f"  总资产价值: {total_asset_value:.4f}")
                    except Exception as e:
                        print(f"\n💵 账户余额: 解析失败 ({e})")
                        import traceback
                        traceback.print_exc()
                else:
                    print(f"\n💵 账户余额: 需要账户信息")
                
                # 获取真实持仓（从 API）
                api_positions = []
                if actual_account and hasattr(actual_account, 'positions'):
                    api_positions = actual_account.positions
                
                # 也获取本地缓存的持仓
                local_positions = engine.position_manager.get_all_positions()
                
                # 显示 API 持仓信息
                total_position_value = 0
                
                if api_positions and len(api_positions) > 0:
                    print(f"\n📈 账户实际持仓 (来自API): {len(api_positions)} 个")
                    
                    for idx, pos in enumerate(api_positions):
                        try:
                            # 从 AccountPosition 对象提取信息
                            # 注意：API返回的已经是实际数值格式，不是wei格式，直接转float即可
                            market_id = pos.market_id if hasattr(pos, 'market_id') else "未知"
                            
                            # position 字段已经是实际数量（如 0.005），直接转float
                            position_size = float(pos.position) if hasattr(pos, 'position') and pos.position else 0
                            
                            # 其他字段也已经是USDT/实际格式
                            position_value = float(pos.position_value) if hasattr(pos, 'position_value') and pos.position_value else 0
                            unrealized_pnl = float(pos.unrealized_pnl) if hasattr(pos, 'unrealized_pnl') and pos.unrealized_pnl else 0
                            realized_pnl = float(pos.realized_pnl) if hasattr(pos, 'realized_pnl') and pos.realized_pnl else 0
                            avg_entry_price = float(pos.avg_entry_price) if hasattr(pos, 'avg_entry_price') and pos.avg_entry_price else 0
                            position_sign = pos.sign if hasattr(pos, 'sign') else 0
                            
                            # 获取交易对符号
                            symbol = pos.symbol if hasattr(pos, 'symbol') else f"市场{market_id}"
                            
                            total_position_value += position_value
                            
                            side_text = "做多" if position_sign > 0 else ("做空" if position_sign < 0 else "平仓")
                            
                            print(f"\n  市场 {market_id} ({symbol}): {side_text}")
                            print(f"    仓位大小: {position_size:.4f}")
                            print(f"    平均入场价: {avg_entry_price:.2f}")
                            print(f"    持仓价值: {position_value:.2f}")
                            print(f"    未实现盈亏: {unrealized_pnl:+.2f}")
                            print(f"    已实现盈亏: {realized_pnl:+.2f}")
                        except Exception as e:
                            print(f"\n  [ERROR] 解析持仓信息失败: {e}")
                            import traceback
                            traceback.print_exc()
                    
                    print(f"  总持仓价值: {total_position_value:.2f}")
                    
                    if total_balance > 0:
                        position_ratio = (total_position_value / total_balance) * 100
                        print(f"  持仓占比: {position_ratio:.2f}%")
                else:
                    print(f"\n📊 账户实际持仓: 无")
                
                # 显示本地缓存持仓（对比）
                if local_positions and len(local_positions) > 0:
                    print(f"\n📋 本地缓存持仓: {len(local_positions)} 个")
                    for market_id, position in local_positions.items():
                        print(f"  市场 {market_id}: {position.side.value.upper()} ({position.size:.4f})")
                elif not api_positions or len(api_positions) == 0:
                    print(f"\n💡 提示: 当前无持仓")
                
                # 分析交易信号条件
                print(f"\n🎯 交易信号分析:")
                
                # 获取最新市场数据
                try:
                    market_data = await engine.data_manager.get_latest_data()
                    
                    # 分析每个策略的信号条件
                    for strategy in engine.strategies:
                        if not strategy.is_active():
                            continue
                        
                        strategy_name = strategy.name
                        print(f"\n  策略: {strategy_name}")
                        
                        # 获取策略参数
                        params = strategy.get_strategy_params() if hasattr(strategy, 'get_strategy_params') else {}
                        strategy_market_id = params.get('market_id', 0)
                        
                        # 检查是否有该市场的数据
                        if strategy_market_id not in market_data:
                            print(f"    ❌ 不满足交易信号")
                            print(f"       原因: 市场 {strategy_market_id} 数据不可用")
                            continue
                        
                        market_info = market_data[strategy_market_id]
                        candlesticks = market_info.get("candlesticks", [])
                        
                        # 检查数据是否足够
                        required_data = params.get('lookback_period') or params.get('long_period') or params.get('atr_period', 20)
                        if len(candlesticks) < required_data:
                            print(f"    ❌ 不满足交易信号")
                            print(f"       原因: K线数据不足 ({len(candlesticks)}/{required_data})")
                            print(f"       建议: 等待数据积累")
                            continue
                        
                        # 获取当前价格
                        if candlesticks:
                            current_price = candlesticks[-1].get('close', 0)
                            print(f"    当前价格: {current_price:.2f}")
                        
                        # 检查是否在信号冷却期
                        if hasattr(strategy, 'last_signal_time') and strategy.last_signal_time:
                            if hasattr(strategy, 'signal_cooldown'):
                                cooldown = strategy.signal_cooldown
                                if isinstance(cooldown, timedelta):
                                    time_since_signal = datetime.now() - strategy.last_signal_time
                                    if time_since_signal < cooldown:
                                        remaining = (cooldown - time_since_signal).total_seconds() / 60
                                        print(f"    ⏳ 不满足交易信号")
                                        print(f"       原因: 在信号冷却期 (还需等待 {remaining:.1f} 分钟)")
                                        continue
                                else:
                                    # signal_cooldown 是秒数
                                    time_since_signal = datetime.now().timestamp() - strategy.last_signal_time
                                    if time_since_signal < cooldown:
                                        remaining = (cooldown - time_since_signal) / 60
                                        print(f"    ⏳ 不满足交易信号")
                                        print(f"       原因: 在信号冷却期 (还需等待 {remaining:.1f} 分钟)")
                                        continue
                        
                        # 检查是否已有仓位
                        has_position = strategy_market_id in local_positions
                        if has_position:
                            print(f"    📊 已有仓位")
                            print(f"       等待平仓信号")
                        else:
                            print(f"    📊 无仓位")
                            print(f"       等待开仓信号")
                        
                        # 策略特定的信号分析
                        if strategy_name == "MeanReversion":
                            # 均值回归策略
                            import numpy as np
                            lookback = params.get('lookback_period', 20)
                            threshold = params.get('threshold', 2.0)
                            
                            prices = [c['close'] for c in candlesticks[-lookback:]]
                            mean_price = np.mean(prices)
                            std_price = np.std(prices)
                            
                            if std_price > 0:
                                z_score = (current_price - mean_price) / std_price
                                print(f"    Z分数: {z_score:.2f} (阈值: ±{threshold})")
                                
                                if abs(z_score) >= threshold:
                                    signal_type = "做空" if z_score > 0 else "做多"
                                    print(f"    ✅ 满足交易信号 - {signal_type}")
                                    print(f"       原因: |Z分数| ({abs(z_score):.2f}) >= 阈值 ({threshold})")
                                else:
                                    print(f"    ❌ 不满足交易信号")
                                    print(f"       原因: |Z分数| ({abs(z_score):.2f}) < 阈值 ({threshold})")
                                    print(f"       说明: 价格偏离均值不够大")
                        
                        elif strategy_name == "Momentum":
                            # 动量策略
                            import numpy as np
                            short_period = params.get('short_period', 5)
                            long_period = params.get('long_period', 20)
                            threshold = params.get('momentum_threshold', 0.02)
                            
                            prices = [c['close'] for c in candlesticks[-long_period:]]
                            short_ma = np.mean(prices[-short_period:])
                            long_ma = np.mean(prices)
                            
                            if long_ma > 0:
                                momentum = (short_ma - long_ma) / long_ma
                                print(f"    动量: {momentum:.4f} (阈值: ±{threshold})")
                                
                                if abs(momentum) >= threshold:
                                    signal_type = "做多" if momentum > 0 else "做空"
                                    print(f"    ✅ 满足交易信号 - {signal_type}")
                                    print(f"       原因: |动量| ({abs(momentum):.4f}) >= 阈值 ({threshold})")
                                else:
                                    print(f"    ❌ 不满足交易信号")
                                    print(f"       原因: |动量| ({abs(momentum):.4f}) < 阈值 ({threshold})")
                                    print(f"       说明: 动量不够强")
                        
                        elif strategy_name == "UTBot":
                            # UT Bot策略
                            if hasattr(strategy, 'xATRTrailingStop') and hasattr(strategy, 'pos'):
                                trailing_stop = strategy.xATRTrailingStop
                                current_pos = strategy.pos
                                
                                print(f"    追踪止损: {trailing_stop:.2f}")
                                print(f"    当前状态: {['无仓位', '多头', '空头'][current_pos + 1]}")
                                
                                if current_price > trailing_stop and current_pos != 1:
                                    print(f"    ✅ 满足交易信号 - 做多")
                                    print(f"       原因: 价格 ({current_price:.2f}) > 追踪止损 ({trailing_stop:.2f})")
                                elif current_price < trailing_stop and current_pos != -1:
                                    print(f"    ✅ 满足交易信号 - 做空")
                                    print(f"       原因: 价格 ({current_price:.2f}) < 追踪止损 ({trailing_stop:.2f})")
                                else:
                                    print(f"    ❌ 不满足交易信号")
                                    print(f"       原因: 价格未突破追踪止损线")
                        
                        else:
                            print(f"    ℹ️  等待策略条件满足")
                    
                except Exception as e:
                    print(f"  ❌ 信号分析失败: {e}")
                
            except Exception as e:
                print(f"❌ 持仓和信号检查失败: {e}")
            
            print("\n" + "=" * 60)
            print(f"✅ 监控检查完成 - 下次检查: {(datetime.now() + timedelta(seconds=check_interval)).strftime('%H:%M:%S')}")
            print("=" * 60 + "\n")
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"⚠️  监控任务错误: {e}")
            await asyncio.sleep(check_interval)


async def start_trading_engine(config, user_config):
    """启动交易引擎"""
    monitor_task = None
    
    try:
        # 启动前测试连接
        if not await test_lighter_connection_on_startup(config):
            print("❌ 取消启动")
            return
        
        # 创建交易引擎
        engine = TradingEngine(config)
        
        # 添加策略
        strategy_choice = user_config["strategy_choice"]
        user_input_market_id = user_config["market_id"]  # 用户交互输入的市场ID（仅作为后备）
        
        # 从config.yaml读取策略配置
        strategies_config = config.strategies if hasattr(config, 'strategies') else {}
        
        if strategy_choice in ["1", "5"]:  # 均值回归或所有策略
            # 从config读取参数，如果不存在则使用用户输入值
            mr_config = strategies_config.get('mean_reversion', {})
            # 优先使用config中的market_id，如果config没有才使用用户输入
            strategy_market_id = mr_config.get('market_id') if 'market_id' in mr_config else user_input_market_id
            mean_reversion = MeanReversionStrategy(
                config=config,
                market_id=strategy_market_id,
                lookback_period=mr_config.get('lookback_period', 20),
                threshold=mr_config.get('threshold', 2.0),
                position_size=mr_config.get('position_size', 0.1),
                stop_loss=mr_config.get('stop_loss', 0.02),
                take_profit=mr_config.get('take_profit', 0.01)
            )
            engine.add_strategy(mean_reversion)
            print(f"✅ 已添加均值回归策略 (market_id={strategy_market_id}, position_size={mr_config.get('position_size', 0.1)})")
        
        if strategy_choice in ["2", "5"]:  # 动量或所有策略
            mom_config = strategies_config.get('momentum', {})
            strategy_market_id = mom_config.get('market_id') if 'market_id' in mom_config else user_input_market_id
            momentum = MomentumStrategy(
                config=config,
                market_id=strategy_market_id,
                short_period=mom_config.get('short_period', 5),
                long_period=mom_config.get('long_period', 20),
                momentum_threshold=mom_config.get('momentum_threshold', 0.02),
                position_size=mom_config.get('position_size', 0.1),
                stop_loss=mom_config.get('stop_loss', 0.03),
                take_profit=mom_config.get('take_profit', 0.05)
            )
            engine.add_strategy(momentum)
            print(f"✅ 已添加动量策略 (market_id={strategy_market_id}, position_size={mom_config.get('position_size', 0.1)})")
        
        if strategy_choice in ["3", "5"]:  # 套利或所有策略
            arb_config = strategies_config.get('arbitrage', {})
            strategy_market_id_1 = arb_config.get('market_id_1') if 'market_id_1' in arb_config else user_input_market_id
            strategy_market_id_2 = arb_config.get('market_id_2') if 'market_id_2' in arb_config else (user_input_market_id + 1)
            arbitrage = ArbitrageStrategy(
                config=config,
                market_id_1=strategy_market_id_1,
                market_id_2=strategy_market_id_2,
                price_threshold=arb_config.get('price_threshold', 0.01),
                position_size=arb_config.get('position_size', 0.02),
                stop_loss=arb_config.get('stop_loss', 0.005),
                take_profit=arb_config.get('take_profit', 0.01)
            )
            engine.add_strategy(arbitrage)
            print(f"✅ 已添加套利策略 (market_id_1={strategy_market_id_1}, market_id_2={strategy_market_id_2}, position_size={arb_config.get('position_size', 0.02)})")
        
        if strategy_choice in ["4", "5"]:  # UT Bot或所有策略
            ut_config = strategies_config.get('ut_bot', {})
            # 优先使用config中的market_id，如果config没有才使用用户输入
            strategy_market_id = ut_config.get('market_id') if 'market_id' in ut_config else user_input_market_id
            
            # 创建UTBotConfig对象
            from quant_trading.strategies.ut_bot_strategy import UTBotConfig
            ut_bot_config = UTBotConfig(
                key_value=ut_config.get('key_value', 3.0),
                atr_period=ut_config.get('atr_period', 10),
                use_heikin_ashi=ut_config.get('use_heikin_ashi', False),
                ema_length=ut_config.get('ema_length', 200),
                risk_per_trade=ut_config.get('risk_per_trade', 2.5),
                atr_multiplier=ut_config.get('atr_multiplier', 1.5),
                risk_reward_breakeven=ut_config.get('risk_reward_breakeven', 0.75),
                risk_reward_takeprofit=ut_config.get('risk_reward_takeprofit', 3.0),
                tp_percent=ut_config.get('tp_percent', 50.0),
                stoploss_type=ut_config.get('stoploss_type', "atr"),
                swing_high_bars=ut_config.get('swing_high_bars', 10),
                swing_low_bars=ut_config.get('swing_low_bars', 10),
                enable_long=ut_config.get('enable_long', True),
                enable_short=ut_config.get('enable_short', True),
                use_takeprofit=ut_config.get('use_takeprofit', True),
                use_leverage=ut_config.get('use_leverage', True),
                trading_start_time=ut_config.get('trading_start_time', "00:00"),
                trading_end_time=ut_config.get('trading_end_time', "23:59")
            )
            
            # 创建UT Bot策略实例
            ut_bot = UTBotStrategy(
                name="UTBot",
                config=config,
                ut_config=ut_bot_config
            )
            
            # 设置市场ID
            ut_bot.market_id = strategy_market_id
            
            engine.add_strategy(ut_bot)
            print(f"✅ 已添加UT Bot策略 (market_id={strategy_market_id}, use_real_time_ticks={ut_bot.use_real_time_ticks})")
            print(f"   配置: key_value={ut_bot_config.key_value}, atr_period={ut_bot_config.atr_period}, ema_length={ut_bot_config.ema_length}")
            print(f"   风险管理: risk_per_trade={ut_bot_config.risk_per_trade}%, atr_multiplier={ut_bot_config.atr_multiplier}")
            print(f"   实时tick模式: {'已启用' if ut_bot.use_real_time_ticks else '未启用'}")
        
        print()
        print("🚀 启动交易引擎...")
        print("📊 启动监控任务（每2分钟检查连接和持仓）...")
        print("按 Ctrl+C 停止程序")
        print()
        
        # 启动监控任务（后台运行）
        monitor_task = asyncio.create_task(monitor_connection_and_positions(engine, config))
        
        # 启动交易引擎
        await engine.start()
        
    except KeyboardInterrupt:
        print("\n⏹️  收到停止信号，正在关闭...")
    except Exception as e:
        print(f"❌ 运行错误: {e}")
        raise
    finally:
        # 取消监控任务
        if monitor_task and not monitor_task.done():
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass
        
        if 'engine' in locals():
            await engine.stop()
        print("✅ 交易引擎已停止")


async def main():
    """主函数"""
    print_banner()
    
    # 获取用户配置
    user_config = get_user_config()
    if not user_config:
        return 1
    
    # 创建配置
    config = create_config(user_config)
    
    # 保存配置到文件
    config.save_to_file("user_config.yaml")
    print("✅ 配置已保存到 user_config.yaml")
    print()
    
    # 启动交易引擎
    await start_trading_engine(config, user_config)
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 再见!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 程序错误: {e}")
        sys.exit(1)
