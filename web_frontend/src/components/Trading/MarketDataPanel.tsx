import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Table, 
  Tag, 
  Space, 
  Typography, 
  Button,
  Select,
  Spin,
  Alert
} from 'antd';
import { 
  ReloadOutlined, 
  RiseOutlined, 
  FallOutlined,
  DollarOutlined
} from '@ant-design/icons';
import { useTradingStore } from '../../store/tradingStore';
import { useWebSocketStore } from '../../store/websocketStore';
import { tradingApi } from '../../api';
import { MarketData } from '../../types';

const { Title, Text } = Typography;
const { Option } = Select;

interface MarketDataPanelProps {
  className?: string;
}

const MarketDataPanel: React.FC<MarketDataPanelProps> = ({ className }) => {
  const [loading, setLoading] = useState(false);
  const [selectedTimeframe, setSelectedTimeframe] = useState('1m');
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  
  const { selectedSymbol, updateMarketData } = useTradingStore();
  const { isConnected } = useWebSocketStore();

  // 时间周期选项
  const timeframeOptions = [
    { value: '1m', label: '1分钟' },
    { value: '5m', label: '5分钟' },
    { value: '15m', label: '15分钟' },
    { value: '1h', label: '1小时' },
    { value: '4h', label: '4小时' },
    { value: '1d', label: '1天' },
  ];

  // 加载市场数据
  const loadMarketData = async () => {
    if (!selectedSymbol) return;
    
    try {
      setLoading(true);
      const data = await tradingApi.getMarketData(selectedSymbol, selectedTimeframe);
      setMarketData([data]);
      updateMarketData(data);
    } catch (error) {
      console.error('加载市场数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 初始化加载
  useEffect(() => {
    loadMarketData();
  }, [selectedSymbol, selectedTimeframe]);

  // WebSocket实时数据更新
  useEffect(() => {
    if (!isConnected || !selectedSymbol) return;

    const handleMarketData = (message: any) => {
      if (message.type === 'market_data' && message.data.symbol === selectedSymbol) {
        setMarketData(prev => {
          const newData = [message.data, ...prev.slice(0, 9)]; // 保留最新10条
          updateMarketData(message.data);
          return newData;
        });
      }
    };

    // 订阅市场数据
    const unsubscribe = useWebSocketStore.getState().onMessage(handleMarketData);
    
    return unsubscribe;
  }, [isConnected, selectedSymbol, updateMarketData]);

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
        <Text strong style={{ fontSize: '12px' }}>
          ${price.toFixed(2)}
        </Text>
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
          >
            {isPositive ? '+' : ''}{change.toFixed(2)}%
          </Tag>
        );
      },
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

  return (
    <Card 
      title="市场数据" 
      size="small"
      className={className}
      extra={
        <Space>
          <Select
            value={selectedTimeframe}
            onChange={setSelectedTimeframe}
            size="small"
            style={{ width: 80 }}
          >
            {timeframeOptions.map(option => (
              <Option key={option.value} value={option.value}>
                {option.label}
              </Option>
            ))}
          </Select>
          <Button
            type="text"
            icon={<ReloadOutlined />}
            onClick={loadMarketData}
            loading={loading}
            size="small"
          />
        </Space>
      }
    >
      {!isConnected && (
        <Alert
          message="连接断开"
          description="无法获取实时数据"
          type="warning"
          style={{ marginBottom: 12 }}
        />
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '20px' }}>
          <Spin size="small" />
          <div style={{ marginTop: 8, fontSize: '12px', color: '#8c8c8c' }}>
            加载中...
          </div>
        </div>
      ) : marketData.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '20px', color: '#8c8c8c' }}>
          <DollarOutlined style={{ fontSize: '24px', marginBottom: '8px' }} />
          <div>暂无数据</div>
        </div>
      ) : (
        <Table
          columns={columns}
          dataSource={marketData}
          pagination={false}
          size="small"
          showHeader={false}
          rowKey="symbol"
          style={{ fontSize: '12px' }}
        />
      )}

      {selectedSymbol && (
        <div style={{ 
          marginTop: 12, 
          padding: '8px 12px', 
          background: '#f5f5f5', 
          borderRadius: '4px',
          fontSize: '12px',
          color: '#8c8c8c'
        }}>
          <Space>
            <Text>当前选择: {selectedSymbol}</Text>
            <Text>周期: {timeframeOptions.find(opt => opt.value === selectedTimeframe)?.label}</Text>
          </Space>
        </div>
      )}
    </Card>
  );
};

export default MarketDataPanel;
