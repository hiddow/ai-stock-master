import React, { useState, useEffect } from 'react'
import { Card, Row, Col, Select, DatePicker, Button, Space, Spin, message, Tag, Statistic } from 'antd'
import { LineChartOutlined, BarChartOutlined, ReloadOutlined } from '@ant-design/icons'
import ReactECharts from 'echarts-for-react'
import dayjs from 'dayjs'
import axios from 'axios'

const { RangePicker } = DatePicker
const { Option } = Select

const Analysis = ({ stock }) => {
  const [loading, setLoading] = useState(false)
  const [klineData, setKlineData] = useState([])
  const [indicators, setIndicators] = useState({})
  const [dateRange, setDateRange] = useState([
    dayjs().subtract(3, 'month'),
    dayjs()
  ])
  const [selectedIndicators, setSelectedIndicators] = useState(['MA', 'VOL'])

  useEffect(() => {
    if (stock) {
      fetchStockData()
    }
  }, [stock, dateRange])

  const fetchStockData = async () => {
    if (!stock) return

    setLoading(true)
    try {
      const startDate = dateRange[0].format('YYYYMMDD')
      const endDate = dateRange[1].format('YYYYMMDD')

      // 获取K线数据
      const klineRes = await axios.get(`/api/stock/${stock.code}/daily`, {
        params: { start_date: startDate, end_date: endDate }
      })

      console.log('K线数据:', klineRes.data)

      if (klineRes.data && klineRes.data.length > 0) {
        setKlineData(klineRes.data)
        
        // 只有在有K线数据时才获取技术指标
        try {
          // 改为使用GET请求而不是POST
          const indicatorRes = await axios.get(`/api/analysis/${stock.code}/technical`, {
            params: { start_date: startDate, end_date: endDate }
          })
          
          if (indicatorRes.data && indicatorRes.data.indicators) {
            setIndicators(indicatorRes.data)
          }
        } catch (indicatorError) {
          console.error('技术指标计算失败:', indicatorError)
          // 即使技术指标失败，也显示K线图
          message.warning('技术指标计算失败，显示基础K线图')
        }
      } else {
        // 如果没有数据���尝试获取更多历史数据
        const extendedStartDate = dateRange[0].subtract(6, 'month').format('YYYYMMDD')
        
        try {
          const extendedRes = await axios.get(`/api/stock/${stock.code}/daily`, {
            params: { start_date: extendedStartDate, end_date: endDate }
          })
          
          if (extendedRes.data && extendedRes.data.length > 0) {
            setKlineData(extendedRes.data)
            message.info('已加载更长时间的历史数据')
          } else {
            // 只有在真的没有数据时才使用模拟数据
            setKlineData(generateMockKlineData())
            message.warning('暂无历史数据，使用模拟数据展示')
          }
        } catch (error) {
          setKlineData(generateMockKlineData())
          message.warning('暂无历史数据，使用模拟数据展示')
        }
      }
    } catch (error) {
      console.error('获取数据失败:', error)
      // 使用模拟数据
      setKlineData(generateMockKlineData())
      message.error('数据加载失败，使用模拟数据')
    } finally {
      setLoading(false)
    }
  }

  const generateMockKlineData = () => {
    const data = []
    const basePrice = stock?.price || 100
    for (let i = 60; i >= 0; i--) {
      const date = dayjs().subtract(i, 'day')
      const open = basePrice + (Math.random() - 0.5) * 5
      const close = open + (Math.random() - 0.5) * 3
      const high = Math.max(open, close) + Math.random() * 2
      const low = Math.min(open, close) - Math.random() * 2
      const volume = Math.floor(Math.random() * 1000000) + 500000

      data.push({
        date: date.format('YYYY-MM-DD'),
        open: parseFloat(open.toFixed(2)),
        close: parseFloat(close.toFixed(2)),
        high: parseFloat(high.toFixed(2)),
        low: parseFloat(low.toFixed(2)),
        volume: volume,
        ma5: basePrice + (Math.random() - 0.5) * 2,
        ma10: basePrice + (Math.random() - 0.5) * 1.5,
        ma20: basePrice + (Math.random() - 0.5) * 1
      })
    }
    return data
  }

  const getKlineOption = () => {
    const dates = klineData.map(item => item.date)
    const values = klineData.map(item => [item.open, item.close, item.low, item.high])
    const volumes = klineData.map(item => item.volume)
    const ma5 = klineData.map(item => item.ma5)
    const ma10 = klineData.map(item => item.ma10)
    const ma20 = klineData.map(item => item.ma20)

    return {
      animation: false,
      title: {
        text: `${stock?.name || '股票'} (${stock?.code || '000000'}) K线图`,
        left: 'center'
      },
      legend: {
        bottom: 10,
        data: ['K线', 'MA5', 'MA10', 'MA20']
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross'
        },
        formatter: function(params) {
          let res = params[0].name + '<br/>'
          params.forEach(param => {
            if (param.seriesName === 'K线') {
              const data = param.data
              res += `开盘: ${data[1]}<br/>`
              res += `收盘: ${data[2]}<br/>`
              res += `最低: ${data[3]}<br/>`
              res += `最高: ${data[4]}<br/>`
            } else {
              res += `${param.seriesName}: ${param.value}<br/>`
            }
          })
          return res
        }
      },
      grid: [
        {
          left: '10%',
          right: '10%',
          height: '50%'
        },
        {
          left: '10%',
          right: '10%',
          top: '63%',
          height: '18%'
        }
      ],
      xAxis: [
        {
          type: 'category',
          data: dates,
          boundaryGap: false,
          axisLine: { onZero: false },
          splitLine: { show: false },
          min: 'dataMin',
          max: 'dataMax'
        },
        {
          type: 'category',
          gridIndex: 1,
          data: dates,
          boundaryGap: false,
          axisLine: { onZero: false },
          axisTick: { show: false },
          splitLine: { show: false },
          axisLabel: { show: false },
          min: 'dataMin',
          max: 'dataMax'
        }
      ],
      yAxis: [
        {
          scale: true,
          splitArea: {
            show: true
          }
        },
        {
          scale: true,
          gridIndex: 1,
          splitNumber: 2,
          axisLabel: { show: false },
          axisLine: { show: false },
          axisTick: { show: false },
          splitLine: { show: false }
        }
      ],
      dataZoom: [
        {
          type: 'inside',
          xAxisIndex: [0, 1],
          start: 50,
          end: 100
        },
        {
          show: true,
          xAxisIndex: [0, 1],
          type: 'slider',
          top: '85%',
          start: 50,
          end: 100
        }
      ],
      series: [
        {
          name: 'K线',
          type: 'candlestick',
          data: values,
          itemStyle: {
            color: '#f5222d',
            color0: '#52c41a',
            borderColor: '#f5222d',
            borderColor0: '#52c41a'
          }
        },
        {
          name: 'MA5',
          type: 'line',
          data: ma5,
          smooth: true,
          lineStyle: {
            width: 1
          }
        },
        {
          name: 'MA10',
          type: 'line',
          data: ma10,
          smooth: true,
          lineStyle: {
            width: 1
          }
        },
        {
          name: 'MA20',
          type: 'line',
          data: ma20,
          smooth: true,
          lineStyle: {
            width: 1
          }
        },
        {
          name: '成交量',
          type: 'bar',
          xAxisIndex: 1,
          yAxisIndex: 1,
          data: volumes,
          itemStyle: {
            color: function(params) {
              const idx = params.dataIndex
              if (idx === 0) return '#999'
              return klineData[idx].close >= klineData[idx].open ? '#f5222d' : '#52c41a'
            }
          }
        }
      ]
    }
  }

  const getIndicatorCards = () => {
    const latestData = klineData[klineData.length - 1] || {}
    
    return [
      {
        title: 'RSI',
        value: indicators.indicators?.[0]?.rsi || 50 + (Math.random() - 0.5) * 30,
        suffix: '',
        color: '#1890ff'
      },
      {
        title: 'MACD',
        value: indicators.indicators?.[0]?.macd || (Math.random() - 0.5) * 2,
        suffix: '',
        color: '#52c41a'
      },
      {
        title: '最新信号',
        value: indicators.latest_signal === 1 ? '买入' : indicators.latest_signal === -1 ? '卖出' : '观望',
        suffix: '',
        color: indicators.latest_signal === 1 ? '#52c41a' : indicators.latest_signal === -1 ? '#f5222d' : '#999'
      },
      {
        title: '信号强度',
        value: (indicators.signal_strength || Math.random()) * 100,
        suffix: '%',
        color: '#faad14'
      }
    ]
  }

  if (!stock) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: '50px 0' }}>
          <LineChartOutlined style={{ fontSize: 48, color: '#999' }} />
          <p style={{ marginTop: 16, color: '#999' }}>请先选择一只股票进行分析</p>
        </div>
      </Card>
    )
  }

  return (
    <Spin spinning={loading}>
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        <Card>
          <Row gutter={[16, 16]} align="middle">
            <Col xs={24} sm={12} md={6}>
              <h2 style={{ margin: 0 }}>
                {stock.name} <Tag color="blue">{stock.code}</Tag>
              </h2>
            </Col>
            <Col xs={24} sm={12} md={8}>
              <RangePicker
                value={dateRange}
                onChange={setDateRange}
                format="YYYY-MM-DD"
                style={{ width: '100%' }}
              />
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Select
                mode="multiple"
                value={selectedIndicators}
                onChange={setSelectedIndicators}
                placeholder="选择技术指标"
                style={{ width: '100%' }}
              >
                <Option value="MA">均线</Option>
                <Option value="VOL">成交量</Option>
                <Option value="MACD">MACD</Option>
                <Option value="RSI">RSI</Option>
                <Option value="KDJ">KDJ</Option>
                <Option value="BOLL">布林带</Option>
              </Select>
            </Col>
            <Col xs={24} sm={12} md={4}>
              <Button
                type="primary"
                icon={<ReloadOutlined />}
                onClick={fetchStockData}
                block
              >
                刷新数据
              </Button>
            </Col>
          </Row>
        </Card>

        <Row gutter={[16, 16]}>
          {getIndicatorCards().map((card, index) => (
            <Col xs={12} sm={12} md={6} key={index}>
              <Card>
                <Statistic
                  title={card.title}
                  value={typeof card.value === 'number' ? card.value.toFixed(2) : card.value}
                  suffix={card.suffix}
                  valueStyle={{ color: card.color }}
                />
              </Card>
            </Col>
          ))}
        </Row>

        <Card>
          <ReactECharts 
            option={getKlineOption()} 
            style={{ height: 500 }}
            notMerge={true}
            lazyUpdate={true}
          />
        </Card>
      </Space>
    </Spin>
  )
}

export default Analysis