import React, { useState, useEffect } from 'react'
import { Layout, Menu, theme, message } from 'antd'
import {
  StockOutlined,
  LineChartOutlined,
  RobotOutlined,
  ExperimentOutlined,
  DashboardOutlined,
  SettingOutlined,
  StarOutlined,
  BulbOutlined
} from '@ant-design/icons'
import Dashboard from './pages/Dashboard'
import StockList from './pages/StockList'
import StockDetail from './pages/StockDetail'
import Analysis from './pages/Analysis'
import AIPredict from './pages/AIPredict'
import Backtest from './pages/Backtest'
import WatchList from './pages/WatchList'
import GeminiAnalysis from './pages/GeminiAnalysis'
import './App.css'

const { Header, Content, Sider } = Layout

function App() {
  const [collapsed, setCollapsed] = useState(false)
  const [selectedKey, setSelectedKey] = useState('dashboard')
  const [selectedStock, setSelectedStock] = useState(null)
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken()

  const menuItems = [
    {
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: '仪表盘',
    },
    {
      key: 'watchlist',
      icon: <StarOutlined />,
      label: '我的关注',
    },
    {
      key: 'stocks',
      icon: <StockOutlined />,
      label: '股票列表',
    },
    {
      key: 'analysis',
      icon: <LineChartOutlined />,
      label: '技术分析',
    },
    {
      key: 'gemini',
      icon: <BulbOutlined />,
      label: 'Gemini AI',
    },
    {
      key: 'ai-predict',
      icon: <RobotOutlined />,
      label: 'AI预测',
    },
    {
      key: 'backtest',
      icon: <ExperimentOutlined />,
      label: '策略回测',
    },
  ]

  const renderContent = () => {
    switch (selectedKey) {
      case 'dashboard':
        return <Dashboard onSelectStock={handleSelectStock} />
      case 'watchlist':
        return <WatchList onSelectStock={handleSelectStock} />
      case 'stocks':
        return <StockList onSelectStock={handleSelectStock} />
      case 'analysis':
        return <Analysis stock={selectedStock} />
      case 'gemini':
        return <GeminiAnalysis stock={selectedStock} />
      case 'ai-predict':
        return <AIPredict stock={selectedStock} />
      case 'backtest':
        return <Backtest stock={selectedStock} />
      default:
        if (selectedKey.startsWith('stock-')) {
          return <StockDetail code={selectedKey.replace('stock-', '')} />
        }
        return <Dashboard />
    }
  }

  const handleSelectStock = (stock) => {
    setSelectedStock(stock)
    setSelectedKey('analysis')
    message.success(`已选择股票: ${stock.name} (${stock.code})`)
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider 
        collapsible 
        collapsed={collapsed} 
        onCollapse={setCollapsed}
        style={{
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
        }}
      >
        <div className="logo">
          <h2 style={{ color: 'white', textAlign: 'center', padding: '16px 0' }}>
            {collapsed ? 'AI' : 'AI炒股大师'}
          </h2>
        </div>
        <Menu
          theme="dark"
          selectedKeys={[selectedKey]}
          mode="inline"
          items={menuItems}
          onClick={({ key }) => setSelectedKey(key)}
        />
      </Sider>
      <Layout style={{ marginLeft: collapsed ? 80 : 200 }}>
        <Header
          style={{
            padding: '0 24px',
            background: colorBgContainer,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            boxShadow: '0 1px 4px rgba(0,0,0,0.08)'
          }}
        >
          <h1 style={{ margin: 0, fontSize: 20 }}>
            A股智能分析系统
          </h1>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            {selectedStock && (
              <span style={{ color: '#666' }}>
                当前选择: <strong>{selectedStock.name} ({selectedStock.code})</strong>
              </span>
            )}
            <SettingOutlined style={{ fontSize: 18, cursor: 'pointer' }} />
          </div>
        </Header>
        <Content
          style={{
            margin: '24px',
            padding: 24,
            minHeight: 280,
            background: colorBgContainer,
            borderRadius: borderRadiusLG,
          }}
        >
          {renderContent()}
        </Content>
      </Layout>
    </Layout>
  )
}

export default App