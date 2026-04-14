<!--
  FiguresSearch.vue - 手办搜索筛选组件

  功能说明：
  - 提供手办搜索和筛选功能
  - 支持按名称、入手形式、入手时间范围搜索
  - 支持标签筛选和显示当前筛选的标签
  - 提供搜索和重置按钮

  组件依赖：
  - 使用 Element Plus 的 el-input、el-select、el-date-picker、el-button、el-tag 组件
  - 接收 tagStore 作为 props，用于获取标签信息

  维护提示：
  - 本地状态 localSearchName、localSearchPurchaseType、localSearchPurchaseDateRange 用于双向绑定
  - 搜索和重置事件通过 $emit 传递给父组件
  - 标签筛选通过 filter-by-tag 事件向父组件传递
-->
<template>
  <div class="search-section">
    <div class="search-form">
      <span style="margin-right: 5px; font-weight: 500;">名称:</span>
      <el-input v-model="localSearchName" placeholder="搜索名称" style="width: 200px; margin-right: 10px;"></el-input>
      <span style="margin-right: 5px; font-weight: 500;">入手形式:</span>
      <el-select v-model="localSearchPurchaseType" placeholder="选择入手形式" style="width: 200px; margin-right: 10px;">
        <el-option value="" label="全部" />
        <el-option value="OTHER" label="其他" />
        <el-option value="PREORDER" label="预定" />
        <el-option value="INSTOCK" label="现货" />
        <el-option value="SECONDHAND" label="二手" />
        <el-option value="LOOSE" label="散货" />
        <el-option value="DOMESTIC" label="国产" />
      </el-select>
      <span style="margin-right: 5px; font-weight: 500;">入手时间:</span>
      <el-date-picker v-model="localSearchPurchaseDateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" style="width: 500px; min-width: 500px; max-width: 500px; margin-right: 10px;"></el-date-picker>
      <el-button type="primary" @click="handleSearch">搜索</el-button>
      <el-button @click="handleReset">重置</el-button>
    </div>
    <!-- 标签筛选显示 -->
    <div v-if="searchTagIds.length > 0" class="tag-filter-info" style="margin-top: 10px; padding: 8px 12px; background-color: #f0f9ff; border-radius: 4px; display: inline-flex; align-items: center; flex-wrap: wrap; gap: 8px;">
      <span style="color: #606266; margin-right: 4px;">当前标签筛选:</span>
      <el-tag 
        v-for="tagId in searchTagIds" 
        :key="tagId"
        size="small" 
        type="primary" 
        closable 
        @close="$emit('filter-by-tag', tagId)"
        style="font-size: 14px;"
      >
        {{ getTagNameById(tagId) }}
      </el-tag>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FiguresSearch',
  props: {
    searchName: {
      type: String,
      default: ''
    },
    searchPurchaseType: {
      type: String,
      default: ''
    },
    searchPurchaseDateRange: {
      type: Array,
      default: () => []
    },
    searchTagIds: {
      type: Array,
      default: () => []
    },
    tagStore: {
      type: Object,
      required: true
    }
  },
  emits: ['update:searchName', 'update:searchPurchaseType', 'update:searchPurchaseDateRange', 'search', 'reset', 'filter-by-tag'],
  computed: {
    localSearchName: {
      get() {
        return this.searchName
      },
      set(value) {
        this.$emit('update:searchName', value)
      }
    },
    localSearchPurchaseType: {
      get() {
        return this.searchPurchaseType
      },
      set(value) {
        this.$emit('update:searchPurchaseType', value)
      }
    },
    localSearchPurchaseDateRange: {
      get() {
        return this.searchPurchaseDateRange
      },
      set(value) {
        this.$emit('update:searchPurchaseDateRange', value)
      }
    }
  },
  methods: {
    handleSearch() {
      this.$emit('search')
    },
    handleReset() {
      this.$emit('reset')
    },
    getTagNameById(tagId) {
      const tag = this.tagStore.tags.find(t => t.id === tagId)
      return tag ? tag.name : ''
    }
  }
}
</script>

<style scoped>
.search-section {
  margin-bottom: 30px;
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.search-form {
  display: flex;
  align-items: center;
  gap: 15px;
  width: 100%;
  justify-content: flex-start;
}
</style>
