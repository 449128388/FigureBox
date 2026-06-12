<!--
  QuickActions.vue - 快速操作组件

  功能说明：
  - 提供交易相关的快速操作按钮
  - 采用低饱和填充卡片风格，图标+主副双行文字
  - 与交易流水卡片、筛选标签风格一致

  组件依赖：
  - 无外部组件依赖
  - 使用 Element Plus 图标组件

  维护提示：
  - 点击事件通过 $emit 传递给父组件
  - 按钮样式根据操作类型区分颜色
-->
<template>
  <div class="quick-actions">
    <h4 class="section-title">快速操作</h4>
    <div class="actions-grid">
      <!-- 买入·新增预定 -->
      <div
        class="action-card action-buy"
        @click="$emit('open-buy-dialog')"
      >
        <div class="action-icon">
          <el-icon><Plus /></el-icon>
        </div>
        <div class="action-main">买入</div>
        <div class="action-sub">新增预定</div>
      </div>

      <!-- 卖出·标记转卖 -->
      <div
        class="action-card action-sell"
        @click="$emit('open-sell-dialog')"
      >
        <div class="action-icon">
          <el-icon><PriceTag /></el-icon>
        </div>
        <div class="action-main">卖出</div>
        <div class="action-sub">标记转卖</div>
      </div>

      <!-- 补款·支付尾款 -->
      <div
        class="action-card action-payment"
        @click="$emit('open-payment-dialog')"
      >
        <div class="action-icon">
          <el-icon><Money /></el-icon>
        </div>
        <div class="action-main">补款</div>
        <div class="action-sub">支付尾款</div>
      </div>

      <!-- 撤单·取消订单 -->
      <div
        class="action-card action-cancel"
        @click="handleCancelClick"
      >
        <div class="action-icon">
          <el-icon><Delete /></el-icon>
        </div>
        <div class="action-main">撤单</div>
        <div class="action-sub">取消订单</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Plus, PriceTag, Money, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

defineEmits(['open-buy-dialog', 'open-sell-dialog', 'open-payment-dialog'])

const handleCancelClick = () => {
  ElMessage.info('功能正在开发中')
}
</script>

<style scoped>
/* 快速操作区域 */
.quick-actions {
  margin-bottom: 20px;
  background-color: white;
  border-radius: 8px;
  padding: 16px 20px;
}

.section-title {
  margin: 0 0 16px 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

/* 操作按钮网格布局 */
.actions-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

/* 操作卡片基础样式 */
.action-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 16px 8px;
  border-radius: 8px;
  border: 1px solid;
  cursor: pointer;
  transition: all 0.2s ease;
  height: 72px;
}

/* 图标样式 */
.action-icon {
  font-size: 20px;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-icon .el-icon {
  width: 20px;
  height: 20px;
}

/* 主操作文字 */
.action-main {
  font-size: 14px;
  font-weight: 600;
  line-height: 1.4;
}

/* 副文案 */
.action-sub {
  font-size: 12px;
  line-height: 1.3;
  margin-top: 2px;
}

/* 买入·新增预定 - 极浅蓝 */
.action-buy {
  background-color: #E6F7FF;
  border-color: #91D5FF;
  color: #1890FF;
}

.action-buy .action-sub {
  color: #1890FF;
  opacity: 0.8;
}

.action-buy:hover {
  background-color: #BAE7FF;
}

/* 卖出·标记转卖 - 极浅红 */
.action-sell {
  background-color: #FFF2F0;
  border-color: #FFCCC7;
  color: #CF1322;
}

.action-sell .action-sub {
  color: #CF1322;
  opacity: 0.8;
}

.action-sell:hover {
  background-color: #FFCCC7;
}

/* 补款·支付尾款 - 极浅橙 */
.action-payment {
  background-color: #FFF7E6;
  border-color: #FFD591;
  color: #FA8C16;
}

.action-payment .action-sub {
  color: #FA8C16;
  opacity: 0.8;
}

.action-payment:hover {
  background-color: #FFE7BA;
}

/* 撤单·取消订单 - 浅灰 */
.action-cancel {
  background-color: #F5F5F5;
  border-color: #D9D9D9;
  color: #8C8C8C;
}

.action-cancel .action-sub {
  color: #8C8C8C;
  opacity: 0.8;
}

.action-cancel:hover {
  background-color: #D9D9D9;
}

/* 响应式布局 */
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
