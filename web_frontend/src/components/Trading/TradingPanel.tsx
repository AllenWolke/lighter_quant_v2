import React, { useState, useEffect } from 'react';
import {
  Card,
  Form,
  Select,
  InputNumber,
  Button,
  Row,
  Col,
  Divider,
  Space,
  message,
  Alert,
  Typography
} from 'antd';
import { SaveOutlined, ReloadOutlined } from '@ant-design/icons';

// 状态管理
import { useTradingStore } from '../../store/tradingStore';

// API
import { tradingApi, strategyApi } from '../../api';

// 类型
import { Strategy, StrategyParameter } from '../../types';

const { Title, Text } = Typography;
const { Option } = Select;

interface TradingPanelProps {
  className?: string;
}

const TradingPanel: React.FC<TradingPanelProps> = ({ className }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [strategyParams, setStrategyParams] = useState<StrategyParameter[]>([]);
  
  const {
    selectedSymbol,
    selectedStrategy,
    strategyParams: currentParams,
    updateSelectedSymbol,
    updateSelectedStrategy,
    updateStrategyParams
  } = useTradingStore();

  // 初始化
  useEffect(() => {
    loadStrategies();
    loadSymbols();
  }, []);

  // 加载策略列表
  const loadStrategies = async () => {
    try {
      const data = await strategyApi.getStrategies();
      setStrategies(data);
    } catch (error) {
      console.error('加载策略失败:', error);
      message.error('加载策略失败');
    }
  };

  // 加载交易对列表
  const loadSymbols = async () => {
    try {
      const data = await tradingApi.getSymbols();
      // 这里可以设置可用的交易对
    } catch (error) {
      console.error('加载交易对失败:', error);
    }
  };

  // 策略改变时加载参数
  useEffect(() => {
    if (selectedStrategy) {
      loadStrategyParameters(selectedStrategy);
    }
  }, [selectedStrategy]);

  // 加载策略参数
  const loadStrategyParameters = async (strategyId: number) => {
    try {
      const data = await strategyApi.getStrategyParameters(strategyId);
      setStrategyParams(data);
      
      // 设置表单默认值
      const defaultValues: Record<string, any> = {};
      data.forEach(param => {
        defaultValues[param.parameterName] = JSON.parse(param.parameterValue);
      });
      form.setFieldsValue(defaultValues);
    } catch (error) {
      console.error('加载策略参数失败:', error);
    }
  };

  // 保存设置
  const handleSave = async () => {
    try {
      setLoading(true);
      
      const values = await form.validateFields();
      
      // 更新策略参数
      if (selectedStrategy) {
        await strategyApi.updateStrategyParameters(selectedStrategy, values);
        updateStrategyParams(values);
      }
      
      message.success('设置保存成功');
    } catch (error) {
      console.error('保存设置失败:', error);
      message.error('保存设置失败');
    } finally {
      setLoading(false);
    }
  };

  // 重置设置
  const handleReset = () => {
    form.resetFields();
    if (selectedStrategy) {
      loadStrategyParameters(selectedStrategy);
    }
  };

  // 渲染参数输入
  const renderParameterInput = (param: StrategyParameter) => {
    const { parameterName, parameterType, description } = param;
    
    switch (parameterType) {
      case 'int':
        return (
          <Form.Item
            key={parameterName}
            name={parameterName}
            label={parameterName}
            tooltip={description}
            rules={[{ required: true, message: `请输入${parameterName}` }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              placeholder={`请输入${parameterName}`}
            />
          </Form.Item>
        );
        
      case 'float':
        return (
          <Form.Item
            key={parameterName}
            name={parameterName}
            label={parameterName}
            tooltip={description}
            rules={[{ required: true, message: `请输入${parameterName}` }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              step={0.01}
              placeholder={`请输入${parameterName}`}
            />
          </Form.Item>
        );
        
      case 'bool':
        return (
          <Form.Item
            key={parameterName}
            name={parameterName}
            label={parameterName}
            tooltip={description}
            valuePropName="checked"
          >
            <Select placeholder={`请选择${parameterName}`}>
              <Option value={true}>是</Option>
              <Option value={false}>否</Option>
            </Select>
          </Form.Item>
        );
        
      default:
        return (
          <Form.Item
            key={parameterName}
            name={parameterName}
            label={parameterName}
            tooltip={description}
            rules={[{ required: true, message: `请输入${parameterName}` }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              placeholder={`请输入${parameterName}`}
            />
          </Form.Item>
        );
    }
  };

  return (
    <div className={className}>
      <Card title="交易设置" extra={
        <Space>
          <Button
            icon={<ReloadOutlined />}
            onClick={handleReset}
          >
            重置
          </Button>
          <Button
            type="primary"
            icon={<SaveOutlined />}
            onClick={handleSave}
            loading={loading}
          >
            保存设置
          </Button>
        </Space>
      }>
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            symbol: selectedSymbol,
            strategy: selectedStrategy
          }}
        >
          {/* 基础设置 */}
          <Title level={5}>基础设置</Title>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="symbol"
                label="交易对"
                rules={[{ required: true, message: '请选择交易对' }]}
              >
                <Select
                  placeholder="请选择交易对"
                  onChange={(value) => updateSelectedSymbol(value)}
                >
                  <Option value="ETH/USDT">ETH/USDT</Option>
                  <Option value="BTC/USDT">BTC/USDT</Option>
                  <Option value="BNB/USDT">BNB/USDT</Option>
                  <Option value="ADA/USDT">ADA/USDT</Option>
                  <Option value="SOL/USDT">SOL/USDT</Option>
                </Select>
              </Form.Item>
            </Col>
            
            <Col span={12}>
              <Form.Item
                name="strategy"
                label="交易策略"
                rules={[{ required: true, message: '请选择交易策略' }]}
              >
                <Select
                  placeholder="请选择交易策略"
                  onChange={(value) => updateSelectedStrategy(value)}
                >
                  {strategies.map(strategy => (
                    <Option key={strategy.id} value={strategy.id}>
                      {strategy.name}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          {/* 策略参数 */}
          {strategyParams.length > 0 && (
            <>
              <Divider />
              <Title level={5}>策略参数</Title>
              
              <Alert
                message="参数说明"
                description="请根据您的风险承受能力和市场情况调整策略参数。建议先在模拟环境中测试参数效果。"
                type="info"
                showIcon
                style={{ marginBottom: 16 }}
              />
              
              <Row gutter={16}>
                {strategyParams.map(param => (
                  <Col span={12} key={param.id}>
                    {renderParameterInput(param)}
                  </Col>
                ))}
              </Row>
            </>
          )}

          {/* 风险控制 */}
          <Divider />
          <Title level={5}>风险控制</Title>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="maxPositionSize"
                label="最大持仓量"
                tooltip="单次交易的最大持仓量（USDT）"
                rules={[{ required: true, message: '请输入最大持仓量' }]}
              >
                <InputNumber
                  style={{ width: '100%' }}
                  min={0}
                  step={100}
                  placeholder="请输入最大持仓量"
                  addonAfter="USDT"
                />
              </Form.Item>
            </Col>
            
            <Col span={12}>
              <Form.Item
                name="maxLeverage"
                label="最大杠杆倍数"
                tooltip="允许使用的最大杠杆倍数"
                rules={[{ required: true, message: '请输入最大杠杆倍数' }]}
              >
                <InputNumber
                  style={{ width: '100%' }}
                  min={1}
                  max={10}
                  step={0.1}
                  placeholder="请输入最大杠杆倍数"
                  addonAfter="x"
                />
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="stopLossPercent"
                label="止损百分比"
                tooltip="触发止损的亏损百分比"
                rules={[{ required: true, message: '请输入止损百分比' }]}
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
                label="止盈百分比"
                tooltip="触发止盈的盈利百分比"
                rules={[{ required: true, message: '请输入止盈百分比' }]}
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
        </Form>
      </Card>
    </div>
  );
};

export default TradingPanel;
