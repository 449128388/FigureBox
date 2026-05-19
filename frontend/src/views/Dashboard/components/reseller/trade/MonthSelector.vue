<!--
  MonthSelector.vue - 月份切换器组件

  功能说明：
  - 提供月份切换功能，支持查看历史月份数据
  - 显示当前选中年月（如 < 2026年5月 >）
  - 支持左右箭头切换上一个月/下一个月

  组件依赖：
  - 接收 modelValue 作为当前选中的年月
  - 触发 update:modelValue 事件更新父组件数据

  维护提示：
  - 月份范围限制在合理范围内（如2020年至今）
  - 切换时触发事件通知父组件重新加载数据
-->
<template>
  <div class="month-selector">
    <button class="month-btn" @click="prevMonth" :disabled="!canGoPrev">
      <i class="arrow left"></i>
    </button>
    <span class="month-display">{{ formattedMonth }}</span>
    <button class="month-btn" @click="nextMonth" :disabled="!canGoNext">
      <i class="arrow right"></i>
    </button>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'MonthSelector',
  props: {
    modelValue: {
      type: Object,
      default: () => ({
        year: new Date().getFullYear(),
        month: new Date().getMonth() + 1
      })
    }
  },
  emits: ['update:modelValue', 'change'],
  setup(props, { emit }) {
    // 格式化显示年月
    const formattedMonth = computed(() => {
      const { year, month } = props.modelValue
      return `${year}年${month}月`
    })

    // 是否可以切换到上个月（限制到2020年1月）
    const canGoPrev = computed(() => {
      const { year, month } = props.modelValue
      return year > 2020 || (year === 2020 && month > 1)
    })

    // 是否可以切换到下个月（限制到当前月份）
    const canGoNext = computed(() => {
      const { year, month } = props.modelValue
      const now = new Date()
      const currentYear = now.getFullYear()
      const currentMonth = now.getMonth() + 1
      return year < currentYear || (year === currentYear && month < currentMonth)
    })

    // 切换到上个月
    const prevMonth = () => {
      if (!canGoPrev.value) return
      let { year, month } = props.modelValue
      month--
      if (month < 1) {
        month = 12
        year--
      }
      const newValue = { year, month }
      emit('update:modelValue', newValue)
      emit('change', newValue)
    }

    // 切换到下个月
    const nextMonth = () => {
      if (!canGoNext.value) return
      let { year, month } = props.modelValue
      month++
      if (month > 12) {
        month = 1
        year++
      }
      const newValue = { year, month }
      emit('update:modelValue', newValue)
      emit('change', newValue)
    }

    return {
      formattedMonth,
      canGoPrev,
      canGoNext,
      prevMonth,
      nextMonth
    }
  }
}
</script>

<style scoped>
.month-selector {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  padding: 10px 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 20px;
}

.month-btn {
  width: 32px;
  height: 32px;
  border: none;
  background-color: white;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.month-btn:hover:not(:disabled) {
  background-color: #409eff;
  color: white;
  transform: scale(1.1);
}

.month-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.month-display {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  min-width: 100px;
  text-align: center;
}

/* 箭头样式 */
.arrow {
  border: solid #606266;
  border-width: 0 2px 2px 0;
  display: inline-block;
  padding: 4px;
}

.arrow.left {
  transform: rotate(135deg);
  margin-left: 2px;
}

.arrow.right {
  transform: rotate(-45deg);
  margin-right: 2px;
}

.month-btn:hover:not(:disabled) .arrow {
  border-color: white;
}
</style>
