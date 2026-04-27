<!--
  AddPositionDialog.vue - 补仓弹窗组件

  功能说明：
  - 提供补仓操作的界面
  - 显示当前持仓信息和市值
  - 支持输入补仓数量和价格
  - 预览补仓后的加权平均成本和库存
  - 确认后创建已完成订单并更新资产数据

  组件依赖：
  - 使用 Element Plus 的 el-dialog、el-input-number
  - 使用 useAddPosition composable 处理业务逻辑

  维护提示：
  - 通过 openDialog 方法打开弹窗并传入手办信息
  - 补仓成功后触发 add-success 事件
  - 加权平均成本自动计算并预览
-->
<template>
  <el-dialog
    v-model="dialogVisible"
    :title="`补仓${currentFigure?.figure_name || ''}`"
    width="420px"
    :close-on-click-modal="false"
    @close="closeDialog"
  >
    <div v-loading="loading" class="add-position-dialog">
      <!-- 当前持仓信息 -->
      <div class="current-info" v-if="currentFigure">
        <div class="info-row">
          <span class="info-label">当前持仓:</span>
          <span class="info-value">{{ formatNumber(currentFigure.stock || 1) }}体 @ {{ formatMoney(currentFigure.cost_price || 0) }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">当前市值:</span>
          <span class="info-value">{{ formatMoney((currentFigure.current_price || 0) * (currentFigure.stock || 1)) }}</span>
        </div>
      </div>

      <el-divider />

      <!-- 补仓表单 -->
      <div class="add-position-form">
        <div class="form-row">
          <span class="form-label">补仓数量:</span>
          <el-input-number
            v-model="addPositionForm.quantity"
            :min="1"
            :precision="0"
            :step="1"
            controls-position="right"
            class="form-input"
          />
          <span class="form-unit">体</span>
        </div>

        <div class="form-row">
          <span class="form-label">补仓价格:</span>
          <el-input-number
            v-model="addPositionForm.price"
            :min="0"
            :precision="2"
            :step="100"
            controls-position="right"
            class="form-input"
          />
          <span class="form-unit">¥/体</span>
        </div>
        <div class="price-hint">(请输入实际入手价格)</div>
      </div>

      <el-divider />

      <!-- 补仓后预览 -->
      <div class="preview-section" v-if="positionPreview">
        <div class="preview-row">
          <span class="preview-label">补仓后成本:</span>
          <span class="preview-value">{{ formatMoney(positionPreview.newCostPrice) }}/体</span>
        </div>
        <div class="preview-hint">(加权平均)</div>
        <div class="preview-row">
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
      addPositionForm,
      positionPreview,
      openDialog,
      closeDialog,
      confirmAddPosition,
      formatMoney,
      formatNumber
    } = useAddPosition()

    // 包装确认方法，添加成功回调
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
      addPositionForm,
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

.current-info {
  margin-bottom: 16px;
}

.info-row {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.info-label {
  font-size: 14px;
  color: #606266;
  min-width: 80px;
}

.info-value {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.add-position-form {
  margin: 16px 0;
}

.form-row {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.form-label {
  font-size: 14px;
  color: #606266;
  min-width: 80px;
}

.form-input {
  width: 150px;
}

.form-unit {
  font-size: 14px;
  color: #606266;
  margin-left: 8px;
}

.price-hint {
  font-size: 12px;
  color: #909399;
  margin-left: 80px;
  margin-top: -8px;
}

.preview-section {
  background-color: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
}

.preview-row {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.preview-row:last-child {
  margin-bottom: 0;
}

.preview-label {
  font-size: 14px;
  color: #606266;
  min-width: 80px;
}

.preview-value {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.preview-hint {
  font-size: 12px;
  color: #909399;
  margin-left: 80px;
  margin-top: -4px;
  margin-bottom: 12px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
