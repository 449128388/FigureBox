<!--
  ValuableCollections.vue - 收藏家模式高价值藏品组件

  功能说明：
  - 展示高价值手办藏品列表
  - 显示藏品图片、状态和收益情况
  - 区分已转卖和在售藏品的显示样式
  - 支持点击查看更多藏品

  组件依赖：
  - 接收 collectorData 作为 props，包含 valuable_items 数组

  维护提示：
  - 根据藏品状态显示不同样式
  - 收益为正负数时显示不同颜色
-->
<template>
  <div class="valuable-collections">
    <div class="section-title">
      <el-icon><Picture /></el-icon> 高价值藏品
    </div>
    <div class="collections-grid">
      <div 
        v-for="item in collectorData?.valuable_items || []" 
        :key="item.id"
        class="collection-item"
        :class="{ 'sold-item': item.status === '已转卖' }"
      >
        <div class="item-image">
          <img :src="item.image" :alt="item.name" />
        </div>
        <div v-if="item.status === '已转卖'" class="item-status sold">
          已转卖
        </div>
        <div v-else class="item-profit" :class="{ positive: item.profit >= 0, negative: item.profit < 0 }">
          {{ item.profit >= 0 ? '💹+' : '🔻' }}¥{{ Math.abs(item.profit) }}
        </div>
        <div class="item-status">
          {{ item.status }}
        </div>
        <div v-if="item.sold_profit" class="sold-profit">
          利润¥{{ item.sold_profit }}
        </div>
      </div>
      <!-- 更多按钮 -->
      <div class="collection-item more-item">
        <div class="more-content">
          <span>+15</span>
          <p>更多</p>
        </div>
      </div>
      <div class="collection-item more-item">
        <div class="more-content">
          <span>+15</span>
          <p>更多</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Picture } from '@element-plus/icons-vue'

export default {
  name: 'ValuableCollections',
  components: { Picture },
  props: {
    collectorData: {
      type: Object,
      default: () => ({})
    }
  }
}
</script>

<style scoped>
.valuable-collections {
  margin-bottom: 30px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 20px;
}

.collections-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.collection-item {
  position: relative;
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.collection-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.item-image {
  width: 100%;
  height: 200px;
  overflow: hidden;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.collection-item:hover .item-image img {
  transform: scale(1.05);
}

.item-profit {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
}

.item-profit.positive {
  background-color: rgba(76, 175, 80, 0.8);
}

.item-profit.negative {
  background-color: rgba(244, 67, 54, 0.8);
}

.item-status {
  padding: 15px;
  text-align: center;
  font-weight: bold;
  color: #333;
}

.sold-item .item-status.sold {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  background-color: rgba(255, 152, 0, 0.8);
  color: white;
  padding: 5px;
  font-size: 14px;
}

.sold-item .sold-profit {
  padding: 0 15px 15px;
  text-align: center;
  color: #666;
  font-size: 14px;
}

.more-item {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  border: 2px dashed #e0e0e0;
  min-height: 200px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.more-item:hover {
  border-color: #2196F3;
  background-color: rgba(33, 150, 243, 0.05);
}

.more-content {
  text-align: center;
}

.more-content span {
  display: block;
  font-size: 32px;
  font-weight: bold;
  color: #999;
  margin-bottom: 10px;
}

.more-content p {
  margin: 0;
  font-size: 14px;
  color: #666;
}

@media (max-width: 768px) {
  .collections-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
