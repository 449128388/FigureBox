<!--
  QuickSellDialog.vue - 快速卖出弹窗组件

  功能说明：
  - 展示当前持仓信息（手办名称、库存、成本价、市场价）
  - 输入卖出数量和卖出价格
  - 预览预计收入和预计盈亏
  - 支持使用当前市价快速填充
  - 确认后执行卖出操作并联动更新所有相关模块

  组件依赖：
  - 使用 useQuickSell composable 处理业务逻辑
  - 触发 sell-success 事件给父组件

  维护提示：
  - 盈亏计算 = (卖出价 - 成本价) × 卖出数量
  - 卖出后会更新库存账、交易记录、仓位管理和总资产
-->
<template>
  <el-dialog
    v-model="dialogVisible"
    :title="dialogTitle"
    width="500px"
    class="quick-sell-dialog"
    :close-on-click-modal="false"
    @close="closeDialog"
  >
    <div v-if="currentFigure" class="dialog-content">
      <!-- 当前持仓信息 -->
      <div class="current-info">
        <div class="info-row">
          <span class="info-label">当前持仓:</span>
          <span class="info-value">{{ formatNumber(currentFigure.stock || 0) }}体</span>
        </div>
        <div class="info-row">
          <span class="info-label">当前均价:</span>
          <span class="info-value">{{ formatMoney(currentFigure.cost_price || 0) }}/体</span>
        </div>
        <div class="info-row">
          <span class="info-label">当前市值:</span>
          <span class="info-value">{{ formatMoney(currentFigure.current_price || 0) }}/体</span>
        </div>
      </div>

      <el-divider />

      <!-- 卖出输入 -->
      <div class="sell-form">
        <div class="form-item">
          <span class="form-label">卖出数量:</span>
          <el-input-number
            v-model="sellQuantity"
            :min="1"
            :max="currentFigure.stock || 1"
            :precision="0"
            :step="1"
            controls-position="right"
            class="form-input"
          />
          <span class="form-unit">体</span>
          <el-button
            v-if="currentFigure.stock > 1"
            type="primary"
            link
            size="small"
            class="all-btn"
            @click="sellQuantity = currentFigure.stock"
          >
            (全部)
          </el-button>
        </div>

        <div class="form-item">
          <span class="form-label">卖出价格:</span>
          <el-input-number
            v-model="sellPrice"
            :min="0"
            :precision="2"
            :step="100"
            controls-position="right"
            class="form-input"
          />
          <span class="form-unit">¥/体</span>
        </div>

        <div class="form-hint">
          <el-button type="primary" link size="small" @click="useCurrentMarketPrice">
            [使用当前市价]
          </el-button>
        </div>
      </div>

      <el-divider />

      <!-- 卖出预览 -->
      <div v-if="sellPreview" class="preview-section">
        <div class="preview-item">
          <span class="preview-label">预计收入:</span>
          <span class="preview-value highlight">{{ formatMoney(sellPreview.totalRevenue) }}</span>
        </div>
        <div class="preview-item">
          <span class="preview-label">预计盈亏:</span>
          <span
            class="preview-value"
            :class="{ profit: sellPreview.profit >= 0, loss: sellPreview.profit < 0 }"
          >
            {{ sellPreview.profit >= 0 ? '+' : '' }}{{ formatMoney(sellPreview.profit) }}
            ({{ sellPreview.profit >= 0 ? '+' : '' }}{{ sellPreview.profitPercentage.toFixed(0) }}%)
          </span>
        </div>
      </div>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="closeDialog">取消</el-button>
        <el-button type="primary" @click="handleConfirmClick" :loading="loading">
          确认卖出
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script>
import { useQuickSell } from '../../../composables/useQuickSell'

export default {
  name: 'QuickSellDialog',
  emits: ['sell-success'],
  setup(props, { emit }) {
    const {
      dialogVisible,
      dialogTitle,
      loading,
      currentFigure,
      sellQuantity,
      sellPrice,
      sellPreview,
      openDialog,
      closeDialog,
      confirmSell,
      useCurrentMarketPrice,
      formatMoney,
      formatNumber
    } = useQuickSell()

    // 包装确认卖出方法，添加成功回调
    const handleConfirm = async () => {
      const result = await confirmSell()
      if (result) {
        emit('sell-success', result)
      }
    }

    // 处理按钮点击事件
    const handleConfirmClick = () => {
      handleConfirm()
    }

    // 暴露 openDialog 方法给父组件
    const exposedOpenDialog = (item) => {
      openDialog(item)
    }

    return {
      dialogVisible,
      dialogTitle,
      loading,
      currentFigure,
      sellQuantity,
      sellPrice,
      sellPreview,
      openDialog: exposedOpenDialog,
      closeDialog,
      confirmSell: handleConfirm,
      useCurrentMarketPrice,
      handleConfirmClick,
      formatMoney,
      formatNumber
    }
  }
}
</script>

<style scoped>
.quick-sell-dialog {
  padding: 10px 0;
}

.dialog-content {
  padding: 10px 10px;
  min-height: 300px;
}

.current-info {
  margin-bottom: 20px;
}

.info-row {
  display: flex;
  margin-bottom: 10px;
  font-size: 14px;
  gap: 12px;
}

.info-label {
  color: #606266;
  min-width: 70px;
}

.info-value {
  color: #303133;
  font-weight: 500;
}

.sell-form {
  margin-bottom: 20px;
}

.form-item {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  gap: 8px;
}

.form-label {
  color: #606266;
  min-width: 70px;
  font-size: 14px;
}

.form-input {
  width: 140px;
}

.form-unit {
  color: #909399;
  font-size: 14px;
}

.all-btn {
  margin-left: 4px;
}

.form-hint {
  margin-left: 78px;
  margin-top: -8px;
}

.preview-section {
  background-color: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
}

.preview-item {
  display: flex;
  margin-bottom: 10px;
  font-size: 14px;
  gap: 12px;
}

.preview-item:last-child {
  margin-bottom: 0;
}

.preview-label {
  color: #606266;
  min-width: 70px;
}

.preview-value {
  color: #303133;
  font-weight: 600;
}

.preview-value.highlight {
  color: #409eff;
}

/* 中国股市颜色规范：盈利红色，亏损绿色 */
.preview-value.profit {
  color: #f56c6c;
}

.preview-value.loss {
  color: #67c23a;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
