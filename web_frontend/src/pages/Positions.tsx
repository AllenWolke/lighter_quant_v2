import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Table, 
  Button, 
  Space, 
  Typography, 
  Tag,
  Popconfirm,
  Modal,
  Form,
  InputNumber,
  message,
  Row,
  Col,
  Statistic,
  Progress,
  Tooltip,
  Select,
  DatePicker,
  Alert
} from 'antd';
import { 
  CloseOutlined, 
  EditOutlined,
  ReloadOutlined,
  WarningOutlined,
  DollarOutlined,
  BarChartOutlined
} from '@ant-design/icons';
import { useTradingStore } from '../store/tradingStore';
import { positionApi } from '../api';
import { Position } from '../types';

const { Title, Text } = Typography;
const { Option } = Select;
const { RangePicker } = DatePicker;

const Positions: React.FC = () => {
  const [positions, setPositions] = useState<Position[]>([]);
  const [loading, setLoading] = useState(false);
  const [closing, setClosing] = useState<number | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingPosition, setEditingPosition] = useState<Position | null>(null);
  const [form] = Form.useForm();
  const [filters, setFilters] = useState({
    symbol: '',
    isActive: undefined as boolean | undefined,
  });

  // 加载持仓数据
  const loadPositions = async () => {
    try {
      setLoading(true);
      const params: any = {};
      if (filters.symbol) params.symbol = filters.symbol;
      if (filters.isActive !== undefined) params.isActive = filters.isActive;
      
      const data = await positionApi.getPositions(params);
      setPositions(data);
    } catch (error) {
      console.error('加载持仓失败:', error);
      message.error('加载持仓失败');
    } finally {
      setLoading(false);
    }
  };

  // 初始化加载
  useEffect(() => {
    loadPositions();
  }, [filters]);

  // 关闭持仓
  const handleClosePosition = async (positionId: number) => {
    try {
      setClosing(positionId);
      await positionApi.closePosition(positionId);
      message.success('持仓已关闭');
      loadPositions();
    } catch (error) {
      console.error('关闭持仓失败:', error);
      message.error('关闭持仓失败');
    } finally {
      setClosing(null);
    }
  };

  // 批量关闭持仓
  const handleCloseAllPositions = async () => {
    try {
      await positionApi.closeAllPositions();
      message.success('所有持仓已关闭');
      loadPositions();
    } catch (error) {
      console.error('批量关闭持仓失败:', error);
      message.error('批量关闭持仓失败');
    }
  };

  // 更新止损止盈
  const handleUpdateStopLoss = async (values: { stopLossPrice: number }) => {
    if (!editingPosition) return;
    
    try {
      await positionApi.updateStopLoss(editingPosition.id, values.stopLossPrice);
      message.success('止损价格已更新');
      setModalVisible(false);
      setEditingPosition(null);
      form.resetFields();
      loadPositions();
    } catch (error) {
      console.error('更新止损价格失败:', error);
      message.error('更新止损价格失败');
    }
  };

  // 更新止盈价格
  const handleUpdateTakeProfit = async (values: { takeProfitPrice: number }) => {
    if (!editingPosition) return;
    
    try {
      await positionApi.updateTakeProfit(editingPosition.id, values.takeProfitPrice);
      message.success('止盈价格已更新');
      setModalVisible(false);
      setEditingPosition(null);
      form.resetFields();
      loadPositions();
    } catch (error) {
      console.error('更新止盈价格失败:', error);
      message.error('更新止盈价格失败');
    }
  };

  // 打开编辑模态框
  const openEditModal = (position: Position) => {
    setEditingPosition(position);
    form.setFieldsValue({
      stopLossPrice: position.stopLossPrice,
      takeProfitPrice: position.takeProfitPrice,
    });
    setModalVisible(true);
  };

  // 关闭模态框
  const closeModal = () => {
    setModalVisible(false);
    setEditingPosition(null);
    form.resetFields();
  };

  // 表格列配置
  const columns = [
    {
      title: '交易对',
      dataIndex: 'symbol',
      key: 'symbol',
      width: 100,
      render: (symbol: string) => (
        <Text strong>{symbol}</Text>
      ),
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
      render: (quantity: number) => (
        <Text>{quantity.toFixed(4)}</Text>
      ),
    },
    {
      title: '入场价',
      dataIndex: 'entryPrice',
      key: 'entryPrice',
      width: 100,
      render: (price: number) => (
        <Text>${price.toFixed(2)}</Text>
      ),
    },
    {
      title: '当前价',
      dataIndex: 'currentPrice',
      key: 'currentPrice',
      width: 100,
      render: (price: number) => (
        <Text>${price.toFixed(2)}</Text>
      ),
    },
    {
      title: '未实现盈亏',
      dataIndex: 'unrealizedPnl',
      key: 'unrealizedPnl',
      width: 120,
      render: (pnl: number, record: Position) => (
        <div>
          <Text 
            style={{ 
              color: pnl >= 0 ? '#52c41a' : '#ff4d4f',
              fontWeight: 'bold'
            }}
          >
            {pnl >= 0 ? '+' : ''}${pnl.toFixed(2)}
          </Text>
          <div style={{ fontSize: '12px', color: '#8c8c8c' }}>
            {record.pnlRatio >= 0 ? '+' : ''}{record.pnlRatio.toFixed(2)}%
          </div>
        </div>
      ),
    },
    {
      title: '杠杆',
      dataIndex: 'leverage',
      key: 'leverage',
      width: 80,
      render: (leverage: number) => (
        <Text>{leverage}x</Text>
      ),
    },
    {
      title: '保证金',
      dataIndex: 'margin',
      key: 'margin',
      width: 100,
      render: (margin: number) => (
        <Text>${margin.toFixed(2)}</Text>
      ),
    },
    {
      title: '止损/止盈',
      key: 'stopLossTakeProfit',
      width: 120,
      render: (_: any, record: Position) => (
        <div style={{ fontSize: '12px' }}>
          {record.stopLossPrice && (
            <div>止损: ${record.stopLossPrice.toFixed(2)}</div>
          )}
          {record.takeProfitPrice && (
            <div>止盈: ${record.takeProfitPrice.toFixed(2)}</div>
          )}
          {!record.stopLossPrice && !record.takeProfitPrice && (
            <Text type="secondary">未设置</Text>
          )}
        </div>
      ),
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
      title: '操作',
      key: 'action',
      width: 120,
      render: (_: any, record: Position) => (
        <Space>
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => openEditModal(record)}
            size="small"
          />
          {record.isActive && (
            <Popconfirm
              title="确定要关闭这个持仓吗？"
              onConfirm={() => handleClosePosition(record.id)}
              okText="确定"
              cancelText="取消"
            >
              <Button
                type="text"
                icon={<CloseOutlined />}
                loading={closing === record.id}
                danger
                size="small"
              />
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ];

  // 计算统计信息
  const stats = {
    totalPositions: positions.length,
    activePositions: positions.filter(p => p.isActive).length,
    totalUnrealizedPnl: positions.reduce((sum, p) => sum + p.unrealizedPnl, 0),
    totalMargin: positions.reduce((sum, p) => sum + p.margin, 0),
    averageLeverage: positions.length > 0 
      ? positions.reduce((sum, p) => sum + p.leverage, 0) / positions.length 
      : 0,
    maxDrawdown: Math.min(...positions.map(p => p.unrealizedPnl), 0),
  };

  return (
    <div className="page-content">
      {/* 页面头部 */}
      <div className="page-header">
        <div>
          <Title level={2} style={{ margin: 0 }}>持仓管理</Title>
          <Text type="secondary">查看和管理您的交易持仓</Text>
        </div>
        <Space>
          <Button
            icon={<ReloadOutlined />}
            onClick={loadPositions}
            loading={loading}
          >
            刷新
          </Button>
          {positions.filter(p => p.isActive).length > 0 && (
            <Popconfirm
              title="确定要关闭所有活跃持仓吗？"
              onConfirm={handleCloseAllPositions}
              okText="确定"
              cancelText="取消"
            >
              <Button danger>
                关闭所有持仓
              </Button>
            </Popconfirm>
          )}
        </Space>
      </div>

      {/* 统计卡片 */}
      <Row gutter={[24, 24]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总持仓数"
              value={stats.totalPositions}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="活跃持仓"
              value={stats.activePositions}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="未实现盈亏"
              value={stats.totalUnrealizedPnl}
              precision={2}
              prefix="$"
              valueStyle={{ color: stats.totalUnrealizedPnl >= 0 ? '#52c41a' : '#ff4d4f' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总保证金"
              value={stats.totalMargin}
              precision={2}
              prefix="$"
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
      </Row>

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
            <Select
              placeholder="选择状态"
              value={filters.isActive}
              onChange={(value) => setFilters({ ...filters, isActive: value })}
              style={{ width: '100%' }}
              allowClear
            >
              <Option value={true}>活跃</Option>
              <Option value={false}>已关闭</Option>
            </Select>
          </Col>
          <Col span={12}>
            <Space>
              <Button onClick={() => setFilters({ symbol: '', isActive: undefined })}>
                重置筛选
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 风险警告 */}
      {stats.averageLeverage > 5 && (
        <Alert
          message="高风险警告"
          description={`平均杠杆为 ${stats.averageLeverage.toFixed(1)}x，建议降低杠杆以控制风险`}
          type="warning"
          icon={<WarningOutlined />}
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      {/* 持仓列表 */}
      <Card>
        <Table
          columns={columns}
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
      </Card>

      {/* 编辑止损止盈模态框 */}
      <Modal
        title="设置止损止盈"
        open={modalVisible}
        onCancel={closeModal}
        onOk={() => form.submit()}
        width={400}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleUpdateStopLoss}
        >
          <Form.Item
            name="stopLossPrice"
            label="止损价格"
            rules={[{ required: true, message: '请输入止损价格' }]}
          >
            <InputNumber
              placeholder="请输入止损价格"
              style={{ width: '100%' }}
              precision={2}
              min={0}
            />
          </Form.Item>

          <Form.Item
            name="takeProfitPrice"
            label="止盈价格"
            rules={[{ required: true, message: '请输入止盈价格' }]}
          >
            <InputNumber
              placeholder="请输入止盈价格"
              style={{ width: '100%' }}
              precision={2}
              min={0}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Positions;
