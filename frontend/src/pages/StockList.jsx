import React, { useState, useEffect } from 'react'
import { Table, Input, Button, Space, Tag, message, Card, Row, Col, Select } from 'antd'
import { SearchOutlined, ReloadOutlined, StarOutlined, StarFilled } from '@ant-design/icons'
import axios from 'axios'

const { Search } = Input
const { Option } = Select

const StockList = ({ onSelectStock }) => {
  const [stocks, setStocks] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchText, setSearchText] = useState('')
  const [filteredStocks, setFilteredStocks] = useState([])
  const [favorites, setFavorites] = useState([])
  const [selectedIndustry, setSelectedIndustry] = useState('all')

  useEffect(() => {
    fetchStocks()
    loadFavorites()
  }, [])

  useEffect(() => {
    filterStocks()
  }, [stocks, searchText, selectedIndustry])

  const fetchStocks = async () => {
    setLoading(true)
    try {
      const response = await axios.get('/api/stock/list')
      const stockData = response.data.length > 0 ? response.data : getMockStocks()
      setStocks(stockData)
      setFilteredStocks(stockData)
      message.success(`加载了 ${stockData.length} 只股票`)
    } catch (error) {
      console.error('获取股票列表失败:', error)
      message.warning('使用模拟数据展示')
      // 使用模拟数据
      const mockData = getMockStocks()
      setStocks(mockData)
      setFilteredStocks(mockData)
    } finally {
      setLoading(false)
    }
  }

  const getMockStocks = () => [
    { code: '000001', name: '平安银行', industry: '银行', price: 12.58, change: 2.35, pe: 5.8, pb: 0.68, marketCap: 2443 },
    { code: '000002', name: '万科A', industry: '房地产', price: 15.82, change: -1.25, pe: 6.2, pb: 0.82, marketCap: 1835 },
    { code: '000858', name: '五粮液', industry: '白酒', price: 168.35, change: 3.68, pe: 28.5, pb: 8.2, marketCap: 6532 },
    { code: '002415', name: '海康威视', industry: '电子', price: 35.26, change: 1.85, pe: 18.6, pb: 4.5, marketCap: 3296 },
    { code: '600519', name: '贵州茅台', industry: '白酒', price: 1685.50, change: -0.58, pe: 35.2, pb: 12.8, marketCap: 21168 },
    { code: '600036', name: '招商银行', industry: '银行', price: 35.82, change: 1.68, pe: 7.2, pb: 1.05, marketCap: 9035 },
    { code: '000333', name: '美的集团', industry: '家电', price: 58.65, change: 0.85, pe: 12.8, pb: 3.2, marketCap: 4108 },
    { code: '002594', name: '比亚迪', industry: '汽车', price: 285.36, change: 4.25, pe: 68.5, pb: 5.8, marketCap: 8296 },
    { code: '300750', name: '宁德时代', industry: '电池', price: 198.56, change: -2.15, pe: 42.3, pb: 6.5, marketCap: 8725 },
    { code: '601318', name: '中国平安', industry: '保险', price: 48.25, change: 0.95, pe: 8.5, pb: 0.95, marketCap: 8813 }
  ]

  const filterStocks = () => {
    let filtered = stocks

    // 按行业筛选
    if (selectedIndustry !== 'all') {
      filtered = filtered.filter(stock => stock.industry === selectedIndustry)
    }

    // 按搜索词筛选
    if (searchText) {
      filtered = filtered.filter(stock =>
        stock.code.includes(searchText) ||
        stock.name.toLowerCase().includes(searchText.toLowerCase())
      )
    }

    setFilteredStocks(filtered)
  }

  const loadFavorites = () => {
    const saved = localStorage.getItem('favorites')
    if (saved) {
      setFavorites(JSON.parse(saved))
    }
  }

  const toggleFavorite = (code) => {
    const newFavorites = favorites.includes(code)
      ? favorites.filter(c => c !== code)
      : [...favorites, code]
    
    setFavorites(newFavorites)
    localStorage.setItem('favorites', JSON.stringify(newFavorites))
    message.success(favorites.includes(code) ? '已取消收藏' : '已添加收藏')
  }

  const updateStockData = async (code) => {
    message.loading('正在更新数据...')
    try {
      const endDate = new Date().toISOString().slice(0, 10).replace(/-/g, '')
      const startDate = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
        .toISOString().slice(0, 10).replace(/-/g, '')
      
      await axios.post(`/api/data/update/daily/${code}`, null, {
        params: { start_date: startDate, end_date: endDate }
      })
      message.success('数据更新成功')
    } catch (error) {
      message.error('数据更新失败')
    }
  }

  const columns = [
    {
      title: '收藏',
      key: 'favorite',
      width: 60,
      fixed: 'left',
      render: (_, record) => (
        <Button
          type="text"
          icon={favorites.includes(record.code) ? <StarFilled style={{ color: '#faad14' }} /> : <StarOutlined />}
          onClick={(e) => {
            e.stopPropagation()
            toggleFavorite(record.code)
          }}
        />
      )
    },
    {
      title: '代码',
      dataIndex: 'code',
      key: 'code',
      width: 100,
      fixed: 'left',
      render: (text) => <Tag color="blue">{text}</Tag>
    },
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      width: 120,
      fixed: 'left',
      render: (text) => <strong>{text}</strong>
    },
    {
      title: '行业',
      dataIndex: 'industry',
      key: 'industry',
      width: 100,
      render: (text) => <Tag>{text}</Tag>
    },
    {
      title: '现价',
      dataIndex: 'price',
      key: 'price',
      width: 100,
      align: 'right',
      render: (val) => <span style={{ fontWeight: 'bold' }}>{val?.toFixed(2) || '-'}</span>
    },
    {
      title: '涨跌幅',
      dataIndex: 'change',
      key: 'change',
      width: 120,
      align: 'right',
      sorter: (a, b) => (a.change || 0) - (b.change || 0),
      render: (val) => (
        <span className={val > 0 ? 'price-up' : val < 0 ? 'price-down' : 'price-flat'}>
          {val > 0 && '+'}{val?.toFixed(2) || 0}%
        </span>
      )
    },
    {
      title: '市盈率',
      dataIndex: 'pe',
      key: 'pe',
      width: 100,
      align: 'right',
      sorter: (a, b) => (a.pe || 0) - (b.pe || 0),
      render: (val) => val?.toFixed(2) || '-'
    },
    {
      title: '市净率',
      dataIndex: 'pb',
      key: 'pb',
      width: 100,
      align: 'right',
      sorter: (a, b) => (a.pb || 0) - (b.pb || 0),
      render: (val) => val?.toFixed(2) || '-'
    },
    {
      title: '市值(亿)',
      dataIndex: 'marketCap',
      key: 'marketCap',
      width: 120,
      align: 'right',
      sorter: (a, b) => (a.marketCap || 0) - (b.marketCap || 0),
      render: (val) => val?.toFixed(0) || '-'
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Button 
            type="link" 
            size="small"
            onClick={(e) => {
              e.stopPropagation()
              onSelectStock(record)
            }}
          >
            分析
          </Button>
          <Button 
            type="link" 
            size="small"
            onClick={(e) => {
              e.stopPropagation()
              updateStockData(record.code)
            }}
          >
            更新
          </Button>
        </Space>
      )
    }
  ]

  const industries = ['all', '银行', '房地产', '白酒', '电子', '家电', '汽车', '电池', '保险']

  return (
    <Card>
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={24} sm={12} md={8}>
          <Search
            placeholder="输入股票代码或名称"
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            onSearch={filterStocks}
            enterButton={<SearchOutlined />}
          />
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Select
            style={{ width: '100%' }}
            value={selectedIndustry}
            onChange={setSelectedIndustry}
            placeholder="选择行业"
          >
            {industries.map(ind => (
              <Option key={ind} value={ind}>
                {ind === 'all' ? '全部行业' : ind}
              </Option>
            ))}
          </Select>
        </Col>
        <Col xs={24} sm={12} md={4}>
          <Button
            icon={<ReloadOutlined />}
            onClick={fetchStocks}
            loading={loading}
            block
          >
            刷新数据
          </Button>
        </Col>
      </Row>

      <Table
        columns={columns}
        dataSource={filteredStocks}
        rowKey="code"
        loading={loading}
        scroll={{ x: 1200 }}
        pagination={{
          pageSize: 20,
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 只股票`
        }}
        onRow={(record) => ({
          onClick: () => onSelectStock(record),
          style: { cursor: 'pointer' }
        })}
      />
    </Card>
  )
}

export default StockList