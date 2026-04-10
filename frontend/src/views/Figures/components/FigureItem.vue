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
    <p>定价: {{ figure.price !== null && figure.price !== undefined ? figure.price : '未设置' }} {{ getCurrencySymbol(figure.currency) }}</p>
    <p v-if="figure.market_price !== null && figure.market_price !== undefined">市场价: {{ figure.market_price }} {{ getCurrencySymbol(figure.market_currency) }}</p>
    <p v-else>市场价: 未设置</p>
    <p v-if="figure.purchase_price !== null && figure.purchase_price !== undefined">入手价格: {{ figure.purchase_price }} {{ getCurrencySymbol(figure.purchase_currency) }}</p>
    <p v-else>入手价格: 未设置</p>
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
      <button class="btn btn-edit" @click="$emit('edit', figure)">编辑</button>
      <button class="btn btn-delete" @click="$emit('delete', figure.id)">删除</button>
    </div>
  </div>
</template>

<script>
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
  gap: 10px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.figure-actions .btn {
  margin: 0;
  flex: 1;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.btn-edit {
  background-color: #2196F3;
  color: white;
}

.btn-edit:hover {
  background-color: #0b7dda;
}

.btn-delete {
  background-color: #f44336;
  color: white;
}

.btn-delete:hover {
  background-color: #da190b;
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
