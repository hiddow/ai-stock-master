import React from 'react'
import { Card } from 'antd'

const StockDetail = ({ code }) => {
  return (
    <Card>
      <h2>股票详情: {code}</h2>
      <p>详细信息展示...</p>
    </Card>
  )
}

export default StockDetail