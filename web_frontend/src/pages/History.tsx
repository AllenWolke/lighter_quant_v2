import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Table, 
  Button, 
  Space, 
  Typography, 
  Tag,
  Row,
  Col,
  Statistic,
  Select,
  DatePicker,
  Input,
  Tabs,
  message
} from 'antd';
import { 
  ReloadOutlined,
  DownloadOutlined,
  BarChartOutlined,
  DollarOutlined,
  RiseOutlined,
  FallOutlined
} from '@ant-design/icons';
import { tradingApi, positionApi } from '../api';
import { useWebSocketStore } from '../store/websocketStore';
import { Trade, Order, Position } from '../types';

const { Title, Text } = Typography;
const { Option } = Select;
const { RangePicker } = DatePicker;
const { Search } = Input;
const { TabPane } = Tabs;

const History: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('trades');
  const [trades, setTrades] = useState<Trade[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [positions, setPositions] = useState<Position[]>([]);
  const [filters, setFilters] = useState({
    symbol: '',
    startDate: null as any,
    endDate: null as any,
  });
  
  const { isConnected, connect } = useWebSocketStore();

  // 加载交易历史
  const loadTrades = async () => {
    try {
      setLoading(true);
      const params: any = { limit: 100 };
      if (filters.symbol) params.symbol = filters.symbol;
      if (filters.startDate) params.startDate = filters.startDate.format('YYYY-MM-DD');
      if (filters.endDate) params.endDate = filters.endDate.format('YYYY-MM-DD');
      
      const data = await tradingApi.getTrades(params);
      setTrades(data);
    } catch (error) {
      console.error('加载交易历史失败:', error);
      message.error('加载交易历史失败');
    } finally {
      setLoading(false);
    }
  };

  // 加载订单历史
  const loadOrders = async () => {
    try {
      setLoading(true);
      const params: any = { limit: 100 };
      if (filters.symbol) params.symbol = filters.symbol;
      if (filters.startDate) params.startDate = filters.startDate.format('YYYY-MM-DD');
      if (filters.endDate) params.endDate = filters.endDate.format('YYYY-MM-DD');
      
      const data = await tradingApi.getOrders(params);
      setOrders(data);
    } catch (error) {
      console.error('加载订单历史失败:', error);
      message.error('加载订单历史失败');
    } finally {
      setLoading(false);
    }
  };

  // 加载持仓历史
  const loadPositions = async () => {
    try {
      setLoading(true);
      const params: any = { limit: 100 };
      if (filters.symbol) params.symbol = filters.symbol;
      if (filters.startDate) params.startDate = filters.startDate.format('YYYY-MM-DD');
      if (filters.endDate) params.endDate = filters.endDate.format('YYYY-MM-DD');
      
      const data = await positionApi.getPositionHistory(params);
      setPositions(data.positions || []);
    } catch (error) {
      console.error('加载持仓历史失败:', error);
      message.error('加载持仓历史失败');
    } finally {
      setLoading(false);
    }
  };

  // 根据当前标签页加载数据
  const loadData = () => {
    switch (activeTab) {
      case 'trades':
        loadTrades();
        break;
      case 'orders':
        loadOrders();
        break;
      case 'positions':
        loadPositions();
        break;
    }
  };

  // 初始化加载
  useEffect(() => {
    connect();  // 连接 WebSocket
    loadData();
  }, [activeTab, filters]);

  // 导出数据
  const handleExport = () => {
    let data: any[] = [];
    let filename = '';
    
    switch (activeTab) {
      case 'trades':
        data = trades;
        filename = 'trades';
        break;
      case 'orders':
        data = orders;
        filename = 'orders';
        break;
      case 'positions':
        data = positions;
        filename = 'positions';
        break;
    }
    
    const csvContent = convertToCSV(data);
    downloadCSV(csvContent, `${filename}_${new Date().toISOString().split('T')[0]}.csv`);
  };

  // 转换为CSV格式
  const convertToCSV = (data: any[]) => {
    if (data.length === 0) return '';
    
    const headers = Object.keys(data[0]);
    const csvRows = [
      headers.join(','),
      ...data.map(row => 
        headers.map(header => {
          const value = row[header];
          return typeof value === 'string' ? `"${value}"` : value;
        }).join(',')
      )
    ];
    
    return csvRows.join('\n');
  };

  // 下载CSV文件
  const downloadCSV = (content: string, filename: string) => {
    const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // 交易表格列配置
  const tradeColumns = [
    {
      title: '交易对',
      dataIndex: 'symbol',
      key: 'symbol',
      width: 100,
      render: (symbol: string) => <Text strong>{symbol}</Text>,
    },
    {
      title: '方向',
      dataIndex: 'side',
      key: 'side',
      width: 80,
      render: (side: string) => (
        <Tag color={side === 'buy' ? 'green' : 'red'}>
          {side === 'buy' ? '买入' : '卖出'}
        </Tag>
      ),
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
      width: 100,
      render: (quantity: number) => quantity.toFixed(4),
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      width: 100,
      render: (price: number) => `$${price.toFixed(2)}`,
    },
    {
      title: '手续费',
      dataIndex: 'fee',
      key: 'fee',
      width: 100,
      render: (fee: number) => `$${fee.toFixed(4)}`,
    },
    {
      title: '盈亏',
      dataIndex: 'pnl',
      key: 'pnl',
      width: 100,
      render: (pnl: number) => (
        <Text style={{ color: pnl >= 0 ? '#52c41a' : '#ff4d4f' }}>
          {pnl >= 0 ? '+' : ''}${pnl.toFixed(2)}
        </Text>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 80,
      render: (status: string) => {
        const statusMap: Record<string, { color: string; text: string }> = {
          pending: { color: 'processing', text: '待成交' },
          filled: { color: 'success', text: '已成交' },
          cancelled: { color: 'default', text: '已取消' },
          rejected: { color: 'error', text: '已拒绝' },
        };
        const config = statusMap[status] || { color: 'default', text: status };
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    {
      title: '时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      width: 150,
      render: (time: string) => new Date(time).toLocaleString(),
    },
  ];

  // 订单表格列配置
  const orderColumns = [
    {
      title: '交易对',
      dataIndex: 'symbol',
      key: 'symbol',
      width: 100,
      render: (symbol: string) => <Text strong>{symbol}</Text>,
    },
    {
      title: '方向',
      dataIndex: 'side',
      key: 'side',
      width: 80,
      render: (side: string) => (
        <Tag color={side === 'buy' ? 'green' : 'red'}>
          {side === 'buy' ? '买入' : '卖出'}
        </Tag>
      ),
    },
    {
      title: '类型',
      dataIndex: 'orderType',
      key: 'orderType',
      width: 100,
      render: (type: string) => {
        const typeMap: Record<string, string> = {
          market: '市价',
          limit: '限价',
          stop_loss: '止损',
          take_profit: '止盈',
        };
        return typeMap[type] || type;
      },
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
      width: 100,
      render: (quantity: number) => quantity.toFixed(4),
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      width: 100,
      render: (price: number) => price ? `$${price.toFixed(2)}` : '市价',
    },
    {
      title: '已成交',
      dataIndex: 'filledQuantity',
      key: 'filledQuantity',
      width: 100,
      render: (filled: number, record: Order) => (
        <div>
          <div>{filled.toFixed(4)}</div>
          <div style={{ fontSize: '12px', color: '#8c8c8c' }}>
            {((filled / record.quantity) * 100).toFixed(1)}%
          </div>
        </div>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const statusMap: Record<string, { color: string; text: string }> = {
          pending: { color: 'processing', text: '待成交' },
          partially_filled: { color: 'warning', text: '部分成交' },
          filled: { color: 'success', text: '已成交' },
          cancelled: { color: 'default', text: '已取消' },
          rejected: { color: 'error', text: '已拒绝' },
        };
        const config = statusMap[status] || { color: 'default', text: status };
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    {
      title: '时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      width: 150,
      render: (time: string) => new Date(time).toLocaleString(),
    },
  ];

  // 持仓表格列配置
  const positionColumns = [
    {
      title: '交易对',
      dataIndex: 'symbol',
      key: 'symbol',
      width: 100,
      render: (symbol: string) => <Text strong>{symbol}</Text>,
    },
    {
      title: '方向',
      dataIndex: 'side',
      key: 'side',
      width: 80,
      render: (side: string) => (
        <Tag color={side === 'long' ? 'green' : 'red'}>
          {side === 'long' ? '多头' : '空头'}
        </Tag>
      ),
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
      width: 100,
      render: (quantity: number) => quantity.toFixed(4),
    },
    {
      title: '入场价',
      dataIndex: 'entryPrice',
      key: 'entryPrice',
      width: 100,
      render: (price: number) => `$${price.toFixed(2)}`,
    },
    {
      title: '出场价',
      dataIndex: 'currentPrice',
      key: 'currentPrice',
      width: 100,
      render: (price: number) => `$${price.toFixed(2)}`,
    },
    {
      title: '盈亏',
      dataIndex: 'unrealizedPnl',
      key: 'unrealizedPnl',
      width: 100,
      render: (pnl: number) => (
        <Text style={{ color: pnl >= 0 ? '#52c41a' : '#ff4d4f' }}>
          {pnl >= 0 ? '+' : ''}${pnl.toFixed(2)}
        </Text>
      ),
    },
    {
      title: '杠杆',
      dataIndex: 'leverage',
      key: 'leverage',
      width: 80,
      render: (leverage: number) => `${leverage}x`,
    },
    {
      title: '状态',
      dataIndex: 'isActive',
      key: 'isActive',
      width: 80,
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'green' : 'default'}>
          {isActive ? '活跃' : '已关闭'}
        </Tag>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      width: 150,
      render: (time: string) => new Date(time).toLocaleString(),
    },
    {
      title: '关闭时间',
      dataIndex: 'closedAt',
      key: 'closedAt',
      width: 150,
      render: (time: string) => time ? new Date(time).toLocaleString() : '-',
    },
  ];

  // 计算统计信息
  const getStats = () => {
    switch (activeTab) {
      case 'trades':
        return {
          total: trades.length,
          totalPnl: trades.reduce((sum, t) => sum + t.pnl, 0),
          totalFee: trades.reduce((sum, t) => sum + t.fee, 0),
          winRate: trades.length > 0 
            ? (trades.filter(t => t.pnl > 0).length / trades.length * 100).toFixed(1)
            : 0,
        };
      case 'orders':
        return {
          total: orders.length,
          filled: orders.filter(o => o.status === 'filled').length,
          cancelled: orders.filter(o => o.status === 'cancelled').length,
          pending: orders.filter(o => o.status === 'pending').length,
        };
      case 'positions':
        return {
          total: positions.length,
          active: positions.filter(p => p.isActive).length,
          totalPnl: positions.reduce((sum, p) => sum + p.unrealizedPnl, 0),
          averageLeverage: positions.length > 0 
            ? (positions.reduce((sum, p) => sum + p.leverage, 0) / positions.length).toFixed(1)
            : 0,
        };
      default:
        return {};
    }
  };

  const stats = getStats();

  return (
    <div className="page-content">
      {/* 页面头部 */}
      <div className="page-header">
        <div>
          <Title level={2} style={{ margin: 0 }}>交易历史</Title>
          <Text type="secondary">查看您的交易记录和历史数据</Text>
        </div>
        <Space>
          <Button
            icon={<ReloadOutlined />}
            onClick={loadData}
            loading={loading}
          >
            刷新
          </Button>
          <Button
            icon={<DownloadOutlined />}
            onClick={handleExport}
          >
            导出数据
          </Button>
        </Space>
      </div>

      {/* 筛选器 */}
      <Card style={{ marginBottom: 24 }}>
        <Row gutter={16} align="middle">
          <Col span={6}>
            <Select
              placeholder="选择交易对"
              value={filters.symbol}
              onChange={(value) => setFilters({ ...filters, symbol: value })}
              style={{ width: '100%' }}
              allowClear
            >
              <Option value="ETH/USDT">ETH/USDT</Option>
              <Option value="BTC/USDT">BTC/USDT</Option>
              <Option value="BNB/USDT">BNB/USDT</Option>
              <Option value="ADA/USDT">ADA/USDT</Option>
              <Option value="SOL/USDT">SOL/USDT</Option>
            </Select>
          </Col>
          <Col span={6}>
            <RangePicker
              value={[filters.startDate, filters.endDate]}
              onChange={(dates) => setFilters({ 
                ...filters, 
                startDate: dates?.[0] || null, 
                endDate: dates?.[1] || null 
              })}
              style={{ width: '100%' }}
            />
          </Col>
          <Col span={6}>
            <Button onClick={() => setFilters({ symbol: '', startDate: null, endDate: null })}>
              重置筛选
            </Button>
          </Col>
        </Row>
      </Card>

      {/* 统计卡片 */}
      <Row gutter={[24, 24]} style={{ marginBottom: 24 }}>
        {activeTab === 'trades' && (
          <>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="总交易数"
                  value={stats.total}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="总盈亏"
                  value={stats.totalPnl || 0}
                  precision={2}
                  prefix="$"
                  valueStyle={{ color: (stats.totalPnl || 0) >= 0 ? '#52c41a' : '#ff4d4f' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="总手续费"
                  value={stats.totalFee}
                  precision={4}
                  prefix="$"
                  valueStyle={{ color: '#faad14' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="胜率"
                  value={stats.winRate}
                  precision={1}
                  suffix="%"
                  valueStyle={{ color: '#52c41a' }}
                />
              </Card>
            </Col>
          </>
        )}
        {activeTab === 'orders' && (
          <>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="总订单数"
                  value={stats.total}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="已成交"
                  value={stats.filled}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="已取消"
                  value={stats.cancelled}
                  valueStyle={{ color: '#8c8c8c' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="待成交"
                  value={stats.pending}
                  valueStyle={{ color: '#faad14' }}
                />
              </Card>
            </Col>
          </>
        )}
        {activeTab === 'positions' && (
          <>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="总持仓数"
                  value={stats.total}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="活跃持仓"
                  value={stats.active}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="总盈亏"
                  value={stats.totalPnl || 0}
                  precision={2}
                  prefix="$"
                  valueStyle={{ color: (stats.totalPnl || 0) >= 0 ? '#52c41a' : '#ff4d4f' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="平均杠杆"
                  value={stats.averageLeverage}
                  suffix="x"
                  valueStyle={{ color: '#faad14' }}
                />
              </Card>
            </Col>
          </>
        )}
      </Row>

      {/* 历史数据标签页 */}
      <Card>
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <TabPane tab="交易记录" key="trades">
            <Table
              columns={tradeColumns}
              dataSource={trades}
              loading={loading}
              rowKey="id"
              pagination={{
                pageSize: 20,
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
              }}
            />
          </TabPane>
          
          <TabPane tab="订单记录" key="orders">
            <Table
              columns={orderColumns}
              dataSource={orders}
              loading={loading}
              rowKey="id"
              pagination={{
                pageSize: 20,
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
              }}
            />
          </TabPane>
          
          <TabPane tab="持仓记录" key="positions">
            <Table
              columns={positionColumns}
              dataSource={positions}
              loading={loading}
              rowKey="id"
              pagination={{
                pageSize: 20,
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
              }}
            />
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default History;
