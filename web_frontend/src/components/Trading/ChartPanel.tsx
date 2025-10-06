import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Select, 
  Button, 
  Space, 
  Typography, 
  Row,
  Col,
  Spin,
  Alert,
  Tooltip
} from 'antd';
import { 
  ReloadOutlined, 
  FullscreenOutlined,
  SettingOutlined,
  BarChartOutlined,
  LineChartOutlined
} from '@ant-design/icons';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip as RechartsTooltip, 
  ResponsiveContainer,
} from 'recharts';
import { useTradingStore } from '../../store/tradingStore';
import { useWebSocketStore } from '../../store/websocketStore';
import { tradingApi } from '../../api';
import { KlineData } from '../../types';

const { Title, Text } = Typography;
const { Option } = Select;

interface ChartPanelProps {
  className?: string;
}

const ChartPanel: React.FC<ChartPanelProps> = ({ className }) => {
  const [loading, setLoading] = useState(false);
  const [chartType, setChartType] = useState<'line' | 'candlestick'>('candlestick');
  const [timeframe, setTimeframe] = useState('1m');
  const [klineData, setKlineData] = useState<KlineData[]>([]);
  const [indicators, setIndicators] = useState<string[]>(['ma5', 'ma20']);
  
  const { selectedSymbol, updateKlineData } = useTradingStore();
  const { isConnected } = useWebSocketStore();

  // 时间周期选项
  const timeframeOptions = [
    { value: '1m', label: '1分钟' },
    { value: '5m', label: '5分钟' },
    { value: '15m', label: '15分钟' },
    { value: '30m', label: '30分钟' },
    { value: '1h', label: '1小时' },
    { value: '4h', label: '4小时' },
    { value: '1d', label: '1天' },
  ];

  // 指标选项
  const indicatorOptions = [
    { value: 'ma5', label: 'MA5' },
    { value: 'ma10', label: 'MA10' },
    { value: 'ma20', label: 'MA20' },
    { value: 'ma50', label: 'MA50' },
    { value: 'ema12', label: 'EMA12' },
    { value: 'ema26', label: 'EMA26' },
    { value: 'macd', label: 'MACD' },
    { value: 'rsi', label: 'RSI' },
    { value: 'bollinger', label: '布林带' },
  ];

  // 加载K线数据
  const loadKlineData = async () => {
    if (!selectedSymbol) return;
    
    try {
      setLoading(true);
      const response = await tradingApi.getKlines(selectedSymbol, timeframe, 200);
      setKlineData(response.data);
      updateKlineData(response.data);
    } catch (error) {
      console.error('加载K线数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 初始化加载
  useEffect(() => {
    loadKlineData();
  }, [selectedSymbol, timeframe]);

  // WebSocket实时数据更新
  useEffect(() => {
    if (!isConnected || !selectedSymbol) return;

    const handleKlineData = (message: any) => {
      if (message.type === 'kline' && message.data.symbol === selectedSymbol) {
        setKlineData(prev => {
          const newData = [...prev];
          const lastCandle = newData[newData.length - 1];
          
          if (lastCandle && lastCandle.timestamp === message.data.timestamp) {
            // 更新最后一根K线
            newData[newData.length - 1] = message.data;
          } else {
            // 添加新的K线
            newData.push(message.data);
            if (newData.length > 200) {
              newData.shift(); // 保持最多200根K线
            }
          }
          
          updateKlineData(newData);
          return newData;
        });
      }
    };

    // 订阅K线数据
    const unsubscribe = useWebSocketStore.getState().onMessage(handleKlineData);
    
    return unsubscribe;
  }, [isConnected, selectedSymbol, updateKlineData]);

  // 计算移动平均线
  const calculateMA = (data: KlineData[], period: number) => {
    return data.map((item, index) => {
      if (index < period - 1) return null;
      const sum = data.slice(index - period + 1, index + 1).reduce((acc, curr) => acc + curr.close, 0);
      return sum / period;
    });
  };

  // 处理图表数据
  const chartData = klineData.map((item, index) => {
    const data: any = {
      timestamp: item.timestamp,
      time: new Date(item.timestamp).toLocaleTimeString(),
      open: item.open,
      high: item.high,
      low: item.low,
      close: item.close,
      volume: item.volume,
    };

    // 添加移动平均线
    if (indicators.includes('ma5')) {
      data.ma5 = calculateMA(klineData, 5)[index];
    }
    if (indicators.includes('ma10')) {
      data.ma10 = calculateMA(klineData, 10)[index];
    }
    if (indicators.includes('ma20')) {
      data.ma20 = calculateMA(klineData, 20)[index];
    }
    if (indicators.includes('ma50')) {
      data.ma50 = calculateMA(klineData, 50)[index];
    }

    return data;
  });

  // 渲染K线图
  const renderCandlestickChart = () => {
    return (
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="time" 
            tick={{ fontSize: 12 }}
            interval="preserveStartEnd"
          />
          <YAxis 
            domain={['dataMin', 'dataMax']}
            tick={{ fontSize: 12 }}
          />
          <RechartsTooltip 
            content={({ active, payload, label }) => {
              if (active && payload && payload.length) {
                const data = payload[0].payload;
                return (
                  <div style={{
                    background: '#fff',
                    border: '1px solid #ccc',
                    borderRadius: '4px',
                    padding: '8px',
                    fontSize: '12px'
                  }}>
                    <div><strong>时间:</strong> {label}</div>
                    <div><strong>开盘:</strong> ${data.open?.toFixed(2)}</div>
                    <div><strong>最高:</strong> ${data.high?.toFixed(2)}</div>
                    <div><strong>最低:</strong> ${data.low?.toFixed(2)}</div>
                    <div><strong>收盘:</strong> ${data.close?.toFixed(2)}</div>
                    <div><strong>成交量:</strong> {data.volume?.toLocaleString()}</div>
                  </div>
                );
              }
              return null;
            }}
          />
          <Line 
            type="monotone" 
            dataKey="close" 
            stroke="#1890ff" 
            strokeWidth={2}
            dot={false}
          />
          
          {/* 移动平均线 */}
          {indicators.includes('ma5') && (
            <Line type="monotone" dataKey="ma5" stroke="#ff7300" strokeWidth={1} dot={false} />
          )}
          {indicators.includes('ma10') && (
            <Line type="monotone" dataKey="ma10" stroke="#00ff00" strokeWidth={1} dot={false} />
          )}
          {indicators.includes('ma20') && (
            <Line type="monotone" dataKey="ma20" stroke="#0088fe" strokeWidth={1} dot={false} />
          )}
          {indicators.includes('ma50') && (
            <Line type="monotone" dataKey="ma50" stroke="#ff00ff" strokeWidth={1} dot={false} />
          )}
        </LineChart>
      </ResponsiveContainer>
    );
  };

  // 渲染折线图
  const renderLineChart = () => {
    return (
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="time" 
            tick={{ fontSize: 12 }}
            interval="preserveStartEnd"
          />
          <YAxis 
            domain={['dataMin', 'dataMax']}
            tick={{ fontSize: 12 }}
          />
          <RechartsTooltip 
            content={({ active, payload, label }) => {
              if (active && payload && payload.length) {
                const data = payload[0].payload;
                return (
                  <div style={{
                    background: '#fff',
                    border: '1px solid #ccc',
                    borderRadius: '4px',
                    padding: '8px',
                    fontSize: '12px'
                  }}>
                    <div><strong>时间:</strong> {label}</div>
                    <div><strong>价格:</strong> ${data.close?.toFixed(2)}</div>
                    <div><strong>成交量:</strong> {data.volume?.toLocaleString()}</div>
                  </div>
                );
              }
              return null;
            }}
          />
          <Line 
            type="monotone" 
            dataKey="close" 
            stroke="#1890ff" 
            strokeWidth={2}
            dot={false}
          />
          
          {/* 移动平均线 */}
          {indicators.includes('ma5') && (
            <Line type="monotone" dataKey="ma5" stroke="#ff7300" strokeWidth={1} dot={false} />
          )}
          {indicators.includes('ma10') && (
            <Line type="monotone" dataKey="ma10" stroke="#00ff00" strokeWidth={1} dot={false} />
          )}
          {indicators.includes('ma20') && (
            <Line type="monotone" dataKey="ma20" stroke="#0088fe" strokeWidth={1} dot={false} />
          )}
          {indicators.includes('ma50') && (
            <Line type="monotone" dataKey="ma50" stroke="#ff00ff" strokeWidth={1} dot={false} />
          )}
        </LineChart>
      </ResponsiveContainer>
    );
  };

  return (
    <Card 
      title="图表分析" 
      className={className}
      extra={
        <Space>
          <Select
            value={chartType}
            onChange={setChartType}
            size="small"
            style={{ width: 100 }}
          >
            <Option value="candlestick">
              <BarChartOutlined /> K线图
            </Option>
            <Option value="line">
              <LineChartOutlined /> 折线图
            </Option>
          </Select>
          
          <Select
            value={timeframe}
            onChange={setTimeframe}
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
            onClick={loadKlineData}
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
          style={{ marginBottom: 16 }}
        />
      )}

      {!selectedSymbol ? (
        <div style={{ textAlign: 'center', padding: '40px', color: '#8c8c8c' }}>
          <BarChartOutlined style={{ fontSize: '48px', marginBottom: '16px' }} />
          <div>请先选择交易对</div>
        </div>
      ) : loading ? (
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <Spin size="large" />
          <div style={{ marginTop: 16, color: '#8c8c8c' }}>加载图表数据中...</div>
        </div>
      ) : klineData.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px', color: '#8c8c8c' }}>
          <BarChartOutlined style={{ fontSize: '48px', marginBottom: '16px' }} />
          <div>暂无数据</div>
        </div>
      ) : (
        <div>
          {/* 指标选择 */}
          <div style={{ marginBottom: 16 }}>
            <Text strong style={{ marginRight: 8 }}>技术指标:</Text>
            <Select
              mode="multiple"
              value={indicators}
              onChange={setIndicators}
              size="small"
              style={{ width: 300 }}
              placeholder="选择技术指标"
            >
              {indicatorOptions.map(option => (
                <Option key={option.value} value={option.value}>
                  {option.label}
                </Option>
              ))}
            </Select>
          </div>

          {/* 图表 */}
          {chartType === 'candlestick' ? renderCandlestickChart() : renderLineChart()}

          {/* 图例 */}
          <div style={{ marginTop: 16, fontSize: '12px' }}>
            <Space wrap>
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <div style={{ width: '12px', height: '2px', background: '#1890ff', marginRight: '4px' }} />
                <Text>收盘价</Text>
              </div>
              {indicators.includes('ma5') && (
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  <div style={{ width: '12px', height: '2px', background: '#ff7300', marginRight: '4px' }} />
                  <Text>MA5</Text>
                </div>
              )}
              {indicators.includes('ma10') && (
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  <div style={{ width: '12px', height: '2px', background: '#00ff00', marginRight: '4px' }} />
                  <Text>MA10</Text>
                </div>
              )}
              {indicators.includes('ma20') && (
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  <div style={{ width: '12px', height: '2px', background: '#0088fe', marginRight: '4px' }} />
                  <Text>MA20</Text>
                </div>
              )}
              {indicators.includes('ma50') && (
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  <div style={{ width: '12px', height: '2px', background: '#ff00ff', marginRight: '4px' }} />
                  <Text>MA50</Text>
                </div>
              )}
            </Space>
          </div>
        </div>
      )}
    </Card>
  );
};

export default ChartPanel;
