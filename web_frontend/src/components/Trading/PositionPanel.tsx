import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Table, 
  Tag, 
  Space, 
  Typography, 
  Button,
  Popconfirm,
  Tooltip,
  Progress,
  Alert,
  Row,
  Col,
  Spin
} from 'antd';
import { 
  CloseOutlined, 
  EditOutlined,
  WarningOutlined,
  DollarOutlined,
  RiseOutlined,
  FallOutlined
} from '@ant-design/icons';
import { useTradingStore } from '../../store/tradingStore';
import { positionApi } from '../../api';
import { Position } from '../../types';

const { Title, Text } = Typography;

interface PositionPanelProps {
  className?: string;
}

const PositionPanel: React.FC<PositionPanelProps> = ({ className }) => {
  const [loading, setLoading] = useState(false);
  const [closing, setClosing] = useState<number | null>(null);
  
  const { positions, updatePositions } = useTradingStore();

  // 加载持仓数据
  const loadPositions = async () => {
    try {
      setLoading(true);
      const data = await positionApi.getPositions({ isActive: true });
      updatePositions(data);
    } catch (error) {
      console.error('加载持仓数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 关闭持仓
  const handleClosePosition = async (positionId: number) => {
    try {
      setClosing(positionId);
      await positionApi.closePosition(positionId);
      await loadPositions(); // 重新加载数据
    } catch (error) {
      console.error('关闭持仓失败:', error);
    } finally {
      setClosing(null);
    }
  };

  // 初始化加载
  useEffect(() => {
    loadPositions();
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
        <Tag color={side === 'long' ? 'green' : 'red'} style={{ fontSize: '10px' }}>
          {side === 'long' ? '多' : '空'}
        </Tag>
      ),
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
      width: 80,
      render: (quantity: number) => (
        <Text style={{ fontSize: '12px' }}>{quantity ? quantity.toFixed(4) : '0.0000'}</Text>
      ),
    },
    {
      title: '入场价',
      dataIndex: 'entryPrice',
      key: 'entryPrice',
      width: 80,
      render: (price: number) => (
        <Text style={{ fontSize: '12px' }}>${price ? price.toFixed(2) : '0.00'}</Text>
      ),
    },
    {
      title: '当前价',
      dataIndex: 'currentPrice',
      key: 'currentPrice',
      width: 80,
      render: (price: number) => (
        <Text style={{ fontSize: '12px' }}>${price ? price.toFixed(2) : '0.00'}</Text>
      ),
    },
    {
      title: '盈亏',
      dataIndex: 'unrealizedPnl',
      key: 'unrealizedPnl',
      width: 80,
      render: (pnl: number) => {
        const safePnl = pnl || 0;
        const isPositive = safePnl >= 0;
        return (
          <Text 
            style={{ 
              fontSize: '12px',
              color: isPositive ? '#52c41a' : '#ff4d4f',
              fontWeight: '500'
            }}
          >
            {isPositive ? '+' : ''}${safePnl.toFixed(2)}
          </Text>
        );
      },
    },
    {
      title: '盈亏%',
      dataIndex: 'pnlRatio',
      key: 'pnlRatio',
      width: 70,
      render: (ratio: number) => {
        const safeRatio = ratio || 0;
        const isPositive = safeRatio >= 0;
        return (
          <Text 
            style={{ 
              fontSize: '12px',
              color: isPositive ? '#52c41a' : '#ff4d4f',
              fontWeight: '500'
            }}
          >
            {isPositive ? '+' : ''}{safeRatio.toFixed(2)}%
          </Text>
        );
      },
    },
    {
      title: '杠杆',
      dataIndex: 'leverage',
      key: 'leverage',
      width: 50,
      render: (leverage: number) => (
        <Text style={{ fontSize: '12px' }}>{leverage || 1}x</Text>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 80,
      render: (_: any, record: Position) => (
        <Space size="small">
          <Tooltip title="编辑止损止盈">
            <Button
              type="text"
              icon={<EditOutlined />}
              size="small"
              style={{ fontSize: '12px' }}
            />
          </Tooltip>
          <Popconfirm
            title="确定要关闭这个持仓吗？"
            onConfirm={() => handleClosePosition(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="text"
              icon={<CloseOutlined />}
              size="small"
              loading={closing === record.id}
              danger
              style={{ fontSize: '12px' }}
            />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <Card 
      title="持仓管理" 
      size="small"
      className={className}
      extra={
        <Button
          type="text"
          size="small"
          onClick={loadPositions}
          loading={loading}
        >
          刷新
        </Button>
      }
    >
      {/* 统计信息 */}
      <div style={{ marginBottom: 16 }}>
        <Row gutter={16}>
          <Col span={12}>
            <div style={{ textAlign: 'center', padding: '8px' }}>
              <Text type="secondary" style={{ fontSize: '12px' }}>持仓数量</Text>
              <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#1890ff' }}>
                {stats.totalPositions}
              </div>
            </div>
          </Col>
          <Col span={12}>
            <div style={{ textAlign: 'center', padding: '8px' }}>
              <Text type="secondary" style={{ fontSize: '12px' }}>未实现盈亏</Text>
              <div style={{ 
                fontSize: '16px', 
                fontWeight: 'bold',
                color: (stats.totalUnrealizedPnl || 0) >= 0 ? '#52c41a' : '#ff4d4f'
              }}>
                {(stats.totalUnrealizedPnl || 0) >= 0 ? '+' : ''}${(stats.totalUnrealizedPnl || 0).toFixed(2)}
              </div>
            </div>
          </Col>
        </Row>
        <Row gutter={16}>
          <Col span={12}>
            <div style={{ textAlign: 'center', padding: '8px' }}>
              <Text type="secondary" style={{ fontSize: '12px' }}>总保证金</Text>
              <div style={{ fontSize: '14px', fontWeight: 'bold' }}>
                ${(stats.totalMargin || 0).toFixed(2)}
              </div>
            </div>
          </Col>
          <Col span={12}>
            <div style={{ textAlign: 'center', padding: '8px' }}>
              <Text type="secondary" style={{ fontSize: '12px' }}>平均杠杆</Text>
              <div style={{ fontSize: '14px', fontWeight: 'bold' }}>
                {(stats.averageLeverage || 1).toFixed(1)}x
              </div>
            </div>
          </Col>
        </Row>
      </div>

      {/* 风险警告 */}
      {stats.averageLeverage > 5 && (
        <Alert
          message="高风险警告"
          description="平均杠杆过高，请注意风险控制"
          type="warning"
          icon={<WarningOutlined />}
          showIcon
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
      ) : positions.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '20px', color: '#8c8c8c' }}>
          <DollarOutlined style={{ fontSize: '24px', marginBottom: '8px' }} />
          <div>暂无持仓</div>
        </div>
      ) : (
        <Table
          columns={columns}
          dataSource={positions}
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

export default PositionPanel;
