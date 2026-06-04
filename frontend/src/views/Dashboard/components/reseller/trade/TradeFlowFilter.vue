<!--
  TradeFlowFilter.vue - 交易流水高级筛选组件

  功能说明：
  - 支持时间范围筛选（快捷选项/自定义日期）
  - 支持手办名称多选筛选
  - 支持平台多选筛选
  - 支持订单状态多选筛选
  - 支持金额范围筛选
  - 支持关键词搜索

  组件依赖：
  - 需要父组件传入筛选参数
  - 通过事件通知父组件筛选条件变更

  维护提示：
  - 筛选条件变更时触发 filter-change 事件
  - 点击确定时触发 confirm 事件
  - 点击重置时触发 reset 事件
-->
<template>
  <div class="trade-flow-filter">
    <!-- 快捷筛选类型 -->
    <div class="filter-row type-row">
      <el-button
        v-for="type in filterTypes"
        :key="type.value"
        :class="{ active: localFilter.filterType === type.value }"
        size="small"
        @click="handleTypeChange(type.value)"
      >
        {{ type.label }}
      </el-button>
    </div>

    <!-- 时间筛选 -->
    <div class="filter-section">
      <div class="filter-label">📅 时间</div>
      <div class="filter-content">
        <el-select
          v-model="localFilter.timeType"
          placeholder="选择时间范围"
          size="small"
          style="width: 120px"
          @change="handleTimeTypeChange"
        >
          <el-option
            v-for="option in timeOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
        <template v-if="localFilter.timeType === 'custom'">
          <span class="separator">或</span>
          <el-date-picker
            v-model="localFilter.dateRange"
            type="daterange"
            range-separator="~"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            size="small"
            style="width: 240px"
            value-format="YYYY-MM-DD"
          />
        </template>
      </div>
    </div>

    <!-- 手办筛选 -->
    <div class="filter-section">
      <div class="filter-label">🧸 手办</div>
      <div class="filter-content">
        <el-select
          v-model="localFilter.figureIds"
          multiple
          collapse-tags
          collapse-tags-tooltip
          placeholder="全部"
          size="small"
          style="width: 200px"
          filterable
          remote
          :remote-method="searchFigures"
          :loading="figureLoading"
        >
          <el-option
            v-for="figure in figureOptions"
            :key="figure.id"
            :label="figure.name"
            :value="figure.id"
          />
        </el-select>
      </div>
    </div>

    <!-- 平台筛选 -->
    <div class="filter-section">
      <div class="filter-label">🏪 平台</div>
      <div class="filter-content">
        <el-checkbox-group v-model="localFilter.platforms" size="small">
          <el-checkbox-button
            v-for="platform in platformOptions"
            :key="platform.value"
            :label="platform.value"
          >
            {{ platform.label }}
          </el-checkbox-button>
        </el-checkbox-group>
      </div>
    </div>

    <!-- 状态筛选 -->
    <div class="filter-section">
      <div class="filter-label">📋 状态</div>
      <div class="filter-content">
        <el-checkbox-group v-model="localFilter.statusList" size="small">
          <el-checkbox-button
            v-for="status in statusOptions"
            :key="status.value"
            :label="status.value"
          >
            {{ status.label }}
          </el-checkbox-button>
        </el-checkbox-group>
      </div>
    </div>

    <!-- 金额范围 -->
    <div class="filter-section">
      <div class="filter-label">💰 金额</div>
      <div class="filter-content">
        <el-input-number
          v-model="localFilter.minAmount"
          :min="0"
          :precision="2"
          placeholder="最小金额"
          size="small"
          style="width: 120px"
          controls-position="right"
        />
        <span class="separator">~</span>
        <el-input-number
          v-model="localFilter.maxAmount"
          :min="0"
          :precision="2"
          placeholder="最大金额"
          size="small"
          style="width: 120px"
          controls-position="right"
        />
        <span class="unit">元</span>
      </div>
    </div>

    <!-- 关键词搜索 -->
    <div class="filter-section">
      <div class="filter-label">🔍 关键词</div>
      <div class="filter-content">
        <el-input
          v-model="localFilter.keyword"
          placeholder="搜索订单号、手办名、备注..."
          size="small"
          style="width: 300px"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="filter-actions">
      <el-button size="small" @click="handleReset">重置</el-button>
      <el-button type="primary" size="small" @click="handleConfirm">确定筛选</el-button>
    </div>
  </div>
</template>

<script>
import { ref, reactive, watch } from 'vue'
import { Search } from '@element-plus/icons-vue'
import axios from '../../../../../axios'

export default {
  name: 'TradeFlowFilter',
  components: {
    Search
  },
  props: {
    modelValue: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['update:modelValue', 'change', 'confirm', 'reset'],
  setup(props, { emit }) {
    // 筛选类型
    const filterTypes = [
      { label: '全部', value: 'all' },
      { label: '收入', value: 'income' },
      { label: '支出', value: 'expense' }
    ]

    // 时间选项
    const timeOptions = [
      { label: '近7天', value: 'last7days' },
      { label: '近30天', value: 'last30days' },
      { label: '本月', value: 'thisMonth' },
      { label: '上月', value: 'lastMonth' },
      { label: '本年', value: 'thisYear' },
      { label: '自定义', value: 'custom' }
    ]

    // 平台选项
    const platformOptions = [
      { label: '闲鱼（个人卖家）', value: '闲鱼（个人卖家）' },
      { label: '闲鱼（鱼小铺）', value: '闲鱼（鱼小铺）' },
      { label: '淘宝', value: '淘宝' },
      { label: '转转', value: '转转' },
      { label: '微信群', value: '微信群' },
      { label: 'QQ群', value: 'QQ群' },
      { label: '快速卖出', value: '快速卖出' },
      { label: '其他', value: '其他' }
    ]

    // 状态选项
    const statusOptions = [
      { label: '✅ 已完成', value: '已完成' },
      { label: '⏳ 待发货', value: '待发货' },
      { label: '⏳ 已支付定金', value: '已支付' },
      { label: '⏳ 未支付定金', value: '未支付' },
      { label: '❌ 已取消', value: '已取消' },
      { label: '↩️ 已退款', value: '已退款' }
    ]

    // 手办选项
    const figureOptions = ref([])
    const figureLoading = ref(false)

    // 本地筛选状态
    const localFilter = reactive({
      filterType: 'all',
      timeType: 'last30days',
      dateRange: [],
      figureIds: [],
      platforms: [],
      statusList: [],
      minAmount: null,
      maxAmount: null,
      keyword: ''
    })

    // 同步外部数据
    watch(() => props.modelValue, (newVal) => {
      if (newVal) {
        Object.assign(localFilter, newVal)
      }
    }, { immediate: true, deep: true })

    // 处理类型变更
    const handleTypeChange = (type) => {
      localFilter.filterType = type
      emit('update:modelValue', { ...localFilter })
      emit('change', { ...localFilter })
    }

    // 处理时间类型变更
    const handleTimeTypeChange = (type) => {
      if (type !== 'custom') {
        localFilter.dateRange = []
      }
      emit('update:modelValue', { ...localFilter })
      emit('change', { ...localFilter })
    }

    // 搜索手办
    const searchFigures = async (query) => {
      if (query.length < 1) return
      figureLoading.value = true
      try {
        const response = await axios.get('/figures/search', {
          params: { keyword: query }
        })
        figureOptions.value = response || []
      } catch (error) {
        console.error('搜索手办失败:', error)
      } finally {
        figureLoading.value = false
      }
    }

    // 重置筛选
    const handleReset = () => {
      localFilter.filterType = 'all'
      localFilter.timeType = 'last30days'
      localFilter.dateRange = []
      localFilter.figureIds = []
      localFilter.platforms = []
      localFilter.statusList = []
      localFilter.minAmount = null
      localFilter.maxAmount = null
      localFilter.keyword = ''
      emit('update:modelValue', { ...localFilter })
      emit('reset')
    }

    // 确认筛选
    const handleConfirm = () => {
      emit('update:modelValue', { ...localFilter })
      emit('confirm', { ...localFilter })
    }

    return {
      filterTypes,
      timeOptions,
      platformOptions,
      statusOptions,
      figureOptions,
      figureLoading,
      localFilter,
      handleTypeChange,
      handleTimeTypeChange,
      searchFigures,
      handleReset,
      handleConfirm
    }
  }
}
</script>

<style scoped>
.trade-flow-filter {
  padding: 15px;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.filter-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 15px;
}

.filter-row .el-button {
  border-radius: 4px;
}

.filter-row .el-button.active {
  background-color: #409EFF;
  color: white;
}

.filter-section {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 10px;
}

.filter-label {
  min-width: 70px;
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.filter-content {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.separator {
  color: #999;
  font-size: 13px;
}

.unit {
  font-size: 13px;
  color: #666;
}

.filter-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #e0e0e0;
}
</style>
