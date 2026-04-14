<!--
  PriceUpdateDialog.vue - 修改市场价弹窗组件

  功能说明：
  - 提供修改手办市场价的界面
  - 显示手办当前价格和上次更新时间
  - 支持价格输入和确认修改
  - 显示加载状态和操作结果

  组件依赖：
  - 无外部组件依赖
  - 使用 Element Plus 的 el-dialog 和 el-input-number

  维护提示：
  - 通过 openDialog 方法打开弹窗并传入价格信息
  - 价格更新成功后触发 update-success 事件
  - 价格格式通过 formatMoney 方法处理
-->
<template>
  <el-dialog
    v-model="dialogVisible"
    title="修改市场价"
    width="500px"
    :close-on-click-modal="false"
    @close="closeDialog"
  >
    <div v-loading="loading" class="price-update-dialog">
      <!-- 手办信息 -->
      <div class="figure-info" v-if="priceInfo">
        <h4 class="figure-name">{{ priceInfo.figure_name }} 当前系统估价</h4>
        <div class="last-updated">
          上次更新: {{ priceInfo.last_updated ? new Date(priceInfo.last_updated).toLocaleDateString('zh-CN') : '未知' }} ({{ lastUpdatedText }})
        </div>
        <div class="current-price">
          当前市场价: <span class="price-value">{{ formatMoney(priceInfo.current_price) }}</span>
        </div>
      </div>

      <!-- 新价格输入 -->
      <div class="new-price-section">
        <div class="price-input-row">
          <span class="input-label">新价格:</span>
          <el-input-number
            v-model="newPrice"
            :min="0"
            :precision="2"
            :step="100"
            controls-position="right"
            class="price-input"
          />
          <span class="currency">¥</span>
        </div>
        <div class="quick-actions">
          <el-button type="info" size="small" @click="useXianyuPrice">
            查看闲鱼参考
          </el-button>
          <el-button type="info" size="small" @click="useAveragePrice">
            使用均价
          </el-button>
        </div>
      </div>

      <!-- 影响预览 -->
      <div class="impact-preview" v-if="impactPreview">
        <div class="impact-title">💡 修改后影响:</div>
        <ul class="impact-list">
          <li>
            总资产将从 {{ formatMoney(impactPreview.oldTotalAssets) }} → {{ formatMoney(impactPreview.newTotalAssets) }}
          </li>
          <li>
            盈亏比例将变为 {{ formatPercentage(impactPreview.newProfitPercentage) }}
          </li>
          <li>塑料指数将重新计算</li>
        </ul>
      </div>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="closeDialog">取消</el-button>
        <el-button type="primary" @click="handleConfirmClick" :loading="loading">
          确认修改
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script>
import { usePriceUpdate } from '../../../composables/usePriceUpdate'

export default {
  name: 'PriceUpdateDialog',
  emits: ['update-success'],
  setup(props, { emit }) {
    const {
      dialogVisible,
      loading,
      currentFigure,
      priceInfo,
      newPrice,
      impactPreview,
      lastUpdatedText,
      openDialog,
      closeDialog,
      useXianyuPrice,
      useAveragePrice,
      confirmUpdate,
      formatMoney,
      formatPercentage
    } = usePriceUpdate()

    // 包装确认修改方法，添加成功回调
    const handleConfirm = async () => {
      const result = await confirmUpdate()
      if (result) {
        emit('update-success', result)
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
      priceInfo,
      newPrice,
      impactPreview,
      lastUpdatedText,
      openDialog: exposedOpenDialog,
      closeDialog,
      useXianyuPrice,
      useAveragePrice,
      confirmUpdate: handleConfirm,
      handleConfirmClick,
      formatMoney,
      formatPercentage
    }
  }
}
</script>

<style scoped>
.price-update-dialog {
  padding: 10px 0;
}

.figure-info {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.figure-name {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.last-updated {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.current-price {
  font-size: 14px;
  color: #606266;
}

.price-value {
  font-size: 20px;
  font-weight: 600;
  color: #409eff;
}

.new-price-section {
  margin-bottom: 24px;
}

.price-input-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.input-label {
  font-size: 14px;
  color: #606266;
  min-width: 60px;
}

.price-input {
  width: 200px;
}

.currency {
  font-size: 14px;
  color: #606266;
}

.quick-actions {
  display: flex;
  gap: 8px;
  margin-left: 68px;
}

.impact-preview {
  background-color: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
}

.impact-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.impact-list {
  margin: 0;
  padding-left: 20px;
  color: #606266;
  font-size: 13px;
  line-height: 1.8;
}

.impact-list li {
  margin-bottom: 4px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>