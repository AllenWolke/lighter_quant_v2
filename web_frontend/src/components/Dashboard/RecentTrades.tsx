import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Table, 
  Tag, 
  Space, 
  Typography, 
  Button,
  Tooltip,
  Empty
} from 'antd';
import { 
  ReloadOutlined, 
  EyeOutlined,
  RiseOutlined,
  FallOutlined
} from '@ant-design/icons';
import { useTradingStore } from '../../store/tradingStore';
import { tradingApi } from '../../api';
import { Trade } from '../../types';

const { Title, Text } = Typography;

interface RecentTradesProps {
  className?: string;
}

const RecentTrades: React.FC<RecentTradesProps> = ({ className }) => {
  const [loading, setLoading] = useState(false);
  const [trades, setTrades] = useState<Trade[]>([]);
  
  const { updateOrders } = useTradingStore();

  // 加载最近交易
  const loadRecentTrades = async () => {
    try {
      setLoading(true);
      const data = await tradingApi.getTrades({ limit: 10 });
      setTrades(data);
    } catch (error) {
      console.error('加载最近交易失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 初始化加载
  useEffect(() => {
    loadRecentTrades();
  }, []);

  // 表格列配置
  const columns = [
    {
      title: '交易对',
      dataIndex: 'symbol',
      key: 'symbol',
      width: 80,
      render: (symbol: string) => (
        <Text strong style={{ fontSize: '12px' }}>{symbol}</Text>
      ),
    },
    {
      title: '方向',
      dataIndex: 'side',
      key: 'side',
      width: 60,
      render: (side: string) => (
        <Tag 
          color={side === 'buy' ? 'green' : 'red'} 
          style={{ fontSize: '10px' }}
          icon={side === 'buy' ? <RiseOutlined /> : <FallOutlined />}
        >
          {side === 'buy' ? '买' : '卖'}
        </Tag>
      ),
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
      width: 80,
      render: (quantity: number) => (
        <Text style={{ fontSize: '12px' }}>{quantity.toFixed(4)}</Text>
      ),
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      width: 80,
      render: (price: number) => (
        <Text style={{ fontSize: '12px' }}>${price.toFixed(2)}</Text>
      ),
    },
    {
      title: '盈亏',
      dataIndex: 'pnl',
      key: 'pnl',
      width: 80,
      render: (pnl: number) => {
        const isPositive = pnl >= 0;
        return (
          <Text 
            style={{ 
              fontSize: '12px',
              color: isPositive ? '#52c41a' : '#ff4d4f',
              fontWeight: '500'
            }}
          >
            {isPositive ? '+' : ''}${pnl.toFixed(2)}
          </Text>
        );
      },
    },
    {
      title: '时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      width: 80,
      render: (time: string) => (
        <Text style={{ fontSize: '12px' }}>
          {new Date(time).toLocaleTimeString()}
        </Text>
      ),
    },
  ];

  return (
    <Card 
      title="最近交易" 
      size="small"
      className={className}
      extra={
        <Button
          type="text"
          icon={<ReloadOutlined />}
          onClick={loadRecentTrades}
          loading={loading}
          size="small"
        />
      }
    >
      {loading ? (
        <div style={{ textAlign: 'center', padding: '20px' }}>
          <div style={{ fontSize: '12px', color: '#8c8c8c' }}>加载中...</div>
        </div>
      ) : trades.length === 0 ? (
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description="暂无交易记录"
          style={{ padding: '20px 0' }}
        />
      ) : (
        <Table
          columns={columns}
          dataSource={trades}
          pagination={false}
          size="small"
          scroll={{ y: 200 }}
          rowKey="id"
          style={{ fontSize: '12px' }}
        />
      )}
    </Card>
  );
};

export default RecentTrades;
