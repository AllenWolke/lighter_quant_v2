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
  Select,
  Input,
  Alert,
  Spin
} from 'antd';
import { 
  CloseOutlined, 
  SearchOutlined,
  ReloadOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import { useTradingStore } from '../../store/tradingStore';
import { tradingApi } from '../../api';
import { Order } from '../../types';

const { Title, Text } = Typography;
const { Option } = Select;
const { Search } = Input;

interface OrderPanelProps {
  className?: string;
}

const OrderPanel: React.FC<OrderPanelProps> = ({ className }) => {
  const [loading, setLoading] = useState(false);
  const [cancelling, setCancelling] = useState<number | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [symbolFilter, setSymbolFilter] = useState<string>('');
  
  const { orders, updateOrders } = useTradingStore();

  // 加载订单数据
  const loadOrders = async () => {
    try {
      setLoading(true);
      const params: any = { limit: 20 };
      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }
      if (symbolFilter) {
        params.symbol = symbolFilter;
      }
      
      const data = await tradingApi.getOrders(params);
      updateOrders(data);
    } catch (error) {
      console.error('加载订单数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 取消订单
  const handleCancelOrder = async (orderId: number) => {
    try {
      setCancelling(orderId);
      await tradingApi.cancelOrder(orderId);
      await loadOrders(); // 重新加载数据
    } catch (error) {
      console.error('取消订单失败:', error);
    } finally {
      setCancelling(null);
    }
  };

  // 初始化加载
  useEffect(() => {
    loadOrders();
  }, [statusFilter, symbolFilter]);

  // 状态配置
  const statusConfig = {
    pending: { color: 'processing', text: '待成交', icon: <ClockCircleOutlined /> },
    partially_filled: { color: 'warning', text: '部分成交', icon: <ExclamationCircleOutlined /> },
    filled: { color: 'success', text: '已成交', icon: <CheckCircleOutlined /> },
    cancelled: { color: 'default', text: '已取消', icon: <CloseOutlined /> },
    rejected: { color: 'error', text: '已拒绝', icon: <ExclamationCircleOutlined /> },
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
        <Tag color={side === 'buy' ? 'green' : 'red'} style={{ fontSize: '10px' }}>
          {side === 'buy' ? '买' : '卖'}
        </Tag>
      ),
    },
    {
      title: '类型',
      dataIndex: 'orderType',
      key: 'orderType',
      width: 80,
      render: (type: string) => {
        const typeMap: Record<string, string> = {
          market: '市价',
          limit: '限价',
          stop_loss: '止损',
          take_profit: '止盈',
        };
        return (
          <Text style={{ fontSize: '12px' }}>{typeMap[type] || type}</Text>
        );
      },
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
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      width: 80,
      render: (price: number, record: Order) => (
        <Text style={{ fontSize: '12px' }}>
          {price ? `$${price.toFixed(2)}` : '市价'}
        </Text>
      ),
    },
    {
      title: '已成交',
      dataIndex: 'filledQuantity',
      key: 'filledQuantity',
      width: 80,
      render: (filled: number, record: Order) => {
        const safeFilled = filled || 0;
        const safeQuantity = record.quantity || 1;
        return (
          <div style={{ fontSize: '12px' }}>
            <div>{safeFilled.toFixed(4)}</div>
            <div style={{ color: '#8c8c8c', fontSize: '10px' }}>
              {((safeFilled / safeQuantity) * 100).toFixed(1)}%
            </div>
          </div>
        );
      },
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 80,
      render: (status: string) => {
        const config = statusConfig[status as keyof typeof statusConfig];
        return (
          <Tag color={config?.color} icon={config?.icon} style={{ fontSize: '10px' }}>
            {config?.text || status}
          </Tag>
        );
      },
    },
    {
      title: '时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      width: 100,
      render: (time: string) => (
        <Text style={{ fontSize: '12px' }}>
          {new Date(time).toLocaleTimeString()}
        </Text>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 60,
      render: (_: any, record: Order) => {
        const canCancel = ['pending', 'partially_filled'].includes(record.status);
        
        if (!canCancel) {
          return <Text style={{ fontSize: '12px', color: '#8c8c8c' }}>-</Text>;
        }
        
        return (
          <Popconfirm
            title="确定要取消这个订单吗？"
            onConfirm={() => handleCancelOrder(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="text"
              icon={<CloseOutlined />}
              size="small"
              loading={cancelling === record.id}
              danger
              style={{ fontSize: '12px' }}
            />
          </Popconfirm>
        );
      },
    },
  ];

  // 统计数据
  const stats = {
    total: orders.length,
    pending: orders.filter(o => o.status === 'pending').length,
    filled: orders.filter(o => o.status === 'filled').length,
    cancelled: orders.filter(o => o.status === 'cancelled').length,
  };

  return (
    <Card 
      title="订单管理" 
      size="small"
      className={className}
      extra={
        <Button
          type="text"
          icon={<ReloadOutlined />}
          onClick={loadOrders}
          loading={loading}
          size="small"
        />
      }
    >
      {/* 筛选器 */}
      <div style={{ marginBottom: 16 }}>
        <Space wrap>
          <Select
            value={statusFilter}
            onChange={setStatusFilter}
            size="small"
            style={{ width: 100 }}
          >
            <Option value="all">全部状态</Option>
            <Option value="pending">待成交</Option>
            <Option value="partially_filled">部分成交</Option>
            <Option value="filled">已成交</Option>
            <Option value="cancelled">已取消</Option>
            <Option value="rejected">已拒绝</Option>
          </Select>
          
          <Search
            placeholder="搜索交易对"
            value={symbolFilter}
            onChange={(e) => setSymbolFilter(e.target.value)}
            onSearch={setSymbolFilter}
            size="small"
            style={{ width: 120 }}
            allowClear
          />
        </Space>
      </div>

      {/* 统计信息 */}
      <div style={{ marginBottom: 12, padding: '8px 12px', background: '#f5f5f5', borderRadius: '4px' }}>
        <Space split={<span style={{ color: '#d9d9d9' }}>|</span>}>
          <Text style={{ fontSize: '12px' }}>总计: {stats.total}</Text>
          <Text style={{ fontSize: '12px', color: '#1890ff' }}>待成交: {stats.pending}</Text>
          <Text style={{ fontSize: '12px', color: '#52c41a' }}>已成交: {stats.filled}</Text>
          <Text style={{ fontSize: '12px', color: '#8c8c8c' }}>已取消: {stats.cancelled}</Text>
        </Space>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '20px' }}>
          <Spin size="small" />
          <div style={{ marginTop: 8, fontSize: '12px', color: '#8c8c8c' }}>
            加载中...
          </div>
        </div>
      ) : orders.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '20px', color: '#8c8c8c' }}>
          <ClockCircleOutlined style={{ fontSize: '24px', marginBottom: '8px' }} />
          <div>暂无订单</div>
        </div>
      ) : (
        <Table
          columns={columns}
          dataSource={orders}
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

export default OrderPanel;
