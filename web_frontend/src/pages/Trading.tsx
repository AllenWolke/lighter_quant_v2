import React, { useState, useEffect } from 'react';
import { 
  Row, 
  Col, 
  Card, 
  Tabs, 
  Button, 
  Space, 
  message,
  Spin,
  Alert
} from 'antd';
import { 
  PlayCircleOutlined, 
  PauseCircleOutlined, 
  StopOutlined,
  SettingOutlined,
  BarChartOutlined
} from '@ant-design/icons';

// 组件导入
import TradingPanel from '../components/Trading/TradingPanel';
import MarketDataPanel from '../components/Trading/MarketDataPanel';
import PositionPanel from '../components/Trading/PositionPanel';
import OrderPanel from '../components/Trading/OrderPanel';
import ChartPanel from '../components/Trading/ChartPanel';

// 状态管理
import { useTradingStore } from '../store/tradingStore';
import { useWebSocketStore } from '../store/websocketStore';

// API
import { tradingApi } from '../api/trading';

// 类型
import { TradingStatus } from '../types/trading';

const { TabPane } = Tabs;

const Trading: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [tradingStatus, setTradingStatus] = useState<TradingStatus>('stopped');
  
  const { 
    selectedSymbol, 
    selectedStrategy, 
    strategyParams,
    positions,
    orders,
    marketData,
    updateTradingStatus,
    updatePositions,
    updateOrders,
    updateMarketData
  } = useTradingStore();
  
  const { isConnected, connect, disconnect } = useWebSocketStore();

  // 初始化
  useEffect(() => {
    initializeTrading();
    return () => {
      // 清理
      disconnect();
    };
  }, []);

  // 初始化交易
  const initializeTrading = async () => {
    try {
      setLoading(true);
      
      // 连接WebSocket
      await connect();
      
      // 获取初始数据
      await Promise.all([
        loadPositions(),
        loadOrders(),
        loadMarketData()
      ]);
      
      message.success('交易系统初始化成功');
    } catch (error) {
      console.error('初始化失败:', error);
      message.error('交易系统初始化失败');
    } finally {
      setLoading(false);
    }
  };

  // 加载持仓数据
  const loadPositions = async () => {
    try {
      const data = await tradingApi.getPositions();
      updatePositions(data);
    } catch (error) {
      console.error('加载持仓失败:', error);
    }
  };

  // 加载订单数据
  const loadOrders = async () => {
    try {
      const data = await tradingApi.getOrders();
      updateOrders(data);
    } catch (error) {
      console.error('加载订单失败:', error);
    }
  };

  // 加载市场数据
  const loadMarketData = async () => {
    if (!selectedSymbol) return;
    
    try {
      const data = await tradingApi.getMarketData(selectedSymbol);
      updateMarketData(data);
    } catch (error) {
      console.error('加载市场数据失败:', error);
    }
  };

  // 开始交易
  const handleStartTrading = async () => {
    try {
      setLoading(true);
      await tradingApi.startTrading();
      setTradingStatus('running');
      updateTradingStatus('running');
      message.success('交易已开始');
    } catch (error) {
      console.error('启动交易失败:', error);
      message.error('启动交易失败');
    } finally {
      setLoading(false);
    }
  };

  // 暂停交易
  const handlePauseTrading = async () => {
    try {
      setLoading(true);
      await tradingApi.stopTrading();
      setTradingStatus('paused');
      updateTradingStatus('paused');
      message.success('交易已暂停');
    } catch (error) {
      console.error('暂停交易失败:', error);
      message.error('暂停交易失败');
    } finally {
      setLoading(false);
    }
  };

  // 紧急停止
  const handleEmergencyStop = async () => {
    try {
      setLoading(true);
      await tradingApi.emergencyStop();
      setTradingStatus('stopped');
      updateTradingStatus('stopped');
      message.warning('紧急停止已执行');
    } catch (error) {
      console.error('紧急停止失败:', error);
      message.error('紧急停止失败');
    } finally {
      setLoading(false);
    }
  };

  // 渲染状态指示器
  const renderStatusIndicator = () => {
    const statusConfig = {
      running: { color: '#52c41a', text: '运行中', icon: <PlayCircleOutlined /> },
      paused: { color: '#faad14', text: '已暂停', icon: <PauseCircleOutlined /> },
      stopped: { color: '#ff4d4f', text: '已停止', icon: <StopOutlined /> }
    };
    
    const config = statusConfig[tradingStatus];
    
    return (
      <Space>
        <span style={{ color: config.color, fontSize: '16px' }}>
          {config.icon}
        </span>
        <span style={{ color: config.color, fontWeight: 500 }}>
          {config.text}
        </span>
      </Space>
    );
  };

  // 渲染控制按钮
  const renderControlButtons = () => {
    return (
      <Space>
        {tradingStatus === 'stopped' && (
          <Button
            type="primary"
            icon={<PlayCircleOutlined />}
            onClick={handleStartTrading}
            loading={loading}
          >
            开始交易
          </Button>
        )}
        
        {tradingStatus === 'running' && (
          <Button
            icon={<PauseCircleOutlined />}
            onClick={handlePauseTrading}
            loading={loading}
          >
            暂停交易
          </Button>
        )}
        
        {tradingStatus === 'paused' && (
          <Button
            type="primary"
            icon={<PlayCircleOutlined />}
            onClick={handleStartTrading}
            loading={loading}
          >
            恢复交易
          </Button>
        )}
        
        <Button
          danger
          icon={<StopOutlined />}
          onClick={handleEmergencyStop}
          loading={loading}
        >
          紧急停止
        </Button>
      </Space>
    );
  };

  if (loading && tradingStatus === 'stopped') {
    return (
      <div className="loading-container">
        <Spin size="large" />
        <div className="loading-text">正在初始化交易系统...</div>
      </div>
    );
  }

  return (
    <div className="page-content">
      {/* 页面头部 */}
      <div className="page-header">
        <div>
          <h1 className="page-title">交易控制台</h1>
          <p className="page-subtitle">
            实时监控和管理您的量化交易策略
          </p>
        </div>
        <div className="page-actions">
          {renderStatusIndicator()}
          {renderControlButtons()}
        </div>
      </div>

      {/* 连接状态警告 */}
      {!isConnected && (
        <Alert
          message="WebSocket连接断开"
          description="无法获取实时数据，请检查网络连接"
          type="warning"
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      {/* 主要内容 */}
      <Row gutter={[24, 24]}>
        {/* 左侧面板 */}
        <Col xs={24} lg={16}>
          <Tabs defaultActiveKey="trading" type="card">
            <TabPane 
              tab={
                <span>
                  <SettingOutlined />
                  交易设置
                </span>
              } 
              key="trading"
            >
              <TradingPanel />
            </TabPane>
            
            <TabPane 
              tab={
                <span>
                  <BarChartOutlined />
                  图表分析
                </span>
              } 
              key="chart"
            >
              <ChartPanel />
            </TabPane>
          </Tabs>
        </Col>

        {/* 右侧面板 */}
        <Col xs={24} lg={8}>
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            {/* 市场数据 */}
            <MarketDataPanel />
            
            {/* 持仓信息 */}
            <PositionPanel />
            
            {/* 订单管理 */}
            <OrderPanel />
          </Space>
        </Col>
      </Row>
    </div>
  );
};

export default Trading;
