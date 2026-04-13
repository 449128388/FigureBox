<template>
  <div class="trade-view">
    <!-- 本月交易统计 -->
    <TradeStats 
      :displayTradeData="displayTradeData" 
      :formatNumber="formatNumber" 
    />

    <!-- 快速操作 -->
    <QuickActions 
      @open-buy-dialog="$emit('open-buy-dialog')"
      @open-sell-dialog="$emit('open-sell-dialog')"
      @open-payment-dialog="$emit('open-payment-dialog')"
      @open-cancel-dialog="$emit('open-cancel-dialog')"
    />

    <!-- 交易流水 -->
    <TradeFlow 
      :tradeData="tradeData"
      :formatNumber="formatNumber"
      :getMockTradeData="getMockTradeData"
      @handle-trade-action="handleTradeAction"
    />

    <!-- 盈亏分析报表 -->
    <ProfitAnalysis 
      :displayTradeData="displayTradeData" 
      :formatNumber="formatNumber" 
    />
  </div>
</template>

<script>
import { computed } from 'vue'
import TradeStats from './trade/TradeStats.vue'
import QuickActions from './trade/QuickActions.vue'
import TradeFlow from './trade/TradeFlow.vue'
import ProfitAnalysis from './trade/ProfitAnalysis.vue'

export default {
  name: 'TradeView',
  components: {
    TradeStats,
    QuickActions,
    TradeFlow,
    ProfitAnalysis
  },
  props: {
    tradeData: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['open-buy-dialog', 'open-sell-dialog', 'open-payment-dialog', 'open-cancel-dialog', 'view-record', 'delete-record'],
  setup(props) {
    // 生成模拟数据
    const getMockTradeData = () => {
      return {
        monthly_stats: {
          buy_count: 3,
          buy_amount: 5600,
          sell_count: 2,
          sell_amount: 2400,
          net_cashflow: -3200
        },
        transactions: [
          {
            id: 1,
            date: '04-02 14:30',
            amount: -800,
            title: '买入: 初音未来 韶华 Ver. (尾款支付)',
            order_id: 'ORD20260402001',
            status: '✅ 成功',
            payment_method: '支付宝',
            merchant: 'AmiAmi',
            actions: ['查看订单', '申请售后', '下载电子发票']
          },
          {
            id: 2,
            date: '03-28 10:15',
            amount: 1200,
            title: '卖出: 蕾姆 婚纱 Ver.',
            buyer: '闲鱼用户_xxx',
            platform: '闲鱼',
            status: '✅ 已到账',
            fee: 7.2,
            net_profit: 292.8,
            actions: ['查看买家信息', '物流信息', '评价']
          },
          {
            id: 3,
            date: '03-20 09:00',
            amount: -200,
            title: '定金: Saber 礼服 Ver. (预定锁定)',
            status: '⏳ 持有中',
            estimated_payment: '2026-06',
            actions: ['补款提醒设置', '转让定金', '放弃定金']
          }
        ],
        profit_analysis: {
          yearly_profit: 3400,
          win_rate: 66.7,
          win_count: 4,
          loss_count: 2,
          avg_profit: 850,
          avg_loss: 200,
          max_profit: 1200,
          max_profit_item: '初音韶华',
          max_loss: 200,
          max_loss_item: '蕾姆'
        }
      }
    }
    
    const formatNumber = (num) => {
      return num?.toLocaleString() || '0'
    }
    
    const handleTradeAction = (action, record) => {
      // 处理交易操作
      console.log(`执行交易操作: ${action}`, record)
    }
    
    // 计算显示的交易数据（优先使用真实数据，无数据时使用模拟数据）
    const displayTradeData = computed(() => {
      if (props.tradeData && Object.keys(props.tradeData).length > 0) {
        return props.tradeData
      }
      return getMockTradeData()
    })
    
    return {
      formatNumber,
      handleTradeAction,
      displayTradeData,
      getMockTradeData
    }
  }
}
</script>

<style scoped>
.trade-view {
  width: 100%;
}
</style>