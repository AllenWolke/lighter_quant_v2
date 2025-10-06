import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Table, 
  Tag, 
  Space, 
  Typography, 
  Button,
  Progress,
  Tooltip,
  Empty,
  Row,
  Col
} from 'antd';
import { 
  ReloadOutlined, 
  WarningOutlined,
  RiseOutlined,
  FallOutlined
} from '@ant-design/icons';
import { useTradingStore } from '../../store/tradingStore';
import { positionApi } from '../../api';
import { Position } from '../../types';

const { Title, Text } = Typography;

interface ActivePositionsProps {
  className?: string;
}

const ActivePositions: React.FC<ActivePositionsProps> = ({ className }) => {
  const [loading, setLoading] = useState(false);
  const [positions, setPositions] = useState<Position[]>([]);
  
  const { updatePositions } = useTradingStore();

  // 加载活跃持仓
  const loadActivePositions = async () => {
    try {
      setLoading(true);
      const data = await positionApi.getPositions({ isActive: true, limit: 5 });
      setPositions(data);
      updatePositions(data);
    } catch (error) {
      console.error('加载活跃持仓失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 初始化加载
  useEffect(() => {
    loadActivePositions();
  }, []);

  // 计算统计数据
  const stats = {
    totalPositions: positions.length,
    totalUnrealizedPnl: positions.reduce((sum, pos) => sum + pos.unrealizedPnl, 0),
    totalMargin: positions.reduce((sum, pos) => sum + pos.margin, 0),
    averageLeverage: positions.length > 0 
      ? positions.reduce((sum, pos) => sum + pos.leverage, 0) / positions.length 
      : 0,
  };

  // 表格列配置
  const columns = [
    {
      title: '交易对',
      dataIndex: 'symbol',
      key: 'symbol',
      width: 60,
      render: (symbol: string) => (
        <Text strong style={{ fontSize: '11px' }}>{symbol}</Text>
      ),
    },
    {
      title: '方向',
      dataIndex: 'side',
      key: 'side',
      width: 40,
      render: (side: string) => (
        <Tag 
          color={side === 'long' ? 'green' : 'red'} 
          style={{ fontSize: '9px', padding: '0 4px' }}
        >
          {side === 'long' ? '多' : '空'}
        </Tag>
      ),
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
      width: 60,
      render: (quantity: number) => (
        <Text style={{ fontSize: '11px' }}>{quantity.toFixed(2)}</Text>
      ),
    },
    {
      title: '价格',
      dataIndex: 'currentPrice',
      key: 'currentPrice',
      width: 60,
      render: (price: number) => (
        <Text style={{ fontSize: '11px' }}>${price.toFixed(0)}</Text>
      ),
    },
    {
      title: '盈亏',
      dataIndex: 'unrealizedPnl',
      key: 'unrealizedPnl',
      width: 60,
      render: (pnl: number) => {
        const isPositive = pnl >= 0;
        return (
          <Text 
            style={{ 
              fontSize: '11px',
              color: isPositive ? '#52c41a' : '#ff4d4f',
              fontWeight: '500'
            }}
          >
            {isPositive ? '+' : ''}${pnl.toFixed(0)}
          </Text>
        );
      },
    },
    {
      title: '杠杆',
      dataIndex: 'leverage',
      key: 'leverage',
      width: 40,
      render: (leverage: number) => (
        <Text style={{ fontSize: '11px' }}>{leverage}x</Text>
      ),
    },
  ];

  return (
    <Card 
      title="活跃持仓" 
      size="small"
      className={className}
      extra={
        <Button
          type="text"
          icon={<ReloadOutlined />}
          onClick={loadActivePositions}
          loading={loading}
          size="small"
        />
      }
    >
      {/* 统计信息 */}
      {positions.length > 0 && (
        <div style={{ marginBottom: 12, padding: '8px 12px', background: '#f5f5f5', borderRadius: '4px' }}>
          <Row gutter={8}>
            <Col span={8}>
              <div style={{ textAlign: 'center' }}>
                <Text style={{ fontSize: '10px', color: '#8c8c8c' }}>持仓数</Text>
                <div style={{ fontSize: '12px', fontWeight: 'bold', color: '#1890ff' }}>
                  {stats.totalPositions}
                </div>
              </div>
            </Col>
            <Col span={8}>
              <div style={{ textAlign: 'center' }}>
                <Text style={{ fontSize: '10px', color: '#8c8c8c' }}>未实现盈亏</Text>
                <div style={{ 
                  fontSize: '12px', 
                  fontWeight: 'bold',
                  color: stats.totalUnrealizedPnl >= 0 ? '#52c41a' : '#ff4d4f'
                }}>
                  {stats.totalUnrealizedPnl >= 0 ? '+' : ''}${stats.totalUnrealizedPnl.toFixed(0)}
                </div>
              </div>
            </Col>
            <Col span={8}>
              <div style={{ textAlign: 'center' }}>
                <Text style={{ fontSize: '10px', color: '#8c8c8c' }}>平均杠杆</Text>
                <div style={{ fontSize: '12px', fontWeight: 'bold' }}>
                  {stats.averageLeverage.toFixed(1)}x
                </div>
              </div>
            </Col>
          </Row>
        </div>
      )}

      {/* 风险警告 */}
      {stats.averageLeverage > 5 && (
        <div style={{ marginBottom: 12 }}>
          <Tooltip title="平均杠杆过高，请注意风险控制">
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              padding: '4px 8px', 
              background: '#fff7e6', 
              borderRadius: '4px',
              fontSize: '10px',
              color: '#fa8c16'
            }}>
              <WarningOutlined style={{ marginRight: '4px' }} />
              高风险
            </div>
          </Tooltip>
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '20px' }}>
          <div style={{ fontSize: '12px', color: '#8c8c8c' }}>加载中...</div>
        </div>
      ) : positions.length === 0 ? (
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description="暂无活跃持仓"
          style={{ padding: '20px 0' }}
        />
      ) : (
        <Table
          columns={columns}
          dataSource={positions}
          pagination={false}
          size="small"
          scroll={{ y: 150 }}
          rowKey="id"
          style={{ fontSize: '11px' }}
        />
      )}
    </Card>
  );
};

export default ActivePositions;
