import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Table, 
  Tag, 
  Space, 
  Typography, 
  Button,
  Row,
  Col,
  Statistic,
  Empty
} from 'antd';
import { 
  ReloadOutlined, 
  RiseOutlined,
  FallOutlined,
  DollarOutlined
} from '@ant-design/icons';
import { tradingApi } from '../../api';
import { MarketData } from '../../types';

const { Title, Text } = Typography;

interface MarketOverviewProps {
  className?: string;
}

const MarketOverview: React.FC<MarketOverviewProps> = ({ className }) => {
  const [loading, setLoading] = useState(false);
  const [marketData, setMarketData] = useState<MarketData[]>([]);

  // 主要交易对
  const symbols = ['ETH/USDT', 'BTC/USDT', 'BNB/USDT', 'ADA/USDT', 'SOL/USDT'];

  // 加载市场数据
  const loadMarketData = async () => {
    try {
      setLoading(true);
      const promises = symbols.map(symbol => 
        tradingApi.getMarketData(symbol, '1d').catch(() => null)
      );
      
      const results = await Promise.all(promises);
      const validData = results.filter((data): data is MarketData => data !== null);
      setMarketData(validData);
    } catch (error) {
      console.error('加载市场数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 初始化加载
  useEffect(() => {
    loadMarketData();
  }, []);

  // 表格列配置
  const columns = [
    {
      title: '交易对',
      dataIndex: 'symbol',
      key: 'symbol',
      width: 100,
      render: (symbol: string) => (
        <Text strong style={{ fontSize: '12px' }}>{symbol}</Text>
      ),
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      width: 100,
      render: (price: number) => (
        <Text style={{ fontSize: '12px' }}>${price.toFixed(2)}</Text>
      ),
    },
    {
      title: '24h涨跌',
      dataIndex: 'changePercent24h',
      key: 'changePercent24h',
      width: 100,
      render: (change: number) => {
        const isPositive = change >= 0;
        return (
          <Tag 
            color={isPositive ? 'green' : 'red'}
            icon={isPositive ? <RiseOutlined /> : <FallOutlined />}
            style={{ fontSize: '10px' }}
          >
            {isPositive ? '+' : ''}{change.toFixed(2)}%
          </Tag>
        );
      },
    },
    {
      title: '24h最高',
      dataIndex: 'high24h',
      key: 'high24h',
      width: 100,
      render: (high: number) => (
        <Text style={{ fontSize: '12px' }}>${high.toFixed(2)}</Text>
      ),
    },
    {
      title: '24h最低',
      dataIndex: 'low24h',
      key: 'low24h',
      width: 100,
      render: (low: number) => (
        <Text style={{ fontSize: '12px' }}>${low.toFixed(2)}</Text>
      ),
    },
    {
      title: '24h成交量',
      dataIndex: 'volume24h',
      key: 'volume24h',
      width: 120,
      render: (volume: number) => (
        <Text style={{ fontSize: '12px' }}>
          {(volume / 1000000).toFixed(2)}M
        </Text>
      ),
    },
  ];

  // 计算市场统计
  const marketStats = {
    totalSymbols: marketData.length,
    positiveCount: marketData.filter(data => data.changePercent24h >= 0).length,
    negativeCount: marketData.filter(data => data.changePercent24h < 0).length,
    averageChange: marketData.length > 0 
      ? marketData.reduce((sum, data) => sum + data.changePercent24h, 0) / marketData.length 
      : 0,
    totalVolume: marketData.reduce((sum, data) => sum + data.volume24h, 0),
  };

  return (
    <Card 
      title="市场概览" 
      className={className}
      extra={
        <Button
          type="text"
          icon={<ReloadOutlined />}
          onClick={loadMarketData}
          loading={loading}
          size="small"
        />
      }
    >
      {/* 市场统计 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Statistic
            title="交易对数量"
            value={marketStats.totalSymbols}
            prefix={<DollarOutlined />}
            valueStyle={{ fontSize: '16px' }}
          />
        </Col>
        <Col span={6}>
          <Statistic
            title="上涨数量"
            value={marketStats.positiveCount}
            valueStyle={{ color: '#52c41a', fontSize: '16px' }}
            prefix={<RiseOutlined />}
          />
        </Col>
        <Col span={6}>
          <Statistic
            title="下跌数量"
            value={marketStats.negativeCount}
            valueStyle={{ color: '#ff4d4f', fontSize: '16px' }}
            prefix={<FallOutlined />}
          />
        </Col>
        <Col span={6}>
          <Statistic
            title="平均涨跌"
            value={marketStats.averageChange}
            precision={2}
            suffix="%"
            valueStyle={{ 
              color: marketStats.averageChange >= 0 ? '#52c41a' : '#ff4d4f',
              fontSize: '16px'
            }}
          />
        </Col>
      </Row>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <div style={{ fontSize: '14px', color: '#8c8c8c' }}>加载市场数据中...</div>
        </div>
      ) : marketData.length === 0 ? (
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description="暂无市场数据"
          style={{ padding: '40px 0' }}
        />
      ) : (
        <Table
          columns={columns}
          dataSource={marketData}
          pagination={false}
          size="small"
          scroll={{ y: 300 }}
          rowKey="symbol"
          style={{ fontSize: '12px' }}
        />
      )}
    </Card>
  );
};

export default MarketOverview;
