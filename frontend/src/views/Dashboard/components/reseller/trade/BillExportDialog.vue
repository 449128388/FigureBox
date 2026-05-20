<!--
  BillExportDialog.vue - 账单导出弹窗组件

  功能说明：
  - 提供账单导出范围选择（当前月份或全部历史）
  - 支持导出格式选择（Excel/CSV）
  - 触发后端导出API并下载文件

  组件依赖：
  - 接收 modelValue 控制弹窗显示
  - 接收 currentMonth 显示当前月份
  - 触发 export 事件执行导出

  维护提示：
  - 导出范围与当前筛选月份同步
  - 文件格式默认为 Excel
-->
<template>
  <el-dialog
    v-model="dialogVisible"
    title="选择导出范围"
    width="400px"
    :close-on-click-modal="false"
  >
    <div class="export-options">
      <el-radio-group v-model="exportRange" class="range-group">
        <el-radio label="current">
          仅导出当前月份 ({{ formattedMonth }})
        </el-radio>
        <el-radio label="all">
          导出全部历史账单
        </el-radio>
      </el-radio-group>

      <div class="format-section">
        <span class="format-label">文件格式：</span>
        <el-radio-group v-model="exportFormat" size="small">
          <el-radio-button label="xlsx">Excel (.xlsx)</el-radio-button>
          <el-radio-button label="csv">CSV</el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleExport" :loading="loading">
          确认导出
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script>
import { ref, computed, watch } from 'vue'

export default {
  name: 'BillExportDialog',
  props: {
    modelValue: {
      type: Boolean,
      default: false
    },
    currentMonth: {
      type: Object,
      default: () => ({
        year: new Date().getFullYear(),
        month: new Date().getMonth() + 1
      })
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue', 'export'],
  setup(props, { emit }) {
    const exportRange = ref('current')
    const exportFormat = ref('xlsx')

    const dialogVisible = computed({
      get: () => props.modelValue,
      set: (val) => emit('update:modelValue', val)
    })

    const formattedMonth = computed(() => {
      const { year, month } = props.currentMonth
      return `${year}年${month}月`
    })

    const handleExport = () => {
      emit('export', {
        range: exportRange.value,
        format: exportFormat.value,
        year: props.currentMonth.year,
        month: props.currentMonth.month
      })
    }

    watch(() => props.modelValue, (val) => {
      if (val) {
        exportRange.value = 'current'
        exportFormat.value = 'xlsx'
      }
    })

    return {
      dialogVisible,
      exportRange,
      exportFormat,
      formattedMonth,
      handleExport
    }
  }
}
</script>

<style scoped>
.export-options {
  padding: 20px 0;
}

.range-group {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.range-group :deep(.el-radio) {
  margin-right: 0;
  height: auto;
  line-height: 1.5;
}

.format-section {
  margin-top: 25px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}

.format-label {
  display: block;
  margin-bottom: 10px;
  color: #606266;
  font-size: 14px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
