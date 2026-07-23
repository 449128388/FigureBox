<template>
  <div class="tab-content">
    <div class="form-grid">
      <div class="form-group">
        <label>选择手办 <span class="required">*</span></label>
        <el-select
          v-model="order.figure_id"
          placeholder="🔍 搜索手办"
          filterable
          style="width: 100%;"
          :disabled="isEditing"
          :loading="loadingCostPrice"
          @change="handleFigureChange"
        >
          <el-option
            v-for="figure in availableFigures"
            :key="figure.id"
            :label="figure.name + '/' + (figure.quantity || 1) + '体'"
            :value="figure.id"
          />
        </el-select>
      </div>
      <div class="form-group">
        <label>卖出平台 <span class="required">*</span></label>
        <el-select v-model="order.sell_platform" placeholder="请选择平台" style="width: 100%;">
          <el-option label="闲鱼（个人卖家）" value="闲鱼（个人卖家）" />
          <el-option label="闲鱼（鱼小铺）" value="闲鱼（鱼小铺）" />
          <el-option label="淘宝" value="淘宝" />
          <el-option label="转转" value="转转" />
          <el-option label="微信群" value="微信群" />
          <el-option label="QQ群" value="QQ群" />
          <el-option label="快速卖出" value="快速卖出" />
          <el-option label="其他" value="其他" />
        </el-select>
      </div>
      <div class="form-group">
        <label>订单编号</label>
        <el-input v-model="order.order_number" placeholder="请输入订单号" />
      </div>
      <div class="form-group">
        <label>卖出数量 <span class="required">*</span></label>
        <el-input-number
          v-model="order.quantity"
          :min="1"
          :step="1"
          controls-position="right"
          style="width: 100%;"
          placeholder="请输入卖出数量"
        />
      </div>
      <div class="form-group">
        <label>支付方式 <span class="required">*</span></label>
        <el-select v-model="order.payment_method" placeholder="请选择支付方式" style="width: 100%;">
          <el-option label="支付宝" value="支付宝" />
          <el-option label="微信" value="微信" />
          <el-option label="银行卡" value="银行卡" />
        </el-select>
      </div>
      <div class="form-group">
        <label>卖出时间 <span class="required">*</span></label>
        <el-date-picker
          v-model="order.sell_date"
          type="datetime"
          placeholder="选择卖出时间"
          style="width: 100%;"
          format="YYYY-MM-DD HH:mm:ss"
          value-format="YYYY-MM-DD HH:mm:ss"
        />
      </div>
      <div class="form-group">
        <label>卖出状态 <span class="required">*</span></label>
        <el-select v-model="order.status" placeholder="请选择状态" style="width: 100%;">
          <el-option label="待发货" value="待发货" />
          <el-option label="已发货" value="已发货" />
          <el-option label="已完成" value="已完成" />
          <el-option label="退款/纠纷" value="退款/纠纷" />
        </el-select>
      </div>
      <div class="form-group">
        <label>买家手机号 <span class="required">*</span></label>
        <el-input v-model="order.buyer_phone" placeholder="请输入买家手机号" />
      </div>
      <div class="form-group full-width">
        <label>买家地址</label>
        <el-input v-model="order.buyer_address" placeholder="请输入买家地址" />
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useSoldOrderStore } from '../../../../store'

export default {
  name: 'BasicInfoTab',
  props: {
    order: Object,
    availableFigures: Array,
    isEditing: Boolean
  },
  emits: ['figureChange'],
  setup(props, context) {
    const soldOrderStore = useSoldOrderStore()
    const loadingCostPrice = ref(false)

    const handleFigureChange = async (figureId) => {
      // 触发事件通知父组件
      context.emit('figureChange', figureId)

      // 如果不是编辑模式，调用API获取实际成本价
      if (!props.isEditing && figureId) {
        loadingCostPrice.value = true
        try {
          const response = await soldOrderStore.fetchFigureCostPrice(figureId)
          if (response && response.cost_price !== undefined) {
            props.order.cost_price = response.cost_price
          }
        } catch (error) {
          console.error('获取成本价失败:', error)
          // 如果API调用失败，使用手办的average_purchase_price作为备选
          const figure = props.availableFigures.find(f => f.id === figureId)
          if (figure) {
            props.order.cost_price = figure.average_purchase_price || 0
          }
        } finally {
          loadingCostPrice.value = false
        }
      }
    }

    return {
      handleFigureChange,
      loadingCostPrice
    }
  }
}
</script>

<style scoped>
/* 标签内容区域 */
.tab-content {
  padding: 20px;
}

/* 表单网格 */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-group {
  margin-bottom: 0;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #333;
  font-weight: 500;
  font-size: 16px;
}

.form-group label .required {
  color: #f56c6c;
  margin-left: 4px;
}
</style>