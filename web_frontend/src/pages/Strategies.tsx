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
  Input,
  Select,
  Switch,
  message,
  Row,
  Col,
  Statistic,
  Progress,
  Tooltip
} from 'antd';
import { 
  PlusOutlined, 
  EditOutlined, 
  DeleteOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  SettingOutlined,
  BarChartOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { useTradingStore } from '../store/tradingStore';
import { strategyApi } from '../api';
import { Strategy, StrategyCreateRequest, StrategyUpdateRequest } from '../types';

const { Title, Text } = Typography;
const { Option } = Select;

const Strategies: React.FC = () => {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingStrategy, setEditingStrategy] = useState<Strategy | null>(null);
  const [form] = Form.useForm();

  // 加载策略列表
  const loadStrategies = async () => {
    try {
      setLoading(true);
      const data = await strategyApi.getStrategies();
      setStrategies(data);
    } catch (error) {
      console.error('加载策略失败:', error);
      message.error('加载策略失败');
    } finally {
      setLoading(false);
    }
  };

  // 初始化加载
  useEffect(() => {
    loadStrategies();
  }, []);

  // 创建/更新策略
  const handleSubmit = async (values: StrategyCreateRequest | StrategyUpdateRequest) => {
    try {
      if (editingStrategy) {
        await strategyApi.updateStrategy(editingStrategy.id, values);
        message.success('策略更新成功');
      } else {
        await strategyApi.createStrategy(values as StrategyCreateRequest);
        message.success('策略创建成功');
      }
      
      setModalVisible(false);
      setEditingStrategy(null);
      form.resetFields();
      loadStrategies();
    } catch (error) {
      console.error('保存策略失败:', error);
      message.error('保存策略失败');
    }
  };

  // 删除策略
  const handleDelete = async (id: number) => {
    try {
      await strategyApi.deleteStrategy(id);
      message.success('策略删除成功');
      loadStrategies();
    } catch (error) {
      console.error('删除策略失败:', error);
      message.error('删除策略失败');
    }
  };

  // 切换策略状态
  const handleToggleStrategy = async (id: number, enabled: boolean) => {
    try {
      await strategyApi.toggleStrategy(id, enabled);
      message.success(`策略已${enabled ? '启用' : '禁用'}`);
      loadStrategies();
    } catch (error) {
      console.error('切换策略状态失败:', error);
      message.error('切换策略状态失败');
    }
  };

  // 打开编辑模态框
  const openEditModal = (strategy: Strategy) => {
    setEditingStrategy(strategy);
    form.setFieldsValue({
      name: strategy.name,
      strategyType: strategy.strategyType,
      description: strategy.description,
      isActive: strategy.isActive,
      isEnabled: strategy.isEnabled,
    });
    setModalVisible(true);
  };

  // 打开创建模态框
  const openCreateModal = () => {
    setEditingStrategy(null);
    form.resetFields();
    setModalVisible(true);
  };

  // 关闭模态框
  const closeModal = () => {
    setModalVisible(false);
    setEditingStrategy(null);
    form.resetFields();
  };

  // 表格列配置
  const columns = [
    {
      title: '策略名称',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, record: Strategy) => (
        <div>
          <Text strong>{name}</Text>
          <div style={{ fontSize: '12px', color: '#8c8c8c' }}>
            {record.description}
          </div>
        </div>
      ),
    },
    {
      title: '类型',
      dataIndex: 'strategyType',
      key: 'strategyType',
      width: 120,
      render: (type: string) => {
        const typeMap: Record<string, { color: string; text: string }> = {
          ut_bot: { color: 'blue', text: 'UT Bot' },
          mean_reversion: { color: 'green', text: '均值回归' },
          momentum: { color: 'orange', text: '动量策略' },
          arbitrage: { color: 'purple', text: '套利策略' },
          custom: { color: 'default', text: '自定义' },
        };
        const config = typeMap[type] || { color: 'default', text: type };
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    {
      title: '状态',
      dataIndex: 'isActive',
      key: 'isActive',
      width: 100,
      render: (isActive: boolean, record: Strategy) => (
        <Space direction="vertical" size="small">
          <Tag color={isActive ? 'green' : 'default'}>
            {isActive ? '运行中' : '已停止'}
          </Tag>
          <Tag color={record.isEnabled ? 'blue' : 'default'}>
            {record.isEnabled ? '已启用' : '已禁用'}
          </Tag>
        </Space>
      ),
    },
    {
      title: '统计信息',
      key: 'stats',
      width: 200,
      render: (_: any, record: Strategy) => (
        <div style={{ fontSize: '12px' }}>
          <div>总交易: {record.totalTrades}</div>
          <div>胜率: {record.winningTrades > 0 ? ((record.winningTrades / record.totalTrades) * 100).toFixed(1) : 0}%</div>
          <div>总盈亏: 
            <Text style={{ color: record.totalPnl >= 0 ? '#52c41a' : '#ff4d4f' }}>
              {record.totalPnl >= 0 ? '+' : ''}${record.totalPnl.toFixed(2)}
            </Text>
          </div>
        </div>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_: any, record: Strategy) => (
        <Space>
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => openEditModal(record)}
            size="small"
          />
          <Button
            type="text"
            icon={record.isActive ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
            onClick={() => handleToggleStrategy(record.id, !record.isActive)}
            size="small"
          />
          <Popconfirm
            title="确定要删除这个策略吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="text"
              icon={<DeleteOutlined />}
              danger
              size="small"
            />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // 计算统计信息
  const stats = {
    totalStrategies: strategies.length,
    activeStrategies: strategies.filter(s => s.isActive).length,
    enabledStrategies: strategies.filter(s => s.isEnabled).length,
    totalPnl: strategies.reduce((sum, s) => sum + s.totalPnl, 0),
    averageWinRate: strategies.length > 0 
      ? strategies.reduce((sum, s) => sum + (s.winningTrades / Math.max(s.totalTrades, 1)) * 100, 0) / strategies.length 
      : 0,
  };

  return (
    <div className="page-content">
      {/* 页面头部 */}
      <div className="page-header">
        <div>
          <Title level={2} style={{ margin: 0 }}>策略管理</Title>
          <Text type="secondary">管理和配置您的量化交易策略</Text>
        </div>
        <Space>
          <Button
            icon={<ReloadOutlined />}
            onClick={loadStrategies}
            loading={loading}
          >
            刷新
          </Button>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={openCreateModal}
          >
            创建策略
          </Button>
        </Space>
      </div>

      {/* 统计卡片 */}
      <Row gutter={[24, 24]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总策略数"
              value={stats.totalStrategies}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="运行中"
              value={stats.activeStrategies}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总盈亏"
              value={stats.totalPnl}
              precision={2}
              prefix="$"
              valueStyle={{ color: stats.totalPnl >= 0 ? '#52c41a' : '#ff4d4f' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="平均胜率"
              value={stats.averageWinRate}
              precision={1}
              suffix="%"
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 策略列表 */}
      <Card>
        <Table
          columns={columns}
          dataSource={strategies}
          loading={loading}
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
          }}
        />
      </Card>

      {/* 创建/编辑策略模态框 */}
      <Modal
        title={editingStrategy ? '编辑策略' : '创建策略'}
        open={modalVisible}
        onCancel={closeModal}
        onOk={() => form.submit()}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="name"
            label="策略名称"
            rules={[{ required: true, message: '请输入策略名称' }]}
          >
            <Input placeholder="请输入策略名称" />
          </Form.Item>

          <Form.Item
            name="strategyType"
            label="策略类型"
            rules={[{ required: true, message: '请选择策略类型' }]}
          >
            <Select placeholder="请选择策略类型">
              <Option value="ut_bot">UT Bot策略</Option>
              <Option value="mean_reversion">均值回归策略</Option>
              <Option value="momentum">动量策略</Option>
              <Option value="arbitrage">套利策略</Option>
              <Option value="custom">自定义策略</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="description"
            label="策略描述"
          >
            <Input.TextArea 
              placeholder="请输入策略描述"
              rows={3}
            />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="isActive"
                label="是否运行"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="isEnabled"
                label="是否启用"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  );
};

export default Strategies;
