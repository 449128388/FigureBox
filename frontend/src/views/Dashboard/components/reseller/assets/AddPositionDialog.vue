<!--
  AddPositionDialog.vue - 补仓弹窗组件

  功能说明：
  - 展示当前持仓信息
  - 输入补仓数量和价格
  - 预览补仓后的成本价和库存
  - 确认后执行补仓操作

  组件依赖：
  - 使用 useAddPosition composable 处理业务逻辑
  - 触发 add-success 事件给父组件

  维护提示：
  - 成本价计算采用加权平均法
  - 补仓后库存数量相应增加
-->
<template>
  <el-dialog
    v-model="dialogVisible"
    title="补仓"
    width="550px"
    class="add-position-dialog"
    :close-on-click-modal="false"
    @close="closeDialog"
  >
    <div v-if="currentFigure" class="dialog-content">
      <!-- 当前持仓信息 -->
      <div class="current-info">
        <div class="info-row figure-name-row">
          <span class="info-label">手办名称:</span>
          <span class="info-value figure-name-value">{{ currentFigure.figure_name }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">当前持仓:</span>
          <span class="info-value">{{ formatNumber(currentFigure.stock || 1) }}体</span>
        </div>
        <div class="info-row">
          <span class="info-label">成本价:</span>
          <span class="info-value">{{ formatMoney(currentFigure.cost_price || 0) }}/体</span>
        </div>
        <div class="info-row market-value-row">
          <span class="info-label">当前市值:</span>
          <span class="info-value">{{ formatMoney((currentFigure.current_price || 0) * (currentFigure.stock || 1)) }}</span>
        </div>
      </div>

      <el-divider />

      <!-- 补仓输入 -->
      <div class="add-position-form">
        <div class="form-item">
          <span class="form-label">补仓数量:</span>
          <el-input-number
            v-model="addQuantity"
            :min="1"
            :precision="0"
            :step="1"
            controls-position="right"
            class="form-input"
          />
          <span class="form-unit">体</span>
        </div>

        <div class="form-item">
          <span class="form-label">补仓价格:</span>
          <el-input-number
            v-model="addPrice"
            :min="0"
            :precision="2"
            :step="100"
            controls-position="right"
            class="form-input"
          />
          <el-select v-model="addCurrency" class="currency-select" placeholder="币种">
            <el-option label="人民币" value="CNY" />
            <el-option label="日元" value="JPY" />
            <el-option label="美元" value="USD" />
            <el-option label="欧元" value="EUR" />
          </el-select>
          <span class="form-unit">/体</span>
        </div>

        <div class="form-hint">
          (请输入实际入手价格，将根据汇率转换为人民币计算)
        </div>
      </div>

      <el-divider />

      <!-- 补仓后预览 -->
      <div v-if="positionPreview" class="preview-section">
        <div class="preview-item">
          <span class="preview-label">补仓后成本:</span>
          <span class="preview-value">{{ formatMoney(positionPreview.newCostPrice) }}/体<span class="weighted-avg-note">(加权平均)</span></span>
        </div>
        <div class="preview-item">
          <span class="preview-label">补仓后库存:</span>
          <span class="preview-value">{{ formatNumber(positionPreview.newStock) }}体</span>
        </div>
      </div>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="closeDialog">取消</el-button>
        <el-button type="primary" @click="handleConfirmClick" :loading="loading">
          确认买入
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script>
import { useAddPosition } from '../../../composables/useAddPosition'

export default {
  name: 'AddPositionDialog',
  emits: ['add-success'],
  setup(props, { emit }) {
    const {
      dialogVisible,
      loading,
      currentFigure,
      addQuantity,
      addPrice,
      addCurrency,
      positionPreview,
      openDialog,
      closeDialog,
      confirmAddPosition,
      formatMoney,
      formatNumber
    } = useAddPosition()

    // 包装确认补仓方法，添加成功回调
    const handleConfirm = async () => {
      const result = await confirmAddPosition()
      if (result) {
        emit('add-success', result)
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
      loading,
      currentFigure,
      addQuantity,
      addPrice,
      addCurrency,
      positionPreview,
      openDialog: exposedOpenDialog,
      closeDialog,
      confirmAddPosition: handleConfirm,
      handleConfirmClick,
      formatMoney,
      formatNumber
    }
  }
}
</script>

<style scoped>
.add-position-dialog {
  padding: 10px 0;
}

.dialog-content {
  padding: 10px 10px;
  min-height: 350px;
}

.current-info {
  margin-bottom: 24px;
}

.info-row {
  display: flex;
  margin-bottom: 12px;
  font-size: 14px;
  gap: 12px;
}

.info-label {
  color: #606266;
}

.info-value {
  color: #303133;
  font-weight: 500;
}

/* 手办名称行样式 - 16px加粗 */
.figure-name-row {
  font-size: 16px;
  font-weight: 600;
}

.figure-name-row .info-label,
.figure-name-value {
  font-size: 16px;
  font-weight: 600;
}

/* 当前市值行样式 - 数值上下居中 */
.market-value-row {
  align-items: center;
}

.add-position-form {
  margin: 24px 0;
}

.form-item {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.form-label {
  font-size: 14px;
  color: #606266;
  min-width: 80px;
}

.form-input {
  width: 180px;
  margin: 0 8px;
}

.currency-select {
  width: 120px;
  margin-right: 8px;
}

.currency-select :deep(.el-input__inner) {
  text-align: center;
}

.form-unit {
  font-size: 14px;
  color: #606266;
}

.form-hint {
  font-size: 12px;
  color: #909399;
  margin-left: 80px;
  margin-top: -8px;
}

.preview-section {
  background-color: #f5f7fa;
  border-radius: 8px;
  padding: 20px;
  margin-top: 24px;
}

.preview-item {
  display: flex;
  margin-bottom: 12px;
  font-size: 14px;
  gap: 12px;
}

.preview-label {
  color: #606266;
}

.preview-value {
  color: #409eff;
  font-weight: 600;
}

.weighted-avg-note {
  font-size: 12px;
  color: #909399;
  margin-left: 4px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
