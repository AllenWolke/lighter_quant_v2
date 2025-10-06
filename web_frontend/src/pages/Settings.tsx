import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Form, 
  Input, 
  Button, 
  Space, 
  Typography, 
  Switch,
  Select,
  InputNumber,
  Divider,
  message,
  Row,
  Col,
  Tabs,
  Alert
} from 'antd';
import { 
  SaveOutlined, 
  ReloadOutlined,
  UserOutlined,
  SettingOutlined,
  BellOutlined,
  SecurityScanOutlined
} from '@ant-design/icons';
import { useAuthStore } from '../store/authStore';
import { authApi, notificationApi } from '../api';

const { Title, Text } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;

const Settings: React.FC = () => {
  const [form] = Form.useForm();
  const [notificationForm] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [notificationSettings, setNotificationSettings] = useState<any>(null);
  
  const { user, updateUser } = useAuthStore();

  // 加载用户设置
  const loadSettings = async () => {
    try {
      setLoading(true);
      
      // 加载通知设置
      const notificationData = await notificationApi.getSettings();
      setNotificationSettings(notificationData);
      notificationForm.setFieldsValue(notificationData);
      
      // 设置用户信息表单
      form.setFieldsValue({
        username: user?.username,
        email: user?.email,
        fullName: user?.fullName,
      });
    } catch (error) {
      console.error('加载设置失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 初始化加载
  useEffect(() => {
    loadSettings();
  }, [user]);

  // 保存用户信息
  const handleSaveProfile = async (values: any) => {
    try {
      setLoading(true);
      const updatedUser = await authApi.updateUser(values);
      updateUser(updatedUser);
      message.success('个人信息更新成功');
    } catch (error) {
      console.error('更新个人信息失败:', error);
      message.error('更新个人信息失败');
    } finally {
      setLoading(false);
    }
  };

  // 修改密码
  const handleChangePassword = async (values: any) => {
    try {
      setLoading(true);
      await authApi.changePassword(values);
      message.success('密码修改成功');
      form.resetFields(['currentPassword', 'newPassword', 'confirmPassword']);
    } catch (error) {
      console.error('修改密码失败:', error);
      message.error('修改密码失败');
    } finally {
      setLoading(false);
    }
  };

  // 保存通知设置
  const handleSaveNotifications = async (values: any) => {
    try {
      setLoading(true);
      await notificationApi.updateSettings(values);
      message.success('通知设置更新成功');
    } catch (error) {
      console.error('更新通知设置失败:', error);
      message.error('更新通知设置失败');
    } finally {
      setLoading(false);
    }
  };

  // 测试通知
  const handleTestNotification = async () => {
    try {
      await notificationApi.testNotification('system_error', 'info');
      message.success('测试通知已发送');
    } catch (error) {
      console.error('发送测试通知失败:', error);
      message.error('发送测试通知失败');
    }
  };

  return (
    <div className="page-content">
      {/* 页面头部 */}
      <div className="page-header">
        <div>
          <Title level={2} style={{ margin: 0 }}>系统设置</Title>
          <Text type="secondary">管理您的账户设置和系统偏好</Text>
        </div>
        <Button
          icon={<ReloadOutlined />}
          onClick={loadSettings}
          loading={loading}
        >
          刷新
        </Button>
      </div>

      <Tabs defaultActiveKey="profile" type="card">
        {/* 个人信息 */}
        <TabPane 
          tab={
            <span>
              <UserOutlined />
              个人信息
            </span>
          } 
          key="profile"
        >
          <Row gutter={24}>
            <Col xs={24} lg={16}>
              <Card title="基本信息">
                <Form
                  form={form}
                  layout="vertical"
                  onFinish={handleSaveProfile}
                >
                  <Row gutter={16}>
                    <Col span={12}>
                      <Form.Item
                        name="username"
                        label="用户名"
                        rules={[
                          { required: true, message: '请输入用户名' },
                          { min: 3, message: '用户名至少3个字符' }
                        ]}
                      >
                        <Input placeholder="请输入用户名" />
                      </Form.Item>
                    </Col>
                    <Col span={12}>
                      <Form.Item
                        name="email"
                        label="邮箱"
                        rules={[
                          { required: true, message: '请输入邮箱' },
                          { type: 'email', message: '请输入有效的邮箱地址' }
                        ]}
                      >
                        <Input placeholder="请输入邮箱" />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Form.Item
                    name="fullName"
                    label="姓名"
                  >
                    <Input placeholder="请输入姓名" />
                  </Form.Item>

                  <Form.Item>
                    <Button
                      type="primary"
                      htmlType="submit"
                      icon={<SaveOutlined />}
                      loading={loading}
                    >
                      保存个人信息
                    </Button>
                  </Form.Item>
                </Form>
              </Card>
            </Col>

            <Col xs={24} lg={8}>
              <Card title="账户信息">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div>
                    <Text type="secondary">用户ID</Text>
                    <div>{user?.id}</div>
                  </div>
                  <div>
                    <Text type="secondary">注册时间</Text>
                    <div>{user?.createdAt ? new Date(user.createdAt).toLocaleString() : '-'}</div>
                  </div>
                  <div>
                    <Text type="secondary">最后登录</Text>
                    <div>{user?.lastLogin ? new Date(user.lastLogin).toLocaleString() : '-'}</div>
                  </div>
                  <div>
                    <Text type="secondary">账户状态</Text>
                    <div>
                      <span style={{ color: user?.isActive ? '#52c41a' : '#ff4d4f' }}>
                        {user?.isActive ? '正常' : '已禁用'}
                      </span>
                    </div>
                  </div>
                </Space>
              </Card>
            </Col>
          </Row>
        </TabPane>

        {/* 安全设置 */}
        <TabPane 
          tab={
            <span>
              <SecurityScanOutlined />
              安全设置
            </span>
          } 
          key="security"
        >
          <Row gutter={24}>
            <Col xs={24} lg={16}>
              <Card title="修改密码">
                <Form
                  layout="vertical"
                  onFinish={handleChangePassword}
                >
                  <Form.Item
                    name="currentPassword"
                    label="当前密码"
                    rules={[{ required: true, message: '请输入当前密码' }]}
                  >
                    <Input.Password placeholder="请输入当前密码" />
                  </Form.Item>

                  <Form.Item
                    name="newPassword"
                    label="新密码"
                    rules={[
                      { required: true, message: '请输入新密码' },
                      { min: 6, message: '密码至少6个字符' }
                    ]}
                  >
                    <Input.Password placeholder="请输入新密码" />
                  </Form.Item>

                  <Form.Item
                    name="confirmPassword"
                    label="确认新密码"
                    dependencies={['newPassword']}
                    rules={[
                      { required: true, message: '请确认新密码' },
                      ({ getFieldValue }) => ({
                        validator(_, value) {
                          if (!value || getFieldValue('newPassword') === value) {
                            return Promise.resolve();
                          }
                          return Promise.reject(new Error('两次输入的密码不一致'));
                        },
                      }),
                    ]}
                  >
                    <Input.Password placeholder="请再次输入新密码" />
                  </Form.Item>

                  <Form.Item>
                    <Button
                      type="primary"
                      htmlType="submit"
                      icon={<SaveOutlined />}
                      loading={loading}
                    >
                      修改密码
                    </Button>
                  </Form.Item>
                </Form>
              </Card>
            </Col>

            <Col xs={24} lg={8}>
              <Card title="安全提示">
                <Alert
                  message="密码安全建议"
                  description={
                    <ul style={{ margin: 0, paddingLeft: '20px' }}>
                      <li>使用至少8个字符的密码</li>
                      <li>包含大小写字母、数字和特殊字符</li>
                      <li>定期更换密码</li>
                      <li>不要使用个人信息作为密码</li>
                    </ul>
                  }
                  type="info"
                  showIcon
                />
              </Card>
            </Col>
          </Row>
        </TabPane>

        {/* 通知设置 */}
        <TabPane 
          tab={
            <span>
              <BellOutlined />
              通知设置
            </span>
          } 
          key="notifications"
        >
          <Row gutter={24}>
            <Col xs={24} lg={16}>
              <Card title="通知偏好">
                <Form
                  form={notificationForm}
                  layout="vertical"
                  onFinish={handleSaveNotifications}
                >
                  <Row gutter={16}>
                    <Col span={12}>
                      <Form.Item
                        name="emailEnabled"
                        label="邮件通知"
                        valuePropName="checked"
                      >
                        <Switch />
                      </Form.Item>
                    </Col>
                    <Col span={12}>
                      <Form.Item
                        name="pushEnabled"
                        label="推送通知"
                        valuePropName="checked"
                      >
                        <Switch />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Form.Item
                    name="types"
                    label="通知类型"
                  >
                    <Select
                      mode="multiple"
                      placeholder="选择要接收的通知类型"
                      style={{ width: '100%' }}
                    >
                      <Option value="trade_executed">交易执行</Option>
                      <Option value="stop_loss">止损触发</Option>
                      <Option value="take_profit">止盈触发</Option>
                      <Option value="system_error">系统错误</Option>
                      <Option value="risk_limit">风险限制</Option>
                    </Select>
                  </Form.Item>

                  <Form.Item
                    name="levels"
                    label="通知级别"
                  >
                    <Select
                      mode="multiple"
                      placeholder="选择要接收的通知级别"
                      style={{ width: '100%' }}
                    >
                      <Option value="info">信息</Option>
                      <Option value="warning">警告</Option>
                      <Option value="error">错误</Option>
                      <Option value="critical">严重</Option>
                    </Select>
                  </Form.Item>

                  <Divider>免打扰时间</Divider>

                  <Row gutter={16}>
                    <Col span={8}>
                      <Form.Item
                        name={['quietHours', 'enabled']}
                        label="启用免打扰"
                        valuePropName="checked"
                      >
                        <Switch />
                      </Form.Item>
                    </Col>
                    <Col span={8}>
                      <Form.Item
                        name={['quietHours', 'start']}
                        label="开始时间"
                      >
                        <Input placeholder="22:00" />
                      </Form.Item>
                    </Col>
                    <Col span={8}>
                      <Form.Item
                        name={['quietHours', 'end']}
                        label="结束时间"
                      >
                        <Input placeholder="08:00" />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Form.Item>
                    <Space>
                      <Button
                        type="primary"
                        htmlType="submit"
                        icon={<SaveOutlined />}
                        loading={loading}
                      >
                        保存设置
                      </Button>
                      <Button
                        onClick={handleTestNotification}
                        loading={loading}
                      >
                        发送测试通知
                      </Button>
                    </Space>
                  </Form.Item>
                </Form>
              </Card>
            </Col>

            <Col xs={24} lg={8}>
              <Card title="通知统计">
                {notificationSettings && (
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <div>
                      <Text type="secondary">总通知数</Text>
                      <div style={{ fontSize: '18px', fontWeight: 'bold' }}>
                        {notificationSettings.totalNotifications || 0}
                      </div>
                    </div>
                    <div>
                      <Text type="secondary">未读通知</Text>
                      <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#1890ff' }}>
                        {notificationSettings.unreadNotifications || 0}
                      </div>
                    </div>
                    <div>
                      <Text type="secondary">今日通知</Text>
                      <div style={{ fontSize: '18px', fontWeight: 'bold' }}>
                        {notificationSettings.todayNotifications || 0}
                      </div>
                    </div>
                  </Space>
                )}
              </Card>
            </Col>
          </Row>
        </TabPane>

        {/* 交易设置 */}
        <TabPane 
          tab={
            <span>
              <SettingOutlined />
              交易设置
            </span>
          } 
          key="trading"
        >
          <Card title="交易偏好">
            <Alert
              message="交易设置"
              description="这些设置将影响您的交易行为和风险控制"
              type="info"
              showIcon
              style={{ marginBottom: 24 }}
            />
            
            <Form layout="vertical">
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    name="maxPositionSize"
                    label="最大持仓量 (USDT)"
                    initialValue={1000}
                  >
                    <InputNumber
                      style={{ width: '100%' }}
                      min={0}
                      step={100}
                      placeholder="请输入最大持仓量"
                    />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    name="maxLeverage"
                    label="最大杠杆倍数"
                    initialValue={5}
                  >
                    <InputNumber
                      style={{ width: '100%' }}
                      min={1}
                      max={10}
                      step={0.1}
                      placeholder="请输入最大杠杆倍数"
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    name="stopLossPercent"
                    label="默认止损百分比"
                    initialValue={2}
                  >
                    <InputNumber
                      style={{ width: '100%' }}
                      min={0}
                      max={100}
                      step={0.1}
                      placeholder="请输入止损百分比"
                      addonAfter="%"
                    />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    name="takeProfitPercent"
                    label="默认止盈百分比"
                    initialValue={4}
                  >
                    <InputNumber
                      style={{ width: '100%' }}
                      min={0}
                      max={1000}
                      step={0.1}
                      placeholder="请输入止盈百分比"
                      addonAfter="%"
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item>
                <Button
                  type="primary"
                  icon={<SaveOutlined />}
                  loading={loading}
                >
                  保存交易设置
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </TabPane>
      </Tabs>
    </div>
  );
};

export default Settings;
