<!--
  FigureItem.vue - 手办卡片组件

  功能说明：
  - 展示单个手办的卡片信息
  - 包含手办图片、名称、定价、市场价、入手价格、入手时间、标签等信息
  - 支持点击手办名称跳转到详情页
  - 支持点击标签进行筛选
  - 无图片时显示默认占位图
  - 【新增】支持批量选择模式，显示复选框在图片左上角

  组件依赖：
  - 接收 figure 作为 props，包含手办的详细信息
  - 接收 searchTagIds 作为 props，用于高亮当前筛选的标签
  - 接收 isBatchMode 作为 props，控制是否显示批量选择模式
  - 接收 isSelected 作为 props，控制复选框选中状态
  - 接收 isDisabled 作为 props，控制复选框禁用状态
  - 接收 disabledTooltip 作为 props，禁用时显示的提示信息

  维护提示：
  - 使用 router-link 实现详情页跳转
  - 使用 getCurrencySymbol 方法获取货币符号
  - 使用 getSortedTags 方法对标签进行排序
  - 入手价格只在有订单时显示（order_count > 0）
  - 标签点击事件通过 filter-by-tag 事件向父组件传递
  - 使用 Element Plus 的 ElButton 和 ElButtonGroup 实现编辑/删除/更多按钮
  - 使用 flex 布局将按钮固定在卡片底部，避免内容缺失时出现空洞
  - 【新增】批量选择时，选中状态添加蓝色边框效果
-->
<template>
  <div
    class="figure-item"
    :class="{
      'figure-item--selected': isSelected,
      'figure-item--batch-mode': isBatchMode
    }"
  >
    <div class="figure-content">
      <div class="figure-image">
        <!-- 【新增】批量选择复选框 -->
        <div
          v-if="isBatchMode"
          class="batch-checkbox-wrapper"
        >
          <el-tooltip
            v-if="isDisabled"
            :content="disabledTooltip"
            placement="top"
          >
            <div class="checkbox-container checkbox--disabled" @click.stop>
              <el-checkbox
                :model-value="false"
                disabled
                size="large"
              />
            </div>
          </el-tooltip>
          <div
            v-else
            class="checkbox-container"
            :class="{ 'checkbox--checked': isSelected }"
            @click.stop
          >
            <el-checkbox
              :model-value="isSelected"
              size="large"
              @change="handleCheckboxChange"
            />
          </div>
        </div>
        <img
          :src="figure.image || '/imgs/no_image.png'"
          :alt="figure.name"
          loading="lazy"
          decoding="async"
        >
      </div>
      <h3><router-link :to="`/figures/${figure.id}`" class="figure-name-link">{{ figure.name }}</router-link></h3>
      <p>官方定价: {{ figure.price !== null && figure.price !== undefined ? figure.price : '未设置' }} {{ getCurrencySymbol(figure.currency) }}</p>
      <p v-if="figure.market_price !== null && figure.market_price !== undefined">市场价: {{ figure.market_price }} {{ getCurrencySymbol(figure.market_currency) }}</p>
      <p v-else>市场价: 未设置</p>
      <!-- 【优化】只在有订单时显示入手价格 -->
      <p v-if="figure.order_count > 0 && figure.average_purchase_price > 0">
        入手价格: {{ figure.average_purchase_price.toFixed(2) }} {{ getCurrencySymbol(figure.purchase_currency) }}
      </p>
      <p v-if="figure.purchase_date">入手时间: {{ figure.purchase_date }}</p>
      <div v-if="figure.tags && figure.tags.length > 0" class="tags-container">
        <span class="tags-label">标签:</span>
        <el-tag
          v-for="tag in getSortedTags(figure.tags)"
          :key="tag.id"
          size="small"
          effect="light"
          class="clickable-tag"
          @click="$emit('filter-by-tag', tag.id)"
          style="margin-right: 4px; margin-bottom: 4px; cursor: pointer;"
          :type="searchTagIds.includes(tag.id) ? 'primary' : ''"
        >
          {{ tag.name }}
        </el-tag>
      </div>
    </div>
    <div class="figure-actions">
      <!-- 编辑/删除/更多按钮组 -->
      <el-button-group class="action-button-group">
        <el-button
          type="primary"
          :icon="Edit"
          @click="$emit('edit', figure)"
        >
          编辑
        </el-button>
        <el-button
          type="danger"
          :icon="Delete"
          @click="$emit('delete', figure)"
        >
          删除
        </el-button>
        <el-button
          type="info"
        >
          更多
        </el-button>
      </el-button-group>
    </div>
  </div>
</template>

<script>
import { Edit, Delete, More } from '@element-plus/icons-vue'

export default {
  name: 'FigureItem',
  props: {
    figure: {
      type: Object,
      required: true
    },
    searchTagIds: {
      type: Array,
      default: () => []
    },
    // 【新增】批量选择相关 props
    isBatchMode: {
      type: Boolean,
      default: false
    },
    isSelected: {
      type: Boolean,
      default: false
    },
    isDisabled: {
      type: Boolean,
      default: false
    },
    disabledTooltip: {
      type: String,
      default: '该手办存在未完成订单'
    }
  },
  emits: ['edit', 'delete', 'filter-by-tag', 'toggle-selection'],
  setup(props, { emit }) {
    // 【新增】处理复选框状态变化
    const handleCheckboxChange = (value) => {
      emit('toggle-selection', props.figure.id, value)
    }

    return {
      Edit,
      Delete,
      More,
      handleCheckboxChange
    }
  },
  methods: {
    getCurrencySymbol(currency) {
      switch(currency) {
        case 'CNY': return '元'
        case 'JPY': return '日元'
        case 'USD': return '美元'
        case 'EUR': return '欧元'
        default: return '元'
      }
    },
    getSortedTags(tags) {
      if (!tags || !Array.isArray(tags)) return []
      return [...tags].sort((a, b) => a.id - b.id)
    }
  }
}
</script>

<style scoped>
.figure-item {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  contain: layout style paint;
  will-change: transform;
  /* 【优化】使用 flex 布局，让按钮固定在底部 */
  display: flex;
  flex-direction: column;
  height: 100%;
}

.figure-content {
  /* 【优化】内容区占据剩余空间，留白会在这里 */
  flex: 1;
}

.figure-item h3 {
  margin-bottom: 10px;
  color: #333;
}

.figure-name-link {
  color: #2196F3;
  text-decoration: none;
  transition: color 0.3s ease;
}

.figure-name-link:hover {
  color: #0b7dda;
}

.figure-item p {
  margin-bottom: 5px;
  color: #666;
}

.tags-container {
  margin-bottom: 10px;
}

.tags-label {
  font-weight: 500;
  margin-right: 8px;
  color: #666;
}

.figure-actions {
  display: flex;
  justify-content: center;
  margin-top: auto; /* 【优化】使用 auto margin 将按钮推到底部 */
  padding-top: 15px;
  border-top: 1px solid #eee;
}

/* Element Plus 按钮组样式优化 - 三个按钮居中分布 */
.action-button-group {
  display: flex;
  gap: 0;
}

.action-button-group :deep(.el-button) {
  min-width: 80px;
}

/* 手办图片样式 */
.figure-image {
  width: 100%;
  height: 200px;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 15px;
  background-color: #f5f5f5;
  /* 【新增】相对定位，用于复选框绝对定位 */
  position: relative;
}

.figure-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  content-visibility: auto;
}

/* 【新增】批量选择复选框样式 */
.batch-checkbox-wrapper {
  position: absolute;
  top: 8px;
  left: 8px;
  z-index: 10;
}

.checkbox-container {
  background: transparent;
  border-radius: 4px;
  padding: 4px;
  transition: all 0.3s ease;
}

.checkbox-container:hover {
  background: transparent;
}

.checkbox--checked {
  background: transparent;
}

.checkbox--disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 【新增】选中状态的卡片样式 */
.figure-item--selected {
  border: 2px solid #3B82F6;
  box-shadow: 0 4px 20px rgba(59, 130, 246, 0.3);
  transform: translateY(-2px);
  transition: all 0.3s ease;
}

.figure-item--batch-mode {
  cursor: pointer;
}

/* 复选框自定义样式 - 透明背景 */
:deep(.el-checkbox) {
  background: transparent;
}

:deep(.el-checkbox__input) {
  background: transparent;
}

:deep(.el-checkbox__inner) {
  background-color: rgba(255, 255, 255, 0.9);
  border-color: #dcdfe6;
}

:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #3B82F6;
  border-color: #3B82F6;
}

:deep(.el-checkbox__input.is-checked + .el-checkbox__label) {
  color: #3B82F6;
}

:deep(.el-checkbox__inner:hover) {
  border-color: #3B82F6;
}

:deep(.el-checkbox__input.is-disabled .el-checkbox__inner) {
  background-color: rgba(245, 247, 250, 0.9);
}

@media (max-width: 768px) {
  .figure-image {
    height: 150px;
  }
}
</style>
