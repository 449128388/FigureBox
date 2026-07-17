<!--
  OrderForm.vue - 订单表单弹窗（三步向导外壳）

  职责：
  - 弹窗蒙层 / 卡片容器
  - 头部标题 + 关闭按钮
  - 步骤进度条
  - 左侧步骤导航栏
  - 右侧渲染当前步骤子组件
  - 底部操作栏（取消 / 上一步 / 下一步 / 保存）
  - 全局表单数据源管理（newOrder）
  - 步骤切换校验入口

  数据流：
  - 父组件通过 props 传入 visible / newOrder / availableFigures 等
  - 子步骤组件通过 props 接收字段值，通过 emit 通知父组件更新
  - 本组件在 template 中使用 v-model / @update 模式完成双向绑定
-->
<template>
  <div class="modal-overlay" v-if="visible">
    <div class="modal-card">
      <!-- 头部 -->
      <div class="modal-header">
        <div class="modal-title">{{ isEditing ? '编辑订单' : '添加订单' }}</div>
        <button class="close-btn" @click="$emit('cancel')" type="button">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <!-- 进度条 -->
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
      </div>

      <!-- 主体 -->
      <div class="modal-body">
        <!-- 左侧步骤导航 -->
        <div class="step-sidebar">
          <div
            v-for="step in steps"
            :key="step.index"
            class="step-item"
            :class="{
              active: currentStep === step.index,
              completed: currentStep > step.index,
              disabled: !isStepReachable(step.index)
            }"
            @click="onStepClick(step.index)"
          >
            <div class="step-num">{{ step.index }}</div>
            <div>
              <div class="step-text">{{ step.title }}</div>
              <div class="step-desc">{{ step.desc }}</div>
            </div>
          </div>
        </div>

        <!-- 右侧表单区域 -->
        <div class="form-area">
          <!-- 步骤 1：核心信息 -->
          <Step1CoreInfo
            v-show="currentStep === 1"
            :figure-id="newOrder.figure_id"
            :deposit="newOrder.deposit"
            :deposit-currency="newOrder.deposit_currency"
            :balance="newOrder.balance"
            :balance-currency="newOrder.balance_currency"
            :due-date="newOrder.due_date"
            :order-type="newOrder.order_type"
            :status="newOrder.status"
            :is-editing="isEditing"
            :available-figures="availableFigures"
            :figure-error="figureError"
            :due-date-error="dueDateError"
            @update:figure-id="newOrder.figure_id = $event"
            @update:deposit="newOrder.deposit = $event"
            @update:deposit-currency="newOrder.deposit_currency = $event"
            @update:balance="newOrder.balance = $event"
            @update:balance-currency="newOrder.balance_currency = $event"
            @update:due-date="newOrder.due_date = $event"
            @update:order-type="newOrder.order_type = $event"
            @update:status="newOrder.status = $event"
          />

          <!-- 步骤 2：店铺与支付 -->
          <Step2ShopPayment
            v-show="currentStep === 2"
            :shop-name="newOrder.shop_name"
            :shop-contact="newOrder.shop_contact"
            :payment-method="newOrder.payment_method"
            :payment-time="newOrder.payment_time"
            @update:shop-name="newOrder.shop_name = $event"
            @update:shop-contact="newOrder.shop_contact = $event"
            @update:payment-method="newOrder.payment_method = $event"
            @update:payment-time="newOrder.payment_time = $event"
          />

          <!-- 步骤 3：物流与备注 -->
          <Step3LogisticsNotes
            v-show="currentStep === 3"
            :status="newOrder.status"
            :tracking-number="newOrder.tracking_number"
            :logistics-company="newOrder.logistics_company"
            :balance-payment-method="newOrder.balance_payment_method"
            :balance-payment-time="newOrder.balance_payment_time"
            :order-number="newOrder.order_number"
            :remarks="newOrder.remarks"
            @update:status="newOrder.status = $event"
            @update:tracking-number="newOrder.tracking_number = $event"
            @update:logistics-company="newOrder.logistics_company = $event"
            @update:balance-payment-method="newOrder.balance_payment_method = $event"
            @update:balance-payment-time="newOrder.balance_payment_time = $event"
            @update:order-number="newOrder.order_number = $event"
            @update:remarks="newOrder.remarks = $event"
          />
        </div>
      </div>

      <!-- 底部操作栏 -->
      <div class="modal-footer">
        <div class="footer-left">
          <button class="btn btn-ghost" @click="$emit('cancel')" type="button">取消</button>
        </div>
        <div class="footer-right">
          <button
            class="btn btn-default"
            v-show="!isFirstStep"
            @click="prevStep"
            type="button"
          >上一步</button>
          <button
            class="btn btn-primary"
            v-show="!isLastStep"
            @click="handleNext"
            type="button"
          >下一步</button>
          <button
            class="btn btn-primary"
            v-show="isLastStep"
            @click="handleSave"
            type="button"
          >保存订单</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { watch } from 'vue'
import { useStepForm } from '../composables/useStepForm'
import Step1CoreInfo from './OrderFormSteps/Step1CoreInfo.vue'
import Step2ShopPayment from './OrderFormSteps/Step2ShopPayment.vue'
import Step3LogisticsNotes from './OrderFormSteps/Step3LogisticsNotes.vue'

export default {
  name: 'OrderForm',
  components: {
    Step1CoreInfo,
    Step2ShopPayment,
    Step3LogisticsNotes
  },
  props: {
    visible: { type: Boolean, default: false },
    isEditing: { type: Boolean, default: false },
    newOrder: { type: Object, required: true },
    availableFigures: { type: Array, default: () => [] },
    figureError: { type: String, default: '' },
    dueDateError: { type: String, default: '' }
  },
  emits: ['saveOrder', 'cancel', 'validateStep'],
  setup() {
    const {
      currentStep,
      totalSteps,
      steps,
      isFirstStep,
      isLastStep,
      progressPercent,
      canJumpTo,
      goToStep,
      nextStep,
      prevStep,
      resetStep
    } = useStepForm(3)

    return {
      currentStep,
      totalSteps,
      steps,
      isFirstStep,
      isLastStep,
      progressPercent,
      canJumpTo,
      goToStep,
      nextStep,
      prevStep,
      resetStep
    }
  },
  computed: {
    /**
     * 步骤 1 必填字段是否都已填写
     * - 手办必填
     * - 尾款状态为"已取消"时,出荷日期可为空;其他状态必填
     */
    isStep1Valid() {
      const o = this.newOrder || {}
      if (!o.figure_id) return false
      const isCancelled = o.status === '已取消'
      if (!isCancelled && !o.due_date) return false
      return true
    },
    /**
     * 当前可自由切换的步骤集合
     * - 当步骤 1 必填字段已填写,所有步骤都可达
     * - 否则只允许步骤 1 与 2
     */
    reachableSteps() {
      return this.isStep1Valid ? new Set([1, 2, 3]) : new Set([1, 2])
    }
  },
  watch: {
    /**
     * 弹窗打开时,重置到步骤 1,确保每次进入都是干净的初始状态
     */
    visible: {
      immediate: false,
      handler(val) {
        if (val) {
          this.resetStep()
        }
      }
    }
  },
  methods: {
    /**
     * 判断目标步骤是否当前可点击
     */
    isStepReachable(target) {
      return this.canJumpTo(target, this.reachableSteps)
    },
    /**
     * 点击步骤导航
     */
    onStepClick(target) {
      if (!this.isStepReachable(target)) {
        // 目标不可达 → 提示用户先完成步骤 1
        if (target > this.currentStep) {
          this.$emit('validateStep', 1)
        }
        return
      }
      this.goToStep(target, this.reachableSteps)
    },
    /**
     * 校验指定步骤
     * @param {number} step
     * @returns {boolean}
     */
    validateStep(step) {
      if (step === 1) {
        // 委托给父组件校验（与原逻辑保持一致）
        this.$emit('validateStep', 1)
        return this.isStep1Valid
      }
      return true
    },
    /**
     * 下一步
     */
    handleNext() {
      if (this.currentStep === 1) {
        // 触发父组件校验,父组件会更新 figureError / dueDateError
        this.$emit('validateStep', 1)
        if (!this.isStep1Valid) {
          return
        }
      }
      this.nextStep()
    },
    /**
     * 保存
     */
    handleSave() {
      // 最后一步保存前,再次校验步骤 1
      this.$emit('validateStep', 1)
      if (!this.isStep1Valid) {
        // 跳回步骤 1 让用户修正
        this.goToStep(1, this.reachableSteps)
        return
      }
      this.$emit('saveOrder', this.newOrder)
      this.resetStep()
    }
  }
}
</script>

<style scoped>
/* ===== 弹窗容器 ===== */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 24px;
}

.modal-card {
  background: #fff;
  border-radius: 12px;
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  overflow: hidden;
}

/* ===== 头部 ===== */
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 28px;
  border-bottom: 1px solid #f0f0f0;
  flex-shrink: 0;
}
.modal-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f1f1f;
}
.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  border-radius: 6px;
  transition: all 0.2s;
}
.close-btn:hover {
  background: #f5f5f5;
  color: #666;
}

/* ===== 进度条 ===== */
.progress-bar {
  height: 3px;
  background: #f0f0f0;
  position: relative;
  overflow: hidden;
  flex-shrink: 0;
}
.progress-fill {
  height: 100%;
  background: #52c41a;
  transition: width 0.4s ease;
  border-radius: 0 2px 2px 0;
}

/* ===== 主体 ===== */
.modal-body {
  display: flex;
  flex: 1;
  overflow: hidden;
  min-height: 0;
}

/* --- 左侧步骤导航 --- */
.step-sidebar {
  width: 200px;
  background: #fafafa;
  border-right: 1px solid #f0f0f0;
  padding: 24px 0;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
}
.step-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  border-left: 3px solid transparent;
}
.step-item:hover {
  background: #f0f0f0;
}
.step-item.active {
  background: #fff;
  border-left-color: #52c41a;
}
.step-item.completed {
  cursor: pointer;
}
.step-item.disabled {
  cursor: not-allowed;
  opacity: 0.55;
}
.step-item.disabled:hover {
  background: transparent;
}
.step-num {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 2px solid #d9d9d9;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  color: #999;
  flex-shrink: 0;
  transition: all 0.2s;
}
.step-item.active .step-num {
  border-color: #52c41a;
  color: #52c41a;
}
.step-item.completed .step-num {
  background: #52c41a;
  color: #fff;
  border-color: #52c41a;
}
.step-text {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}
.step-item.active .step-text {
  color: #1f1f1f;
  font-weight: 600;
}
.step-item.completed .step-text {
  color: #52c41a;
}
.step-desc {
  font-size: 12px;
  color: #bfbfbf;
  margin-top: 2px;
}

/* --- 右侧表单区域 --- */
.form-area {
  flex: 1;
  padding: 28px 32px;
  overflow-y: auto;
  position: relative;
}

/* ===== 底部操作栏 ===== */
.modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 28px;
  border-top: 1px solid #f0f0f0;
  background: #fafafa;
  flex-shrink: 0;
}
.footer-left {
  display: flex;
  gap: 10px;
}
.footer-right {
  display: flex;
  gap: 10px;
}
.btn {
  height: 36px;
  padding: 0 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  outline: none;
}
.btn-default {
  background: #fff;
  border-color: #d9d9d9;
  color: #666;
}
.btn-default:hover {
  border-color: #40a9ff;
  color: #40a9ff;
}
.btn-primary {
  background: #52c41a;
  border-color: #52c41a;
  color: #fff;
}
.btn-primary:hover {
  background: #389e0d;
  border-color: #389e0d;
}
.btn-ghost {
  background: transparent;
  border-color: transparent;
  color: #999;
}
.btn-ghost:hover {
  color: #666;
}

/* 响应式 */
@media (max-width: 700px) {
  .modal-card {
    max-height: 95vh;
  }
  .modal-body {
    flex-direction: column;
  }
  .step-sidebar {
    width: 100%;
    flex-direction: row;
    padding: 12px 16px;
    border-right: none;
    border-bottom: 1px solid #f0f0f0;
    overflow-x: auto;
  }
  .step-item {
    border-left: none;
    border-bottom: 3px solid transparent;
    white-space: nowrap;
    padding: 8px 12px;
  }
  .step-item.active {
    border-bottom-color: #52c41a;
    border-left-color: transparent;
  }
  .form-area {
    padding: 20px;
  }
  .modal-header,
  .modal-footer {
    padding: 16px 20px;
  }
}
</style>
