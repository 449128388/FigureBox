<!--
  FigureItem.vue - 手办卡片组件

  功能说明：
  - 展示单个手办的卡片信息
  - 包含手办图片、名称、定价、市场价、入手价格、入手时间、标签等信息
  - 支持点击手办名称跳转到详情页
  - 支持点击标签进行筛选
  - 无图片时显示默认占位图

  组件依赖：
  - 接收 figure 作为 props，包含手办的详细信息
  - 接收 searchTagIds 作为 props，用于高亮当前筛选的标签

  维护提示：
  - 使用 router-link 实现详情页跳转
  - 使用 getCurrencySymbol 方法获取货币符号
  - 使用 getSortedTags 方法对标签进行排序
  - 标签点击事件通过 filter-by-tag 事件向父组件传递
  - 使用 Element Plus 的 ElButton 和 ElButtonGroup 实现编辑/删除/更多按钮
-->
<template>
  <div class="figure-item">
    <div class="figure-image">
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
    <!-- 【优化】列表中不显示入手价格，改为在详情/编辑中显示计算后的平均入手价格 -->
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
    }
  },
  emits: ['edit', 'delete', 'filter-by-tag'],
  setup() {
    return {
      Edit,
      Delete,
      More
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
  margin-top: 15px;
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
}

.figure-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  content-visibility: auto;
}

@media (max-width: 768px) {
  .figure-image {
    height: 150px;
  }
}
</style>
