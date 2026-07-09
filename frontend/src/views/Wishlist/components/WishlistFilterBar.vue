<template>
  <div class="filter-bar">
    <span style="margin-right: 5px; font-weight: 500;">名称:</span>
    <el-input
      :model-value="filterName"
      @update:model-value="$emit('update:filterName', $event)"
      placeholder="搜索名称"
      style="width: 200px; margin-right: 10px;"
      clearable
    />
    <span style="margin-right: 5px; font-weight: 500;">状态:</span>
    <el-select
      :model-value="filterStatus"
      @update:model-value="$emit('update:filterStatus', $event)"
      placeholder="选择状态"
      style="width: 160px; margin-right: 10px;"
      clearable
    >
      <el-option value="" label="全部状态" />
      <el-option value="wish" label="愿望中" />
      <el-option value="released" label="已发售" />
      <el-option value="purchased" label="已购买" />
      <el-option value="cancelled" label="已取消" />
    </el-select>
    <span style="margin-right: 5px; font-weight: 500;">厂商:</span>
    <el-select
      :model-value="filterMaker"
      @update:model-value="$emit('update:filterMaker', $event)"
      placeholder="选择厂商"
      style="width: 180px; margin-right: 10px;"
      clearable
      filterable
    >
      <el-option value="" label="全部厂商" />
      <el-option v-for="m in manufacturers" :key="m" :value="m" :label="m" />
    </el-select>
    <span style="margin-right: 5px; font-weight: 500;">预计发售:</span>
    <el-date-picker
      :model-value="dateRange"
      @update:model-value="onDateRangeChange"
      type="daterange"
      range-separator="至"
      start-placeholder="开始日期"
      end-placeholder="结束日期"
      style="width: 380px; margin-right: 10px;"
      value-format="YYYY-MM-DD"
    />
    <el-button type="primary" @click="$emit('search')">
      <i class="ri-search-line"></i>
      <span>搜索</span>
    </el-button>
    <el-button @click="$emit('reset')">
      <i class="ri-restart-line"></i>
      <span>重置</span>
    </el-button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { wishlistApi } from '../api/wishlistApi'

const props = defineProps({
  filterName: { type: String, default: '' },
  filterStatus: { type: String, default: '' },
  filterMaker: { type: String, default: '' },
  filterStart: { type: String, default: '' },
  filterEnd: { type: String, default: '' }
})
const emit = defineEmits([
  'reset',
  'search',
  'update:filterName',
  'update:filterStatus',
  'update:filterMaker',
  'update:filterStart',
  'update:filterEnd'
])

const manufacturers = ref([])

onMounted(async () => {
  try {
    const res = await wishlistApi.manufacturers()
    manufacturers.value = res || []
  } catch {
    manufacturers.value = []
  }
})

// 将 YYYY-MM-DD 字符串数组转为 el-date-picker 需要的数组
const dateRange = computed(() => {
  if (props.filterStart && props.filterEnd) {
    return [props.filterStart, props.filterEnd]
  }
  return null
})

const onDateRangeChange = (val) => {
  if (val && val.length === 2) {
    emit('update:filterStart', val[0])
    emit('update:filterEnd', val[1])
  } else {
    emit('update:filterStart', '')
    emit('update:filterEnd', '')
  }
}
</script>

<style scoped>
.filter-bar {
  background: #fff;
  padding: 16px 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
}
</style>
