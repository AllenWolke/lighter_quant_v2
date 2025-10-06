import React, { useState, useEffect } from 'react';
import { 
  Row, 
  Col, 
  Card, 
  Statistic, 
  Typography, 
  Space,
  Button,
  Progress,
  Alert,
  Spin,
  Tabs
} from 'antd';
import { 
  DollarOutlined, 
  RiseOutlined, 
  FallOutlined,
  WalletOutlined,
  TrophyOutlined,
  WarningOutlined,
  ReloadOutlined,
  BarChartOutlined,
  PieChartOutlined
} from '@ant-design/icons';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

// 状态管理
import { useTradingStore } from '../store/tradingStore';
import { useAuthStore } from '../store/authStore';

// API
import { tradingApi } from '../api';

// 组件
import RecentTrades from '../components/Dashboard/RecentTrades';
import ActivePositions from '../components/Dashboard/ActivePositions';
import MarketOverview from '../components/Dashboard/MarketOverview';

const { Title, Text } = Typography;
const { TabPane } = Tabs;

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  
  const { 
    accountInfo, 
    tradingStats, 
    positions, 
    orders,
    updateAccountInfo,
    updateTradingStats,
    updatePositions,
    updateOrders
  } = useTradingStore();
  
  const { user } = useAuthStore();

  // 模拟数据
  const [pnlData] = useState([
    { date: '2024-01-01', pnl: 1000 },
    { date: '2024-01-02', pnl: 1200 },
    { date: '2024-01-03', pnl: 800 },
    { date: '2024-01-04', pnl: 1500 },
    { date: '2024-01-05', pnl: 1800 },
    { date: '2024-01-06', pnl: 1600 },
    { date: '2024-01-07', pnl: 2000 },
  ]);

  const [strategyData] = useState([
    { name: 'UT Bot', value: 45, color: '#1890ff' },
    { name: '均值回归', value: 30, color: '#52c41a' },
    { name: '动量策略', value: 20, color: '#faad14' },
    { name: '套利策略', value: 5, color: '#f5222d' },
  ]);

  // 初始化数据
  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      const [accountData, statsData, positionsData, ordersData] = await Promise.all([
        tradingApi.getAccountInfo(),
        tradingApi.getTradingStats(),
        tradingApi.getPositions(),
        tradingApi.getOrders({ limit: 10 })
      ]);
      
      updateAccountInfo(accountData);
      updateTradingStats(statsData);
      updatePositions(positionsData);
      updateOrders(ordersData);
    } catch (error) {
      console.error('加载仪表板数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  if (loading) {
    return (
      <div className="loading-container">
        <Spin size="large" />
        <div className="loading-text">正在加载仪表板数据...</div>
      </div>
    );
  }

  return (
    <div className="page-content">
      {/* 页面头部 */}
      <div className="page-header">
        <div>
          <Title level={2} style={{ margin: 0 }}>
            欢迎回来，{user?.fullName || user?.username}
          </Title>
          <Text type="secondary">
            这里是您的量化交易控制中心
          </Text>
        </div>
        <Button
          icon={<ReloadOutlined />}
          onClick={handleRefresh}
          loading={refreshing}
        >
          刷新数据
        </Button>
      </div>

      {/* 风险警告 */}
      {accountInfo && accountInfo.riskLevel === 'high' && (
        <Alert
          message="高风险警告"
          description="当前账户风险等级较高，建议调整仓位或降低杠杆"
          type="warning"
          icon={<WarningOutlined />}
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      {/* 统计卡片 */}
      <Row gutter={[24, 24]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="账户余额"
              value={accountInfo?.balance || 0}
              precision={2}
              prefix={<DollarOutlined />}
              suffix="USDT"
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总盈亏"
              value={accountInfo?.totalPnl || 0}
              precision={2}
              prefix={accountInfo?.totalPnl && accountInfo.totalPnl >= 0 ? <RiseOutlined /> : <FallOutlined />}
              suffix="USDT"
              valueStyle={{ 
                color: accountInfo?.totalPnl && accountInfo.totalPnl >= 0 ? '#52c41a' : '#ff4d4f' 
              }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="活跃持仓"
              value={positions.filter(p => p.isActive).length}
              prefix={<WalletOutlined />}
              suffix="个"
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="胜率"
              value={tradingStats?.winRate || 0}
              precision={1}
              prefix={<TrophyOutlined />}
              suffix="%"
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 主要内容 */}
      <Row gutter={[24, 24]}>
        {/* 左侧内容 */}
        <Col xs={24} lg={16}>
          <Tabs defaultActiveKey="performance">
            <TabPane 
              tab={
                <span>
                  <BarChartOutlined />
                  性能分析
                </span>
              } 
              key="performance"
            >
              <Card title="盈亏趋势" style={{ marginBottom: 24 }}>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={pnlData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip 
                      formatter={(value: any) => [`${value} USDT`, '盈亏']}
                      labelFormatter={(label) => `日期: ${label}`}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="pnl" 
                      stroke="#1890ff" 
                      strokeWidth={2}
                      dot={{ fill: '#1890ff', strokeWidth: 2, r: 4 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Card>

              <Card title="策略分布">
                <Row gutter={24}>
                  <Col span={12}>
                    <ResponsiveContainer width="100%" height={250}>
                      <PieChart>
                        <Pie
                          data={strategyData}
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={100}
                          dataKey="value"
                        >
                          {strategyData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip formatter={(value: any) => [`${value}%`, '占比']} />
                      </PieChart>
                    </ResponsiveContainer>
                  </Col>
                  <Col span={12}>
                    <Space direction="vertical" style={{ width: '100%', paddingTop: '40px' }}>
                      {strategyData.map((item, index) => (
                        <div key={index} style={{ display: 'flex', alignItems: 'center' }}>
                          <div 
                            style={{ 
                              width: '12px', 
                              height: '12px', 
                              backgroundColor: item.color, 
                              marginRight: '8px',
                              borderRadius: '2px'
                            }} 
                          />
                          <Text>{item.name}: {item.value}%</Text>
                        </div>
                      ))}
                    </Space>
                  </Col>
                </Row>
              </Card>
            </TabPane>
            
            <TabPane 
              tab={
                <span>
                  <PieChartOutlined />
                  市场概览
                </span>
              } 
              key="market"
            >
              <MarketOverview />
            </TabPane>
          </Tabs>
        </Col>

        {/* 右侧内容 */}
        <Col xs={24} lg={8}>
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            {/* 账户信息 */}
            <Card title="账户信息" size="small">
              <Space direction="vertical" style={{ width: '100%' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Text type="secondary">可用余额</Text>
                  <Text strong>{accountInfo?.availableBalance?.toFixed(2)} USDT</Text>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Text type="secondary">保证金</Text>
                  <Text strong>{accountInfo?.marginBalance?.toFixed(2)} USDT</Text>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Text type="secondary">未实现盈亏</Text>
                  <Text strong style={{ 
                    color: accountInfo?.unrealizedPnl && accountInfo.unrealizedPnl >= 0 ? '#52c41a' : '#ff4d4f' 
                  }}>
                    {accountInfo?.unrealizedPnl?.toFixed(2)} USDT
                  </Text>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Text type="secondary">保证金率</Text>
                  <Text strong>{((accountInfo?.marginRatio || 0) * 100).toFixed(2)}%</Text>
                </div>
                <Progress 
                  percent={(accountInfo?.marginRatio || 0) * 100} 
                  status={accountInfo?.riskLevel === 'high' ? 'exception' : 'normal'}
                  showInfo={false}
                />
              </Space>
            </Card>

            {/* 活跃持仓 */}
            <ActivePositions />

            {/* 最近交易 */}
            <RecentTrades />
          </Space>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
