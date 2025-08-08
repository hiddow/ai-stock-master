import React, { useState, useEffect } from 'react'
import { Card, Row, Col, Button, Space, Alert, Tag, Timeline, Progress, Descriptions, message } from 'antd'
import { RobotOutlined, BulbOutlined, ThunderboltOutlined, TrophyOutlined } from '@ant-design/icons'
import ReactECharts from 'echarts-for-react'
import axios from 'axios'

const AIPredict = ({ stock }) => {
  const [loading, setLoading] = useState(false)
  const [predictions, setPredictions] = useState(null)
  const [patterns, setPatterns] = useState([])
  const [signals, setSignals] = useState([])

  useEffect(() => {
    if (stock) {
      fetchPredictions()
    }
  }, [stock])

  const fetchPredictions = async () => {
    if (!stock) return

    setLoading(true)
    try {
      // 获取交易信号
      const signalsRes = await axios.get(`/api/analysis/${stock.code}/signals`)
      setSignals(signalsRes.data.signals || [])
    } catch (error) {
      console.error('获取预测失败:', error)
    }

    // 生成模拟预测数据
    generateMockPredictions()
    setLoading(false)
  }

  const generateMockPredictions = () => {
    const basePrice = stock?.price || 100
    const trend = Math.random() > 0.5 ? 'up' : 'down'
    const confidence = 60 + Math.random() * 30

    setPredictions({
      nextDay: {
        price: basePrice * (1 + (Math.random() - 0.5) * 0.05),
        change: (Math.random() - 0.5) * 5,
        confidence: confidence,
        trend: trend
      },
      nextWeek: {
        prices: Array.from({ length: 5 }, (_, i) => ({
          day: `第${i + 1}天`,
          price: basePrice * (1 + (Math.random() - 0.5) * 0.08),
          high: basePrice * (1 + Math.random() * 0.1),
          low: basePrice * (1 - Math.random() * 0.1)
        })),
        trend: trend,
        confidence: confidence - 10
      },
      signals: {
        buy: Math.random() * 100,
        sell: Math.random() * 100,
        hold: Math.random() * 100
      }
    })

    setPatterns([
      { name: '金叉形态', type: 'bullish', probability: 75, description: 'MACD金叉，建议关注买入机会' },
      { name: '上升三角形', type: 'bullish', probability: 68, description: '价格形成上升三角形，可能突破' },
      { name: '支撑位反弹', type: 'neutral', probability: 55, description: '股价接近重要支撑位' }
    ])
  }

  const getPredictionChart = () => {
    if (!predictions) return {}

    const dates = ['今日']
    const prices = [stock?.price || 100]
    
    predictions.nextWeek.prices.forEach((p, i) => {
      dates.push(p.day)
      prices.push(p.price)
    })

    return {
      title: {
        text: 'AI价格预测',
        left: 'center'
      },
      tooltip: {
        trigger: 'axis',
        formatter: '{b}: {c}元'
      },
      xAxis: {
        type: 'category',
        data: dates
      },
      yAxis: {
        type: 'value',
        min: function(value) {
          return (value.min * 0.95).toFixed(2)
        },
        max: function(value) {
          return (value.max * 1.05).toFixed(2)
        }
      },
      series: [
        {
          type: 'line',
          data: prices,
          smooth: true,
          lineStyle: {
            width: 3,
            color: predictions.nextDay.trend === 'up' ? '#52c41a' : '#f5222d'
          },
          areaStyle: {
            color: predictions.nextDay.trend === 'up' 
              ? 'rgba(82, 196, 26, 0.1)' 
              : 'rgba(245, 34, 45, 0.1)'
          },
          markPoint: {
            data: [
              { type: 'max', name: '最高' },
              { type: 'min', name: '最低' }
            ]
          },
          markLine: {
            data: [
              { type: 'average', name: '平均值' }
            ]
          }
        }
      ]
    }
  }

  const getSignalChart = () => {
    if (!predictions) return {}

    return {
      title: {
        text: 'AI建议分布',
        left: 'center'
      },
      tooltip: {
        trigger: 'item'
      },
      series: [
        {
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: true,
            formatter: '{b}: {d}%'
          },
          data: [
            { 
              value: predictions.signals.buy.toFixed(0), 
              name: '买入', 
              itemStyle: { color: '#52c41a' } 
            },
            { 
              value: predictions.signals.sell.toFixed(0), 
              name: '卖出', 
              itemStyle: { color: '#f5222d' } 
            },
            { 
              value: predictions.signals.hold.toFixed(0), 
              name: '持有', 
              itemStyle: { color: '#1890ff' } 
            }
          ]
        }
      ]
    }
  }

  if (!stock) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: '50px 0' }}>
          <RobotOutlined style={{ fontSize: 48, color: '#999' }} />
          <p style={{ marginTop: 16, color: '#999' }}>请先选择一只股票进行AI预测</p>
        </div>
      </Card>
    )
  }

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="large">
      <Card>
        <Row align="middle">
          <Col flex="auto">
            <h2 style={{ margin: 0 }}>
              <RobotOutlined style={{ marginRight: 8 }} />
              {stock.name} ({stock.code}) - AI智能预测
            </h2>
          </Col>
          <Col>
            <Button type="primary" onClick={fetchPredictions} loading={loading}>
              重新预测
            </Button>
          </Col>
        </Row>
      </Card>

      {predictions && (
        <>
          <Row gutter={[16, 16]}>
            <Col xs={24} md={12}>
              <Card title="明日预测" extra={<Tag color="blue">置信度: {predictions.nextDay.confidence.toFixed(0)}%</Tag>}>
                <Descriptions column={1}>
                  <Descriptions.Item label="预测价格">
                    <span style={{ fontSize: 24, fontWeight: 'bold', color: predictions.nextDay.trend === 'up' ? '#52c41a' : '#f5222d' }}>
                      ¥{predictions.nextDay.price.toFixed(2)}
                    </span>
                  </Descriptions.Item>
                  <Descriptions.Item label="预测涨跌">
                    <span className={predictions.nextDay.change > 0 ? 'price-up' : 'price-down'}>
                      {predictions.nextDay.change > 0 && '+'}{predictions.nextDay.change.toFixed(2)}%
                    </span>
                  </Descriptions.Item>
                  <Descriptions.Item label="趋势判断">
                    <Tag color={predictions.nextDay.trend === 'up' ? 'green' : 'red'}>
                      {predictions.nextDay.trend === 'up' ? '看涨' : '看跌'}
                    </Tag>
                  </Descriptions.Item>
                  <Descriptions.Item label="置信度">
                    <Progress 
                      percent={predictions.nextDay.confidence} 
                      strokeColor={predictions.nextDay.confidence > 70 ? '#52c41a' : '#faad14'}
                      format={percent => `${percent.toFixed(0)}%`}
                    />
                  </Descriptions.Item>
                </Descriptions>
              </Card>
            </Col>

            <Col xs={24} md={12}>
              <Card title="K线形态识别" extra={<BulbOutlined />}>
                <Timeline>
                  {patterns.map((pattern, index) => (
                    <Timeline.Item 
                      key={index}
                      color={pattern.type === 'bullish' ? 'green' : pattern.type === 'bearish' ? 'red' : 'blue'}
                    >
                      <Space>
                        <strong>{pattern.name}</strong>
                        <Tag>{pattern.probability}%</Tag>
                      </Space>
                      <br />
                      <span style={{ color: '#666', fontSize: 12 }}>{pattern.description}</span>
                    </Timeline.Item>
                  ))}
                </Timeline>
              </Card>
            </Col>
          </Row>

          <Row gutter={[16, 16]}>
            <Col xs={24} md={12}>
              <Card>
                <ReactECharts option={getPredictionChart()} style={{ height: 300 }} />
              </Card>
            </Col>
            <Col xs={24} md={12}>
              <Card>
                <ReactECharts option={getSignalChart()} style={{ height: 300 }} />
              </Card>
            </Col>
          </Row>

          <Card title="AI分析建议" extra={<ThunderboltOutlined />}>
            <Alert
              message="综合分析结果"
              description={
                <div>
                  <p>基于技术指标、K线形态和市场情绪的综合分析：</p>
                  <ul>
                    <li>短期趋势：{predictions.nextDay.trend === 'up' ? '看涨' : '看跌'}，建议{predictions.signals.buy > predictions.signals.sell ? '适量买入' : '谨慎观望'}</li>
                    <li>支撑位：¥{(stock.price * 0.95).toFixed(2)}，压力位：¥{(stock.price * 1.05).toFixed(2)}</li>
                    <li>风险提示：市场存在不确定性，请合理控制仓位</li>
                    <li>置信度：{predictions.nextDay.confidence.toFixed(0)}%，仅供参考</li>
                  </ul>
                </div>
              }
              type={predictions.nextDay.trend === 'up' ? 'success' : 'warning'}
              showIcon
            />
          </Card>

          {signals.length > 0 && (
            <Card title="历史信号记录">
              <Timeline>
                {signals.slice(0, 5).map((signal, index) => (
                  <Timeline.Item
                    key={index}
                    color={signal.signal === 'buy' ? 'green' : 'red'}
                  >
                    {signal.date} - {signal.signal === 'buy' ? '买入' : '卖出'}信号
                    （强度：{(signal.strength * 100).toFixed(0)}%，价格：¥{signal.price}）
                  </Timeline.Item>
                ))}
              </Timeline>
            </Card>
          )}
        </>
      )}
    </Space>
  )
}

export default AIPredict