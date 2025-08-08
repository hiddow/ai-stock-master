import React, { useState, useEffect } from 'react'
import { Card, Table, Button, Space, Tag, Modal, Form, InputNumber, Input, message, Row, Col, Statistic, Progress, Tabs, Timeline, Descriptions, Alert, Spin } from 'antd'
import { StarFilled, EyeOutlined, DeleteOutlined, EditOutlined, PlusOutlined, RiseOutlined, FallOutlined, SyncOutlined } from '@ant-design/icons'
import axios from 'axios'
import ReactECharts from 'echarts-for-react'

const { TextArea } = Input
const { TabPane } = Tabs

const WatchList = ({ onSelectStock }) => {
  const [watchList, setWatchList] = useState([])
  const [loading, setLoading] = useState(false)
  const [addModalVisible, setAddModalVisible] = useState(false)
  const [editModalVisible, setEditModalVisible] = useState(false)
  const [selectedItem, setSelectedItem] = useState(null)
  const [analysisData, setAnalysisData] = useState(null)
  const [analysisModalVisible, setAnalysisModalVisible] = useState(false)
  const [form] = Form.useForm()
  const [editForm] = Form.useForm()

  useEffect(() => {
    fetchWatchList()
    const interval = setInterval(fetchWatchList, 30000) // 每30秒刷新
    return () => clearInterval(interval)
  }, [])

  const fetchWatchList = async () => {
    setLoading(true)
    try {
      const response = await axios.get('/api/watchlist/list')
      setWatchList(response.data)
    } catch (error) {
      console.error('获取关注列表失败:', error)
      // 使用模拟数据
      setWatchList(getMockWatchList())
    } finally {
      setLoading(false)
    }
  }

  const getMockWatchList = () => [
    {
      id: 1,
      code: '605378',
      name: '野马电池',
      add_price: 18.5,
      current_price: 19.2,
      change_pct: 3.78,
      target_price: 22,
      stop_loss_price: 17,
      notes: '新能源概念，关注突破',
      created_at: '2025-08-01'
    },
    {
      id: 2,
      code: '000001',
      name: '平安银行',
      add_price: 12.8,
      current_price: 12.5,
      change_pct: -2.34,
      target_price: 14,
      stop_loss_price: 11.5,
      notes: '银行股防守',
      created_at: '2025-08-05'
    }
  ]

  const handleAdd = async (values) => {
    try {
      await axios.post('/api/watchlist/add', values)
      message.success('添加成功')
      setAddModalVisible(false)
      form.resetFields()
      fetchWatchList()
    } catch (error) {
      message.error('添加失败')
    }
  }

  const handleRemove = async (id) => {
    Modal.confirm({
      title: '确认移除',
      content: '确定要从关注列表中移除这只股票吗？',
      onOk: async () => {
        try {
          await axios.delete(`/api/watchlist/${id}`)
          message.success('移除成功')
          fetchWatchList()
        } catch (error) {
          message.error('移除失败')
        }
      }
    })
  }

  const handleEdit = async (values) => {
    try {
      await axios.put(`/api/watchlist/${selectedItem.id}`, values)
      message.success('更新成功')
      setEditModalVisible(false)
      fetchWatchList()
    } catch (error) {
      message.error('更新失败')
    }
  }

  const fetchAnalysis = async (code) => {
    setLoading(true)
    try {
      const response = await axios.get(`/api/watchlist/${code}/analysis`)
      setAnalysisData(response.data)
      setAnalysisModalVisible(true)
    } catch (error) {
      console.error('获取分析失败:', error)
      message.error('获取分析数据失败')
    } finally {
      setLoading(false)
    }
  }

  const columns = [
    {
      title: '股票',
      key: 'stock',
      render: (_, record) => (
        <Space>
          <strong>{record.name}</strong>
          <Tag color="blue">{record.code}</Tag>
        </Space>
      )
    },
    {
      title: '加入价格',
      dataIndex: 'add_price',
      key: 'add_price',
      align: 'right',
      render: (val) => `¥${val?.toFixed(2) || '-'}`
    },
    {
      title: '当前价格',
      dataIndex: 'current_price',
      key: 'current_price',
      align: 'right',
      render: (val, record) => (
        <span className={record.change_pct > 0 ? 'price-up' : record.change_pct < 0 ? 'price-down' : ''}>
          ¥{val?.toFixed(2) || '-'}
        </span>
      )
    },
    {
      title: '收益率',
      dataIndex: 'change_pct',
      key: 'change_pct',
      align: 'right',
      render: (val) => (
        <span className={val > 0 ? 'price-up' : val < 0 ? 'price-down' : ''}>
          {val > 0 && '+'}{val?.toFixed(2) || 0}%
          {val > 0 ? <RiseOutlined /> : val < 0 ? <FallOutlined /> : null}
        </span>
      )
    },
    {
      title: '目标价',
      dataIndex: 'target_price',
      key: 'target_price',
      align: 'right',
      render: (val, record) => {
        if (!val) return '-'
        const progress = ((record.current_price - record.add_price) / (val - record.add_price)) * 100
        return (
          <div>
            <div>¥{val.toFixed(2)}</div>
            <Progress percent={Math.min(100, Math.max(0, progress))} size="small" showInfo={false} />
          </div>
        )
      }
    },
    {
      title: '止损价',
      dataIndex: 'stop_loss_price',
      key: 'stop_loss_price',
      align: 'right',
      render: (val, record) => {
        if (!val) return '-'
        const isWarning = record.current_price <= val
        return (
          <span style={{ color: isWarning ? '#f5222d' : undefined }}>
            ¥{val.toFixed(2)}
            {isWarning && <Tag color="red" style={{ marginLeft: 8 }}>触及止损</Tag>}
          </span>
        )
      }
    },
    {
      title: '备注',
      dataIndex: 'notes',
      key: 'notes',
      width: 200,
      ellipsis: true
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="small">
          <Button 
            type="link" 
            icon={<EyeOutlined />} 
            onClick={() => fetchAnalysis(record.code)}
          >
            分析
          </Button>
          <Button 
            type="link" 
            icon={<EditOutlined />} 
            onClick={() => {
              setSelectedItem(record)
              editForm.setFieldsValue({
                target_price: record.target_price,
                stop_loss_price: record.stop_loss_price,
                notes: record.notes
              })
              setEditModalVisible(true)
            }}
          >
            编辑
          </Button>
          <Button 
            type="link" 
            danger 
            icon={<DeleteOutlined />} 
            onClick={() => handleRemove(record.id)}
          >
            移除
          </Button>
        </Space>
      )
    }
  ]

  const renderAnalysisModal = () => {
    if (!analysisData) return null

    const { stock_info, current_status, technical_signals, ai_prediction, patterns, detailed_analysis, risk_assessment, investment_suggestion } = analysisData

    return (
      <Modal
        title={`${stock_info.name} (${stock_info.code}) - 详细分析报告`}
        visible={analysisModalVisible}
        onCancel={() => setAnalysisModalVisible(false)}
        width={1200}
        footer={[
          <Button key="close" onClick={() => setAnalysisModalVisible(false)}>
            关闭
          </Button>
        ]}
      >
        <Tabs defaultActiveKey="1">
          <TabPane tab="技术分析" key="1">
            <Row gutter={[16, 16]}>
              <Col span={8}>
                <Card size="small">
                  <Statistic
                    title="当前价格"
                    value={current_status.price}
                    precision={2}
                    prefix="¥"
                  />
                </Card>
              </Col>
              <Col span={8}>
                <Card size="small">
                  <Statistic
                    title="RSI"
                    value={current_status.rsi}
                    precision={1}
                    valueStyle={{ color: current_status.rsi > 70 ? '#f5222d' : current_status.rsi < 30 ? '#52c41a' : undefined }}
                  />
                </Card>
              </Col>
              <Col span={8}>
                <Card size="small">
                  <Statistic
                    title="MACD"
                    value={current_status.macd}
                    precision={3}
                    valueStyle={{ color: current_status.macd > 0 ? '#52c41a' : '#f5222d' }}
                  />
                </Card>
              </Col>
            </Row>
            
            <Card style={{ marginTop: 16 }} title="详细分析">
              <Timeline>
                {detailed_analysis?.map((item, index) => (
                  <Timeline.Item key={index} color={item.type.includes('风险') ? 'red' : 'blue'}>
                    <strong>{item.type}：</strong>{item.content}
                  </Timeline.Item>
                ))}
              </Timeline>
            </Card>
          </TabPane>

          <TabPane tab="AI预测" key="2">
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Card title="明日预测">
                  <Descriptions column={1}>
                    <Descriptions.Item label="预测价格">
                      ¥{ai_prediction?.next_day?.price?.toFixed(2) || '-'}
                    </Descriptions.Item>
                    <Descriptions.Item label="预测涨跌">
                      <span className={ai_prediction?.next_day?.change > 0 ? 'price-up' : 'price-down'}>
                        {ai_prediction?.next_day?.change > 0 && '+'}
                        {(ai_prediction?.next_day?.change * 100)?.toFixed(2)}%
                      </span>
                    </Descriptions.Item>
                    <Descriptions.Item label="置信度">
                      <Progress percent={ai_prediction?.next_day?.confidence || 0} />
                    </Descriptions.Item>
                  </Descriptions>
                  
                  <div style={{ marginTop: 16 }}>
                    <strong>预测依据：</strong>
                    <ul>
                      {ai_prediction?.next_day?.reasons?.map((reason, index) => (
                        <li key={index}>{reason}</li>
                      ))}
                    </ul>
                  </div>
                </Card>
              </Col>
              
              <Col span={12}>
                <Card title="5日趋势预测">
                  {ai_prediction?.five_day_trend && (
                    <>
                      <Tag color={ai_prediction.five_day_trend.trend === 'bullish' ? 'green' : ai_prediction.five_day_trend.trend === 'bearish' ? 'red' : 'blue'}>
                        {ai_prediction.five_day_trend.trend === 'bullish' ? '看涨' : ai_prediction.five_day_trend.trend === 'bearish' ? '看跌' : '震荡'}
                      </Tag>
                      <div style={{ marginTop: 16 }}>
                        {ai_prediction.five_day_trend.predictions?.map((pred, index) => (
                          <div key={index}>
                            第{pred.day}天: ¥{pred.price?.toFixed(2)} ({pred.change > 0 ? '+' : ''}{(pred.change * 100)?.toFixed(2)}%)
                          </div>
                        ))}
                      </div>
                    </>
                  )}
                </Card>
              </Col>
            </Row>

            {patterns && patterns.length > 0 && (
              <Card style={{ marginTop: 16 }} title="K线形态">
                <Timeline>
                  {patterns.map((pattern, index) => (
                    <Timeline.Item 
                      key={index} 
                      color={pattern.signal === 'bullish' ? 'green' : pattern.signal === 'bearish' ? 'red' : 'blue'}
                    >
                      <strong>{pattern.pattern}</strong> - {pattern.description}
                    </Timeline.Item>
                  ))}
                </Timeline>
              </Card>
            )}
          </TabPane>

          <TabPane tab="风险评估" key="3">
            <Card>
              <Row gutter={[16, 16]}>
                <Col span={8}>
                  <Statistic
                    title="风险评分"
                    value={risk_assessment?.risk_score || 50}
                    suffix="/ 100"
                    valueStyle={{ 
                      color: risk_assessment?.risk_score > 70 ? '#f5222d' : risk_assessment?.risk_score < 30 ? '#52c41a' : '#faad14' 
                    }}
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="风险等级"
                    value={risk_assessment?.risk_level || '中'}
                    valueStyle={{ 
                      color: risk_assessment?.risk_level === '高' ? '#f5222d' : risk_assessment?.risk_level === '低' ? '#52c41a' : '#faad14' 
                    }}
                  />
                </Col>
                <Col span={8}>
                  <Progress
                    type="circle"
                    percent={risk_assessment?.risk_score || 50}
                    strokeColor={risk_assessment?.risk_score > 70 ? '#f5222d' : risk_assessment?.risk_score < 30 ? '#52c41a' : '#faad14'}
                  />
                </Col>
              </Row>

              <div style={{ marginTop: 24 }}>
                <h4>风险因素：</h4>
                <ul>
                  {risk_assessment?.risk_factors?.map((factor, index) => (
                    <li key={index}>{factor}</li>
                  ))}
                </ul>
                <Alert
                  message="风险建议"
                  description={risk_assessment?.suggestion}
                  type={risk_assessment?.risk_level === '高' ? 'error' : risk_assessment?.risk_level === '低' ? 'success' : 'warning'}
                  showIcon
                />
              </div>
            </Card>
          </TabPane>

          <TabPane tab="投资建议" key="4">
            <Card>
              <Row gutter={[16, 16]}>
                <Col span={12}>
                  <Descriptions column={1} bordered>
                    <Descriptions.Item label="综合评分">
                      <Progress percent={investment_suggestion?.score || 50} />
                    </Descriptions.Item>
                    <Descriptions.Item label="操作建议">
                      <Tag color={investment_suggestion?.action === '买入' ? 'green' : investment_suggestion?.action === '卖出/回避' ? 'red' : 'blue'}>
                        {investment_suggestion?.action}
                      </Tag>
                    </Descriptions.Item>
                    <Descriptions.Item label="建议仓位">
                      {investment_suggestion?.position}
                    </Descriptions.Item>
                    <Descriptions.Item label="建议原因">
                      {investment_suggestion?.reason}
                    </Descriptions.Item>
                  </Descriptions>
                </Col>
                <Col span={12}>
                  <Descriptions column={1} bordered>
                    <Descriptions.Item label="建议买入点">
                      {investment_suggestion?.entry_points?.map((point, index) => (
                        <div key={index}>¥{point?.toFixed(2)}</div>
                      ))}
                    </Descriptions.Item>
                    <Descriptions.Item label="建议卖出点">
                      {investment_suggestion?.exit_points?.map((point, index) => (
                        <div key={index}>¥{point?.toFixed(2)}</div>
                      ))}
                    </Descriptions.Item>
                    <Descriptions.Item label="止损位">
                      ¥{investment_suggestion?.stop_loss?.toFixed(2)}
                    </Descriptions.Item>
                  </Descriptions>
                </Col>
              </Row>

              <Alert
                style={{ marginTop: 16 }}
                message="投资提示"
                description="以上建议仅供参考，投资有风险，决策需谨慎。请根据自身风险承受能力和投资目标做出决策。"
                type="info"
                showIcon
              />
            </Card>
          </TabPane>
        </Tabs>
      </Modal>
    )
  }

  return (
    <Spin spinning={loading}>
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        <Card>
          <Row justify="space-between" align="middle">
            <Col>
              <h2 style={{ margin: 0 }}>
                <StarFilled style={{ color: '#faad14', marginRight: 8 }} />
                我的关注
              </h2>
            </Col>
            <Col>
              <Space>
                <Button icon={<SyncOutlined />} onClick={fetchWatchList}>
                  刷新
                </Button>
                <Button type="primary" icon={<PlusOutlined />} onClick={() => setAddModalVisible(true)}>
                  添加关注
                </Button>
              </Space>
            </Col>
          </Row>
        </Card>

        <Card>
          <Table
            columns={columns}
            dataSource={watchList}
            rowKey="id"
            pagination={false}
          />
        </Card>

        <Modal
          title="添加关注"
          visible={addModalVisible}
          onCancel={() => setAddModalVisible(false)}
          footer={null}
        >
          <Form
            form={form}
            layout="vertical"
            onFinish={handleAdd}
          >
            <Form.Item
              name="code"
              label="股票代码"
              rules={[{ required: true, message: '请输入股票代码' }]}
            >
              <Input placeholder="如：605378" />
            </Form.Item>
            <Form.Item
              name="target_price"
              label="目标价格"
            >
              <InputNumber
                style={{ width: '100%' }}
                min={0}
                precision={2}
                placeholder="可选"
              />
            </Form.Item>
            <Form.Item
              name="stop_loss_price"
              label="止损价格"
            >
              <InputNumber
                style={{ width: '100%' }}
                min={0}
                precision={2}
                placeholder="可选"
              />
            </Form.Item>
            <Form.Item
              name="notes"
              label="备注"
            >
              <TextArea rows={3} placeholder="可选" />
            </Form.Item>
            <Form.Item>
              <Space>
                <Button type="primary" htmlType="submit">
                  添加
                </Button>
                <Button onClick={() => setAddModalVisible(false)}>
                  取消
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Modal>

        <Modal
          title="编辑关注"
          visible={editModalVisible}
          onCancel={() => setEditModalVisible(false)}
          footer={null}
        >
          <Form
            form={editForm}
            layout="vertical"
            onFinish={handleEdit}
          >
            <Form.Item
              name="target_price"
              label="目标价格"
            >
              <InputNumber
                style={{ width: '100%' }}
                min={0}
                precision={2}
              />
            </Form.Item>
            <Form.Item
              name="stop_loss_price"
              label="止损价格"
            >
              <InputNumber
                style={{ width: '100%' }}
                min={0}
                precision={2}
              />
            </Form.Item>
            <Form.Item
              name="notes"
              label="备注"
            >
              <TextArea rows={3} />
            </Form.Item>
            <Form.Item>
              <Space>
                <Button type="primary" htmlType="submit">
                  保存
                </Button>
                <Button onClick={() => setEditModalVisible(false)}>
                  取消
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Modal>

        {renderAnalysisModal()}
      </Space>
    </Spin>
  )
}

export default WatchList