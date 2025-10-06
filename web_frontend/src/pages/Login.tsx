import React, { useState, useEffect } from 'react';
import { 
  Form, 
  Input, 
  Button, 
  Card, 
  Typography, 
  Space, 
  Alert,
  Divider,
  Row,
  Col
} from 'antd';
import { 
  UserOutlined, 
  LockOutlined, 
  MailOutlined,
  EyeInvisibleOutlined,
  EyeTwoTone
} from '@ant-design/icons';
import { useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { LoginRequest, RegisterRequest } from '../types';

const { Title, Text } = Typography;

const Login: React.FC = () => {
  const [form] = Form.useForm();
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const navigate = useNavigate();
  const { login, register, isAuthenticated, isLoading } = useAuthStore();

  // 如果已登录，重定向到仪表板
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (values: LoginRequest | RegisterRequest) => {
    try {
      setLoading(true);
      setError(null);

      let success = false;
      if (isLogin) {
        success = await login(values as LoginRequest);
      } else {
        success = await register(values as RegisterRequest);
      }

      if (success) {
        navigate('/dashboard');
      } else {
        setError(isLogin ? '登录失败，请检查用户名和密码' : '注册失败，请检查输入信息');
      }
    } catch (error) {
      console.error('认证错误:', error);
      setError('网络错误，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
    setError(null);
    form.resetFields();
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px'
    }}>
      <Row justify="center" style={{ width: '100%', maxWidth: '1200px' }}>
        <Col xs={24} sm={20} md={16} lg={12} xl={10}>
          <Card
            style={{
              borderRadius: '12px',
              boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
              border: 'none'
            }}
          >
            <div style={{ textAlign: 'center', marginBottom: '32px' }}>
              <Title level={2} style={{ color: '#1890ff', marginBottom: '8px' }}>
                Lighter量化交易系统
              </Title>
              <Text type="secondary">
                {isLogin ? '欢迎回来，请登录您的账户' : '创建新账户，开始您的量化交易之旅'}
              </Text>
            </div>

            {error && (
              <Alert
                message={error}
                type="error"
                showIcon
                style={{ marginBottom: '24px' }}
              />
            )}

            <Form
              form={form}
              name={isLogin ? 'login' : 'register'}
              onFinish={handleSubmit}
              layout="vertical"
              size="large"
            >
              {!isLogin && (
                <>
                  <Form.Item
                    name="fullName"
                    label="姓名"
                    rules={[
                      { required: true, message: '请输入您的姓名' },
                      { min: 2, message: '姓名至少2个字符' }
                    ]}
                  >
                    <Input
                      prefix={<UserOutlined />}
                      placeholder="请输入您的姓名"
                    />
                  </Form.Item>

                  <Form.Item
                    name="email"
                    label="邮箱"
                    rules={[
                      { required: true, message: '请输入邮箱地址' },
                      { type: 'email', message: '请输入有效的邮箱地址' }
                    ]}
                  >
                    <Input
                      prefix={<MailOutlined />}
                      placeholder="请输入邮箱地址"
                    />
                  </Form.Item>
                </>
              )}

              <Form.Item
                name="username"
                label="用户名"
                rules={[
                  { required: true, message: '请输入用户名' },
                  { min: 3, message: '用户名至少3个字符' }
                ]}
              >
                <Input
                  prefix={<UserOutlined />}
                  placeholder="请输入用户名"
                />
              </Form.Item>

              <Form.Item
                name="password"
                label="密码"
                rules={[
                  { required: true, message: '请输入密码' },
                  { min: 6, message: '密码至少6个字符' }
                ]}
              >
                <Input.Password
                  prefix={<LockOutlined />}
                  placeholder="请输入密码"
                  iconRender={(visible) => (visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />)}
                />
              </Form.Item>

              {!isLogin && (
                <Form.Item
                  name="confirmPassword"
                  label="确认密码"
                  dependencies={['password']}
                  rules={[
                    { required: true, message: '请确认密码' },
                    ({ getFieldValue }) => ({
                      validator(_, value) {
                        if (!value || getFieldValue('password') === value) {
                          return Promise.resolve();
                        }
                        return Promise.reject(new Error('两次输入的密码不一致'));
                      },
                    }),
                  ]}
                >
                  <Input.Password
                    prefix={<LockOutlined />}
                    placeholder="请再次输入密码"
                    iconRender={(visible) => (visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />)}
                  />
                </Form.Item>
              )}

              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={loading || isLoading}
                  style={{
                    width: '100%',
                    height: '48px',
                    fontSize: '16px',
                    fontWeight: '500'
                  }}
                >
                  {isLogin ? '登录' : '注册'}
                </Button>
              </Form.Item>
            </Form>

            <Divider>
              <Text type="secondary">或</Text>
            </Divider>

            <div style={{ textAlign: 'center' }}>
              <Space>
                <Text type="secondary">
                  {isLogin ? '还没有账户？' : '已有账户？'}
                </Text>
                <Button
                  type="link"
                  onClick={toggleMode}
                  style={{ padding: 0 }}
                >
                  {isLogin ? '立即注册' : '立即登录'}
                </Button>
              </Space>
            </div>

            <div style={{ 
              marginTop: '24px', 
              padding: '16px', 
              background: '#f5f5f5', 
              borderRadius: '8px',
              textAlign: 'center'
            }}>
              <Text type="secondary" style={{ fontSize: '12px' }}>
                登录即表示您同意我们的
                <Button type="link" style={{ padding: 0, fontSize: '12px' }}>
                  服务条款
                </Button>
                和
                <Button type="link" style={{ padding: 0, fontSize: '12px' }}>
                  隐私政策
                </Button>
              </Text>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Login;
