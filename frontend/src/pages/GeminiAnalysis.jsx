import React, { useState, useEffect } from 'react'
import { Card, Button, Space, Spin, message, Tabs, Tag, Alert, Input, Upload, Row, Col, Statistic, Progress, List, Badge } from 'antd'
import { RobotOutlined, CameraOutlined, QuestionCircleOutlined, ThunderboltOutlined, BulbOutlined, AlertOutlined, RiseOutlined, FallOutlined } from '@ant-design/icons'
import axios from 'axios'

const { TabPane } = Tabs
const { TextArea } = Input

const GeminiAnalysis = ({ stock }) => {
  const [loading, setLoading] = useState(false)
  const [analysisResult, setAnalysisResult] = useState(null)
  const [quickSignal, setQuickSignal] = useState(null)
  const [alerts, setAlerts] = useState([])
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [askingQuestion, setAskingQuestion] = useState(false)

  useEffect(() => {
    if (stock) {
      fetchQuickSignal()
    }
    fetchAlerts()
  }, [stock])

  const fetchComprehensiveAnalysis = async () => {
    if (!stock) {
      message.warning('请先选择一只股票')
      return
    }

    setLoading(true)
    try {
      const response = await axios.post(`/api/gemini/${stock.code}/comprehensive`, {
        days: 30
      })
      
      if (response.data.status === 'success') {
        setAnalysisResult(response.data.gemini_analysis)
        message.success('Gemini 分析完成')
      }
    } catch (error) {
      console.error('Gemini 分析失败:', error)
      message.error('分析失败，请检查 Gemini API 配置')
    } finally {
      setLoading(false)
    }
  }

  const fetchQuickSignal = async () => {
    if (!stock) return

    try {
      const response = await axios.post(`/api/gemini/${stock.code}/quick-signal`)
      if (response.data.status === 'success') {
        setQuickSignal(response.data)
      }
    } catch (error) {
      console.error('获取快速信号失败:', error)
    }
  }

  const fetchAlerts = async () => {
    try {
      const response = await axios.get('/api/gemini/monitor/alerts')
      if (response.data.status === 'success') {
        setAlerts(response.data.alerts)
      }
    } catch (error) {
      console.error('获取警报失败:', error)
    }
  }

  const handleAskQuestion = async () => {
    if (!question.trim()) {
      message.warning('请输入问题')
      return
    }

    setAskingQuestion(true)
    try {
      const response = await axios.post('/api/gemini/ask', {
        question: question,
        context: stock ? {
          stock_code: stock.code,
          stock_name: stock.name,
          current_price: stock.price
        } : null
      })

      if (response.data.status === 'success') {
        setAnswer(response.data.answer)
      }
    } catch (error) {
      console.error('提问失败:', error)
      message.error('提问失败')
    } finally {
      setAskingQuestion(false)
    }
  }

  const handleChartUpload = async (info) => {
    if (info.file.status === 'uploading') {
      message.loading('正在分析图表...')
      return
    }
    
    if (info.file.status === 'done') {
      message.success('图表分析完成')
      // 处理分析结果
      if (info.file.response && info.file.response.analysis) {
        setAnalysisResult(info.file.response.analysis)
      }
    }
  }

  const renderAnalysisResult = () => {
    if (!analysisResult) return null

    const analysis = analysisResult.analysis || {}

    return (
      <Card>
        <Tabs defaultActiveKey="1">
          <TabPane tab="技术分析" key="1">
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <h4>趋势分析</h4>
                <p>{analysis['技术面分析'] || '暂无技术分析'}</p>
              </div>
              
              {analysis['关键价位'] && (
                <Row gutter={16}>
                  <Col span={12}>
                    <Statistic
                      title="支撑位"
                      value={analysis['关键价位']['止损位'] || '-'}
                      prefix="¥"
                      valueStyle={{ color: '#52c41a' }}
                    />
                  </Col>
                  <Col span={12}>
                    <Statistic
                      title="阻力位"
                      value={analysis['关键价位']['目标位'] || '-'}
                      prefix="¥"
                      valueStyle={{ color: '#f5222d' }}
                    />
                  </Col>
                </Row>
              )}
            </Space>
          </TabPane>

          <TabPane tab="预测分析" key="2">
            <Space direction="vertical" style={{ width: '100%' }}>
              <Alert
                message="短期预测（1-5天）"
                description={analysis['短期预测'] || '暂无预测'}
                type="info"
                showIcon
              />
              
              <Alert
                message="中期预测（1-4周）"
                description={analysis['中期预测'] || '暂无预测'}
                type="warning"
                showIcon
              />
            </Space>
          </TabPane>

          <TabPane tab="投资建议" key="3">
            <Space direction="vertical" style={{ width: '100%' }}>
              <Card size="small">
                <Row>
                  <Col span={8}>
                    <Tag color={
                      analysis['投资建议'] === '买入' ? 'green' :
                      analysis['投资建议'] === '卖出' ? 'red' : 'blue'
                    } style={{ fontSize: 16, padding: '8px 16px' }}>
                      {analysis['投资建议'] || '持有'}
                    </Tag>
                  </Col>
                </Row>
              </Card>
              
              {analysis['风险提示'] && (
                <Alert
                  message="风险提示"
                  description={analysis['风险提示']}
                  type="error"
                  showIcon
                  icon={<AlertOutlined />}
                />
              )}
            </Space>
          </TabPane>
        </Tabs>
      </Card>
    )
  }

  const renderQuickSignal = () => {
    if (!quickSignal) return null

    const signalColor = quickSignal.signal === 'BUY' ? '#52c41a' : 
                        quickSignal.signal === 'SELL' ? '#f5222d' : '#faad14'

    return (
      <Card title="快速信号" size="small">
        <Row gutter={16}>
          <Col span={8}>
            <div style={{ textAlign: 'center' }}>
              <Tag color={signalColor} style={{ fontSize: 18, padding: '8px 16px' }}>
                {quickSignal.signal === 'BUY' ? '买入' :
                 quickSignal.signal === 'SELL' ? '卖出' : '持有'}
              </Tag>
            </div>
          </Col>
          <Col span={8}>
            <Statistic
              title="信号强度"
              value={quickSignal.strength || 5}
              suffix="/ 10"
              valueStyle={{ color: signalColor }}
            />
          </Col>
          <Col span={8}>
            <div>
              <strong>理由：</strong>
              <p>{quickSignal.reason || '综合技术指标判断'}</p>
            </div>
          </Col>
        </Row>
      </Card>
    )
  }

  const renderAlerts = () => {
    if (!alerts || alerts.length === 0) return null

    return (
      <Card title="实时监控警报" size="small">
        <List
          dataSource={alerts.slice(0, 5)}
          renderItem={alert => (
            <List.Item>
              <Badge 
                status={alert.alert_type === 'PRICE_CHANGE' ? 'error' : 'warning'}
                text={
                  <Space>
                    <strong>{alert.name}({alert.code})</strong>
                    {alert.alert_type === 'PRICE_CHANGE' ? (
                      <span>
                        价格异动 
                        <span style={{ color: alert.change_pct > 0 ? '#52c41a' : '#f5222d' }}>
                          {alert.change_pct > 0 ? '+' : ''}{alert.change_pct?.toFixed(2)}%
                        </span>
                      </span>
                    ) : (
                      <span>成交量异常 {alert.volume_ratio?.toFixed(2)}倍</span>
                    )}
                    {alert.signal && (
                      <Tag color={alert.signal === 'BUY' ? 'green' : alert.signal === 'SELL' ? 'red' : 'blue'}>
                        {alert.signal}
                      </Tag>
                    )}
                  </Space>
                }
              />
            </List.Item>
          )}
        />
      </Card>
    )
  }

  return (
    <Spin spinning={loading}>
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        <Card>
          <Row gutter={16} align="middle">
            <Col span={12}>
              <h2 style={{ margin: 0 }}>
                <RobotOutlined style={{ marginRight: 8, color: '#1890ff' }} />
                Gemini AI 分析
              </h2>
            </Col>
            <Col span={12} style={{ textAlign: 'right' }}>
              <Space>
                <Upload
                  name="file"
                  action="/api/gemini/chart-analysis"
                  accept="image/*"
                  showUploadList={false}
                  onChange={handleChartUpload}
                >
                  <Button icon={<CameraOutlined />}>
                    上传K线图分析
                  </Button>
                </Upload>
                
                <Button
                  type="primary"
                  icon={<BulbOutlined />}
                  onClick={fetchComprehensiveAnalysis}
                  disabled={!stock}
                >
                  深度分析
                </Button>
                
                <Button
                  icon={<ThunderboltOutlined />}
                  onClick={fetchQuickSignal}
                  disabled={!stock}
                >
                  快速信号
                </Button>
              </Space>
            </Col>
          </Row>
        </Card>

        <Row gutter={16}>
          <Col xs={24} md={12}>
            {renderQuickSignal()}
          </Col>
          <Col xs={24} md={12}>
            {renderAlerts()}
          </Col>
        </Row>

        {analysisResult && renderAnalysisResult()}

        <Card title="AI 问答">
          <Space direction="vertical" style={{ width: '100%' }}>
            <TextArea
              placeholder="输入你的问题，例如：这只股票的主力资金流向如何？"
              value={question}
              onChange={e => setQuestion(e.target.value)}
              rows={3}
            />
            
            <Button
              type="primary"
              icon={<QuestionCircleOutlined />}
              onClick={handleAskQuestion}
              loading={askingQuestion}
            >
              提问 Gemini
            </Button>
            
            {answer && (
              <Alert
                message="Gemini 回答"
                description={answer}
                type="info"
                showIcon
                style={{ marginTop: 16 }}
              />
            )}
          </Space>
        </Card>
      </Space>
    </Spin>
  )
}

export default GeminiAnalysis