<template>
  <div class="filter-bar">
    <div class="filter-item">
      <span class="filter-label">名称:</span>
      <input
        :value="filterName"
        @input="$emit('update:filterName', $event.target.value)"
        class="filter-input"
        placeholder="搜索名称"
      />
    </div>
    <div class="filter-item">
      <span class="filter-label">状态:</span>
      <select
        :value="filterStatus"
        @change="$emit('update:filterStatus', $event.target.value)"
        class="filter-select"
      >
        <option value="">全部状态</option>
        <option value="wish">愿望中</option>
        <option value="released">已发售</option>
        <option value="purchased">已购买</option>
        <option value="cancelled">已取消</option>
      </select>
    </div>
    <div class="filter-item">
      <span class="filter-label">预计发售:</span>
      <div class="date-range">
        <input
          :value="filterStart"
          @input="$emit('update:filterStart', $event.target.value)"
          type="month"
          class="date-input"
        />
        <span>至</span>
        <input
          :value="filterEnd"
          @input="$emit('update:filterEnd', $event.target.value)"
          type="month"
          class="date-input"
        />
      </div>
    </div>
    <div class="filter-item">
      <span class="filter-label">厂商:</span>
      <select
        :value="filterMaker"
        @change="$emit('update:filterMaker', $event.target.value)"
        class="filter-select"
      >
        <option value="">全部厂商</option>
        <option value="Alter">Alter</option>
        <option value="GSC">GSC</option>
        <option value="Max Factory">Max Factory</option>
        <option value="Native">Native</option>
        <option value="BINDing">BINDing</option>
      </select>
    </div>
    <div class="filter-item" style="margin-left:auto;">
      <button class="btn btn-info" @click="$emit('search')">
        <i class="ri-search-line"></i>
        <span>搜索</span>
      </button>
      <button class="btn btn-default" @click="$emit('reset')">
        <i class="ri-restart-line"></i>
        <span>重置</span>
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  filterName: { type: String, default: '' },
  filterStatus: { type: String, default: '' },
  filterMaker: { type: String, default: '' },
  filterStart: { type: String, default: '' },
  filterEnd: { type: String, default: '' }
})
defineEmits([
  'reset',
  'search',
  'update:filterName',
  'update:filterStatus',
  'update:filterMaker',
  'update:filterStart',
  'update:filterEnd'
])
</script>

<style scoped>
.filter-bar {
  background: #fff;
  padding: 16px 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}
.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
}
.filter-label {
  color: #666;
  font-weight: 500;
  white-space: nowrap;
}
.filter-input, .filter-select {
  height: 34px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  padding: 0 12px;
  outline: none;
  transition: all 0.3s;
  min-width: 140px;
  font-size: 13px;
  background: #fff;
}
.filter-input:focus, .filter-select:focus {
  border-color: #1890ff;
  box-shadow: 0 0 0 3px rgba(24,144,255,0.1);
}
.date-range {
  display: flex;
  align-items: center;
  gap: 8px;
}
.date-input {
  height: 34px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  padding: 0 12px;
  outline: none;
  font-size: 13px;
  width: 130px;
}
.btn {
  padding: 8px 16px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s;
  font-weight: 500;
}
.btn-default {
  background: #f5f5f5;
  color: #666;
  border: 1px solid #d9d9d9;
}
.btn-default:hover { background: #e8e8e8; color: #333; }
.btn-info {
  background: #1890ff;
  color: #fff;
  border: 1px solid #1890ff;
}
.btn-info:hover { background: #096dd9; border-color: #096dd9; }
</style>
