<template>
  <div class="quick-actions">
    <h4>快速操作</h4>
    <div class="actions-grid">
      <el-button type="primary" @click="$emit('open-buy-dialog')">
        <el-icon><Plus /></el-icon> 买入
        <div class="action-desc">新增预定</div>
      </el-button>
      <el-button type="success" @click="$emit('open-sell-dialog')">
        <el-icon><Minus /></el-icon> 卖出
        <div class="action-desc">标记转卖</div>
      </el-button>
      <el-button type="info" @click="$emit('open-payment-dialog')">
        <el-icon><Money /></el-icon> 补款
        <div class="action-desc">支付尾款</div>
      </el-button>
      <el-button type="danger" @click="$emit('open-cancel-dialog')">
        <el-icon><Close /></el-icon> 撤单
        <div class="action-desc">取消订单</div>
      </el-button>
    </div>
  </div>
</template>

<script>
import { Plus, Minus, Money, Close } from '@element-plus/icons-vue'

export default {
  name: 'QuickActions',
  components: {
    Plus,
    Minus,
    Money,
    Close
  },
  emits: ['open-buy-dialog', 'open-sell-dialog', 'open-payment-dialog', 'open-cancel-dialog']
}
</script>

<style scoped>
/* 快速操作 */
.quick-actions {
  margin-bottom: 30px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.quick-actions h4 {
  margin-bottom: 15px;
  color: #333;
  font-size: 16px;
  font-weight: bold;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
}

.actions-grid .el-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  padding: 20px;
  text-align: center;
  height: auto;
}

.actions-grid .el-button .el-icon {
  font-size: 24px;
  margin-bottom: 5px;
}

.action-desc {
  font-size: 12px;
  margin-top: 5px;
  opacity: 0.8;
}

@media (max-width: 1200px) {
  .actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .actions-grid {
    grid-template-columns: 1fr;
  }
}
</style>