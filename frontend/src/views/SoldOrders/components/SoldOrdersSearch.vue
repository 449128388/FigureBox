<!--
  SoldOrdersSearch.vue - 已出售订单搜索筛选组件

  功能说明：
  - 提供已出售订单搜索和筛选功能
  - 支持按手办名称、订单编号、卖出平台搜索
  - 提供搜索和重置按钮

  组件依赖：
  - 使用 Element Plus 的 el-input、el-select、el-button 组件

  维护提示：
  - 本地状态用于双向绑定
  - 搜索和重置事件通过 $emit 传递给父组件
-->
<template>
  <div class="search-section">
    <div class="search-form">
      <span style="margin-right: 5px; font-weight: 500;">手办名称:</span>
      <el-input v-model="localSearchFigureName" placeholder="搜索手办名称" style="width: 200px; margin-right: 10px;"></el-input>
      <span style="margin-right: 5px; font-weight: 500;">订单编号:</span>
      <el-input v-model="localSearchOrderNumber" placeholder="搜索订单编号" style="width: 200px; margin-right: 10px;"></el-input>
      <span style="margin-right: 5px; font-weight: 500;">卖出平台:</span>
      <el-select v-model="localSearchSellPlatform" placeholder="选择卖出平台" style="width: 200px; margin-right: 10px;" popper-class="sold-order-platform-popper">
        <el-option value="" label="全部" />
        <el-option value="闲鱼（个人卖家）" label="闲鱼（个人卖家）" />
        <el-option value="闲鱼（鱼小铺）" label="闲鱼（鱼小铺）" />
        <el-option value="淘宝" label="淘宝" />
        <el-option value="转转" label="转转" />
        <el-option value="微信群" label="微信群" />
        <el-option value="QQ群" label="QQ群" />
        <el-option value="快速卖出" label="快速卖出" />
        <el-option value="其他" label="其他" />
      </el-select>
      <el-button type="primary" @click="handleSearch">搜索</el-button>
      <el-button @click="handleReset">重置</el-button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SoldOrdersSearch',
  props: {
    searchFigureName: {
      type: String,
      default: ''
    },
    searchOrderNumber: {
      type: String,
      default: ''
    },
    searchSellPlatform: {
      type: String,
      default: ''
    }
  },
  emits: ['update:searchFigureName', 'update:searchOrderNumber', 'update:searchSellPlatform', 'search', 'reset'],
  computed: {
    localSearchFigureName: {
      get() {
        return this.searchFigureName
      },
      set(value) {
        this.$emit('update:searchFigureName', value)
      }
    },
    localSearchOrderNumber: {
      get() {
        return this.searchOrderNumber
      },
      set(value) {
        this.$emit('update:searchOrderNumber', value)
      }
    },
    localSearchSellPlatform: {
      get() {
        return this.searchSellPlatform
      },
      set(value) {
        this.$emit('update:searchSellPlatform', value)
      }
    }
  },
  methods: {
    handleSearch() {
      this.$emit('search')
    },
    handleReset() {
      this.$emit('reset')
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
  flex-wrap: wrap;
}
</style>

<style>
.sold-order-platform-popper {
  overflow: hidden;
}
</style>
