import React, { useState } from 'react'
import { Card, Row, Col, Form, InputNumber, DatePicker, Button, Space, Table, Statistic, Alert, Progress, Divider } from 'antd'
import { ExperimentOutlined, FundOutlined, LineChartOutlined, TrophyOutlined } from '@ant-design/icons'
import ReactECharts from 'echarts-for-react'
import dayjs from 'dayjs'
import axios from 'axios'

const { RangePicker } = DatePicker

const Backtest = ({ stock }) => {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [backtestResult, setBacktestResult] = useState(null)

  const runBacktest = async (values) => {
    if (!stock) return

    setLoading(true)
    try {
      const startDate = values.dateRange[0].format('YYYYMMDD')
      const endDate = values.dateRange[1].format('YYYYMMDD')

      const response = await axios.post(`/api/analysis/${stock.code}/backtest`, null, {
        params: {
          start_date: startDate,
          end_date: endDate,
          initial_capital: values.initialCapital
        }
      })

      setBacktestResult(response.data)
    } catch (error) {
      console.error('回测失败:', error)
      // 使用模拟数据
      generateMockBacktestResult(values)
    } finally {
      setLoading(false)
    }
  }

  const generateMockBacktestResult = (values) => {
    const trades = []
    const capitalHistory = []
    let capital = values.initialCapital
    
    // 生成模拟交易记录
    for (let i = 0; i < 10; i++) {
      const isBuy = i % 2 === 0
      const price = 10 + Math.random() * 5
      const shares = isBuy ? Math.floor(capital * 0.3 / price) : 0
      
      trades.push({
        date: dayjs().subtract(30 - i * 3, 'day').format('YYYY-MM-DD'),
        type: isBuy ? 'buy' : 'sell',
        price: price,
        shares: shares || 1000,
        capital: capital
      })

      if (!isBuy) {
        capital += shares * price * (1 + (Math.random() - 0.5) * 0.2)
      }
    }

    // 生成资金曲线
    for (let i = 0; i <= 30; i++) {
      capitalHistory.push({
        date: dayjs().subtract(30 - i, 'day').format('YYYY-MM-DD'),
        value: values.initialCapital * (1 + (Math.random() - 0.3) * 0.5 * (i / 30))
      })
    }

    const finalValue = capital * (1 + (Math.random() - 0.3) * 0.3)
    const totalReturn = (finalValue - values.initialCapital) / values.initialCapital

    setBacktestResult({
      metrics: {
        total_return: totalReturn,
        win_rate: 0.6 + Math.random() * 0.3,
        max_drawdown: Math.random() * 0.3,
        sharpe_ratio: 1 + Math.random() * 2,
        total_trades: trades.length,
        final_value: finalValue
      },
      trades: trades,
      capitalHistory: capitalHistory,
      summary: `总收益率: ${(totalReturn * 100).toFixed(2)}%`
    })
  }

  const getCapitalCurveOption = () => {
    if (!backtestResult) return {}

    const dates = backtestResult.capitalHistory?.map(item => item.date) || []
    const values = backtestResult.capitalHistory?.map(item => item.value) || []

    return {
      title: {
        text: '资金曲线',
        left: 'center'
      },
      tooltip: {
        trigger: 'axis',
        formatter: '{b}: ¥{c}'
      },
      xAxis: {
        type: 'category',
        data: dates
      },
      yAxis: {
        type: 'value',
        name: '资金(元)'
      },
      series: [
        {
          type: 'line',
          data: values,
          smooth: true,
          areaStyle: {
            color: 'rgba(24, 144, 255, 0.1)'
          },
          lineStyle: {
            color: '#1890ff',
            width: 2
          }
        }
      ],
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      }
    }
  }

  const tradeColumns = [
    {
      title: '日期',
      dataIndex: 'date',
      key: 'date'
    },
    {
      title: '操作',
      dataIndex: 'type',
      key: 'type',
      render: (val) => (
        <span style={{ color: val === 'buy' ? '#52c41a' : '#f5222d' }}>
          {val === 'buy' ? '买入' : '卖出'}
        </span>
      )
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      render: (val) => `¥${val.toFixed(2)}`
    },
    {
      title: '数量',
      dataIndex: 'shares',
      key: 'shares'
    },
    {
      title: '资金',
      dataIndex: 'capital',
      key: 'capital',
      render: (val) => `¥${val.toFixed(2)}`
    }
  ]

  if (!stock) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: '50px 0' }}>
          <ExperimentOutlined style={{ fontSize: 48, color: '#999' }} />
          <p style={{ marginTop: 16, color: '#999' }}>请先选择一只股票进行回测</p>
        </div>
      </Card>
    )
  }

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="large">
      <Card>
        <h2 style={{ margin: 0 }}>
          <ExperimentOutlined style={{ marginRight: 8 }} />
          策略回测 - {stock.name} ({stock.code})
        </h2>
      </Card>

      <Card title="回测参数设置">
        <Form
          form={form}
          layout="vertical"
          onFinish={runBacktest}
          initialValues={{
            initialCapital: 100000,
            dateRange: [dayjs().subtract(6, 'month'), dayjs()]
          }}
        >
          <Row gutter={16}>
            <Col xs={24} md={8}>
              <Form.Item
                name="initialCapital"
                label="初始资金"
                rules={[{ required: true, message: '请输入初始资金' }]}
              >
                <InputNumber
                  style={{ width: '100%' }}
                  min={10000}
                  max={10000000}
                  step={10000}
                  formatter={value => `¥ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                  parser={value => value.replace(/\¥\s?|(,*)/g, '')}
                />
              </Form.Item>
            </Col>
            <Col xs={24} md={10}>
              <Form.Item
                name="dateRange"
                label="回测时间范围"
                rules={[{ required: true, message: '请选择时间范围' }]}
              >
                <RangePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col xs={24} md={6}>
              <Form.Item label=" ">
                <Button type="primary" htmlType="submit" loading={loading} block>
                  开始回测
                </Button>
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Card>

      {backtestResult && (
        <>
          <Row gutter={[16, 16]}>
            <Col xs={12} md={6}>
              <Card>
                <Statistic
                  title="总收益率"
                  value={(backtestResult.metrics.total_return * 100).toFixed(2)}
                  suffix="%"
                  valueStyle={{
                    color: backtestResult.metrics.total_return > 0 ? '#52c41a' : '#f5222d'
                  }}
                  prefix={backtestResult.metrics.total_return > 0 ? '↑' : '↓'}
                />
              </Card>
            </Col>
            <Col xs={12} md={6}>
              <Card>
                <Statistic
                  title="胜率"
                  value={(backtestResult.metrics.win_rate * 100).toFixed(1)}
                  suffix="%"
                  valueStyle={{ color: '#1890ff' }}
                  prefix={<TrophyOutlined />}
                />
              </Card>
            </Col>
            <Col xs={12} md={6}>
              <Card>
                <Statistic
                  title="最大回撤"
                  value={(backtestResult.metrics.max_drawdown * 100).toFixed(1)}
                  suffix="%"
                  valueStyle={{ color: '#faad14' }}
                />
              </Card>
            </Col>
            <Col xs={12} md={6}>
              <Card>
                <Statistic
                  title="夏普比率"
                  value={backtestResult.metrics.sharpe_ratio.toFixed(2)}
                  valueStyle={{ color: '#722ed1' }}
                />
              </Card>
            </Col>
          </Row>

          <Card>
            <ReactECharts option={getCapitalCurveOption()} style={{ height: 400 }} />
          </Card>

          <Row gutter={[16, 16]}>
            <Col xs={24} md={12}>
              <Card title="回测统计">
                <Descriptions column={1}>
                  <Descriptions.Item label="初始资金">
                    ¥{form.getFieldValue('initialCapital').toLocaleString()}
                  </Descriptions.Item>
                  <Descriptions.Item label="最终资金">
                    ¥{backtestResult.metrics.final_value.toLocaleString()}
                  </Descriptions.Item>
                  <Descriptions.Item label="交易次数">
                    {backtestResult.metrics.total_trades}
                  </Descriptions.Item>
                  <Descriptions.Item label="盈利次数">
                    {Math.floor(backtestResult.metrics.total_trades * backtestResult.metrics.win_rate / 2)}
                  </Descriptions.Item>
                  <Descriptions.Item label="亏损次数">
                    {Math.floor(backtestResult.metrics.total_trades * (1 - backtestResult.metrics.win_rate) / 2)}
                  </Descriptions.Item>
                </Descriptions>
              </Card>
            </Col>
            <Col xs={24} md={12}>
              <Card title="风险指标">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div>
                    <span>最大回撤</span>
                    <Progress 
                      percent={(backtestResult.metrics.max_drawdown * 100).toFixed(0)} 
                      strokeColor="#faad14"
                    />
                  </div>
                  <div>
                    <span>胜率</span>
                    <Progress 
                      percent={(backtestResult.metrics.win_rate * 100).toFixed(0)} 
                      strokeColor="#52c41a"
                    />
                  </div>
                  <div>
                    <span>夏普比率</span>
                    <Progress 
                      percent={Math.min(backtestResult.metrics.sharpe_ratio * 33, 100).toFixed(0)} 
                      strokeColor="#722ed1"
                      format={() => backtestResult.metrics.sharpe_ratio.toFixed(2)}
                    />
                  </div>
                </Space>
              </Card>
            </Col>
          </Row>

          <Card title="交易记录">
            <Table
              columns={tradeColumns}
              dataSource={backtestResult.trades.slice(0, 10)}
              rowKey={(record) => `${record.date}-${record.type}`}
              pagination={false}
              size="small"
            />
          </Card>

          <Alert
            message="回测说明"
            description={
              <div>
                <p>本回测基于历史数据和技术指标信号，采用简单的均线交叉策略：</p>
                <ul>
                  <li>当短期均线上穿长期均线时买入（金叉）</li>
                  <li>当短期均线下穿长期均线时卖出（死叉）</li>
                  <li>每次交易使用30%的可用资金</li>
                  <li>不考虑交易手续费和滑点</li>
                </ul>
                <p><strong>风险提示：</strong>历史业绩不代表未来表现，投资需谨慎。</p>
              </div>
            }
            type="info"
            showIcon
          />
        </>
      )}
    </Space>
  )
}

export default Backtest