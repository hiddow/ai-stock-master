import React, { useState, useEffect } from 'react'
import { Row, Col, Card, Statistic, Table, Tag, Space, Spin } from 'antd'
import { ArrowUpOutlined, ArrowDownOutlined, StockOutlined, TrophyOutlined } from '@ant-design/icons'
import axios from 'axios'
import * as echarts from 'echarts'
import ReactECharts from 'echarts-for-react'

const Dashboard = ({ onSelectStock }) => {
  const [loading, setLoading] = useState(false)
  const [marketData, setMarketData] = useState({
    totalStocks: 0,
    todayUp: 0,
    todayDown: 0,
    todayFlat: 0
  })
  const [hotStocks, setHotStocks] = useState([])
  const [recentSignals, setRecentSignals] = useState([])

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    setLoading(true)
    try {
      // 获取市场统计数据
      const statsRes = await axios.get('/api/data/status')
      setMarketData({
        totalStocks: statsRes.data.stock_count || 0,
        todayUp: Math.floor(Math.random() * 2000) + 1000,
        todayDown: Math.floor(Math.random() * 1500) + 500,
        todayFlat: Math.floor(Math.random() * 200) + 50
      })

      // 模拟热门股票数据
      setHotStocks([
        { code: '000001', name: '平安银行', price: 12.58, change: 2.35, volume: 158923 },
        { code: '000002', name: '万科A', price: 15.82, change: -1.25, volume: 235689 },
        { code: '000858', name: '五粮液', price: 168.35, change: 3.68, volume: 89562 },
        { code: '002415', name: '海康威视', price: 35.26, change: 1.85, volume: 125634 },
        { code: '600519', name: '贵州茅台', price: 1685.50, change: -0.58, volume: 45236 }
      ])

      // 模拟最近信号
      setRecentSignals([
        { stock: '平安银行', code: '000001', signal: 'buy', strength: 0.75, time: '10:30' },
        { stock: '招商银行', code: '600036', signal: 'sell', strength: 0.65, time: '11:15' },
        { stock: '中国平安', code: '601318', signal: 'buy', strength: 0.82, time: '14:20' }
      ])
    } catch (error) {
      console.error('获取数据失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const marketTrendOption = {
    title: {
      text: '市场趋势',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: ['9:30', '10:00', '10:30', '11:00', '11:30', '14:00', '14:30', '15:00']
    },
    yAxis: {
      type: 'value',
      name: '指数'
    },
    series: [
      {
        name: '上证指数',
        type: 'line',
        smooth: true,
        data: [3050, 3055, 3048, 3062, 3058, 3065, 3072, 3068],
        itemStyle: { color: '#1890ff' }
      },
      {
        name: '深证成指',
        type: 'line',
        smooth: true,
        data: [9850, 9862, 9845, 9878, 9865, 9882, 9895, 9888],
        itemStyle: { color: '#52c41a' }
      }
    ],
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    }
  }

  const distributionOption = {
    title: {
      text: '涨跌分布',
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
          position: 'outside'
        },
        data: [
          { value: marketData.todayUp, name: '上涨', itemStyle: { color: '#f5222d' } },
          { value: marketData.todayDown, name: '下跌', itemStyle: { color: '#52c41a' } },
          { value: marketData.todayFlat, name: '平盘', itemStyle: { color: '#999' } }
        ]
      }
    ]
  }

  const columns = [
    {
      title: '代码',
      dataIndex: 'code',
      key: 'code',
      render: (text) => <a>{text}</a>
    },
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name'
    },
    {
      title: '现价',
      dataIndex: 'price',
      key: 'price',
      align: 'right',
      render: (val) => <span style={{ fontWeight: 'bold' }}>{val.toFixed(2)}</span>
    },
    {
      title: '涨跌幅',
      dataIndex: 'change',
      key: 'change',
      align: 'right',
      render: (val) => (
        <span className={val > 0 ? 'price-up' : 'price-down'}>
          {val > 0 ? '+' : ''}{val.toFixed(2)}%
          {val > 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
        </span>
      )
    },
    {
      title: '成交量(手)',
      dataIndex: 'volume',
      key: 'volume',
      align: 'right',
      render: (val) => (val / 100).toFixed(0)
    }
  ]

  const signalColumns = [
    {
      title: '股票',
      key: 'stock',
      render: (_, record) => (
        <Space>
          <span>{record.stock}</span>
          <Tag color="blue">{record.code}</Tag>
        </Space>
      )
    },
    {
      title: '信号',
      dataIndex: 'signal',
      key: 'signal',
      render: (val) => (
        <Tag color={val === 'buy' ? 'green' : 'red'}>
          {val === 'buy' ? '买入' : '卖出'}
        </Tag>
      )
    },
    {
      title: '强度',
      dataIndex: 'strength',
      key: 'strength',
      render: (val) => (
        <div style={{ width: 60 }}>
          <div style={{
            width: `${val * 100}%`,
            height: 4,
            background: val > 0.7 ? '#52c41a' : val > 0.4 ? '#faad14' : '#999',
            borderRadius: 2
          }} />
          <span style={{ fontSize: 12 }}>{(val * 100).toFixed(0)}%</span>
        </div>
      )
    },
    {
      title: '时间',
      dataIndex: 'time',
      key: 'time'
    }
  ]

  return (
    <Spin spinning={loading}>
      <div className="fade-in">
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} lg={6}>
            <Card className="stat-card">
              <Statistic
                title="股票总数"
                value={marketData.totalStocks}
                prefix={<StockOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card className="stat-card">
              <Statistic
                title="今日上涨"
                value={marketData.todayUp}
                prefix={<ArrowUpOutlined />}
                valueStyle={{ color: '#f5222d' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card className="stat-card">
              <Statistic
                title="今日下跌"
                value={marketData.todayDown}
                prefix={<ArrowDownOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card className="stat-card">
              <Statistic
                title="今日平盘"
                value={marketData.todayFlat}
                prefix={<TrophyOutlined />}
                valueStyle={{ color: '#999' }}
              />
            </Card>
          </Col>
        </Row>

        <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
          <Col xs={24} lg={14}>
            <Card title="市场走势" className="chart-container">
              <ReactECharts option={marketTrendOption} style={{ height: 300 }} />
            </Card>
          </Col>
          <Col xs={24} lg={10}>
            <Card title="涨跌分布" className="chart-container">
              <ReactECharts option={distributionOption} style={{ height: 300 }} />
            </Card>
          </Col>
        </Row>

        <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
          <Col xs={24} lg={12}>
            <Card title="热门股票" extra={<a>更多</a>}>
              <Table
                columns={columns}
                dataSource={hotStocks}
                rowKey="code"
                pagination={false}
                size="small"
                onRow={(record) => ({
                  onClick: () => onSelectStock(record),
                  style: { cursor: 'pointer' }
                })}
              />
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            <Card title="最新信号" extra={<a>更多</a>}>
              <Table
                columns={signalColumns}
                dataSource={recentSignals}
                rowKey={(record) => `${record.code}-${record.time}`}
                pagination={false}
                size="small"
              />
            </Card>
          </Col>
        </Row>
      </div>
    </Spin>
  )
}

export default Dashboard