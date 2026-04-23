<!--
  OrderItem.vue - 订单卡片组件

  功能说明：
  - 展示单个订单的卡片信息
  - 包含手办图片、名称、定金、尾款、出荷日期、状态等信息
  - 显示购买店铺、联系方式、物流订单等可选信息
  - 支持点击手办名称跳转到详情页
  - 显示倒计时标签（对于未完成和未取消的订单）
  - 提供编辑、收货、删除按钮

  组件依赖：
  - 接收 order 作为 props，包含订单的详细信息

  维护提示：
  - 使用 router-link 实现详情页跳转
  - 倒计时标签样式通过 getCountdownClass 方法获取
  - 倒计时文本通过 getCountdownText 方法获取
  - 定金/尾款金额后显示币种单位（元/日元/美元/欧元）
  - 使用 getCurrencySymbol 方法获取币种对应的单位
  - 收货按钮仅在订单状态为 '已支付' 时显示
  - 按钮点击事件通过 editOrder、receiveOrder、deleteOrder 事件向父组件传递
  - 使用 Element Plus 的 ElButton 和 ElButtonGroup 实现编辑/收货/删除按钮
-->
<template>
  <div class="order-item">
    <div class="figure-image">
      <img
        :src="order.figure_image || '/imgs/no_image.png'"
        :alt="order.figure_name"
        loading="lazy"
        decoding="async"
      >
    </div>
    <h3><router-link :to="`/figures/${order.figure_id}`" class="figure-name-link">{{ order.figure_name }}</router-link><span v-if="order.status !== '已完成' && order.status !== '已取消'" class="countdown-tag" :class="getCountdownClass(order.due_date)">{{ getCountdownText(order.due_date) }}</span></h3>
    <p v-if="order.order_number">订单编号: {{ order.order_number }}</p>
    <p>定金: {{ order.deposit }} {{ getCurrencySymbol(order.deposit_currency) }}</p>
    <p>尾款: {{ order.balance }} {{ getCurrencySymbol(order.balance_currency) }}</p>
    <p>出荷日期: {{ order.due_date }}</p>
    <p>尾款状态: {{ order.status }}</p>
    <p v-if="order.shop_name">购买店铺: {{ order.shop_name }}</p>
    <p v-if="order.shop_contact">店铺联系方式: {{ order.shop_contact }}</p>
    <p v-if="order.tracking_number">物流订单: {{ order.tracking_number }}</p>
    <div class="order-actions">
      <!-- 编辑/收货/删除按钮组 -->
      <el-button-group class="action-button-group">
        <el-button
          type="primary"
          :icon="Edit"
          @click="$emit('editOrder', order)"
        >
          编辑
        </el-button>
        <el-button
          v-if="order.status === '已支付'"
          type="success"
          :icon="Check"
          @click="$emit('receiveOrder', order)"
        >
          收货
        </el-button>
        <el-button
          type="danger"
          :icon="Delete"
          @click="$emit('deleteOrder', order)"
        >
          删除
        </el-button>
      </el-button-group>
    </div>
  </div>
</template>

<script>
import { Edit, Delete, Check } from '@element-plus/icons-vue'

export default {
  name: 'OrderItem',
  props: {
    order: {
      type: Object,
      required: true
    }
  },
  emits: ['editOrder', 'receiveOrder', 'deleteOrder'],
  setup() {
    return {
      Edit,
      Delete,
      Check
    }
  },
  methods: {
    // 获取币种符号
    getCurrencySymbol(currency) {
      switch(currency) {
        case 'CNY': return '元'
        case 'JPY': return '日元'
        case 'USD': return '美元'
        case 'EUR': return '欧元'
        default: return '元'
      }
    },

    // 获取倒计时文本
    getCountdownText(dueDate) {
      if (!dueDate) return ''

      const today = new Date()
      today.setHours(0, 0, 0, 0)

      const due = new Date(dueDate)
      due.setHours(0, 0, 0, 0)

      const diffTime = due - today
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

      if (diffDays < 0) {
        return `已出荷 ${Math.abs(diffDays)} 天`
      } else if (diffDays === 0) {
        return '今天出荷'
      } else {
        return `还有 ${diffDays} 天`
      }
    },

    // 获取倒计时样式类
    getCountdownClass(dueDate) {
      if (!dueDate) return ''

      const today = new Date()
      today.setHours(0, 0, 0, 0)

      const due = new Date(dueDate)
      due.setHours(0, 0, 0, 0)

      const diffTime = due - today
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

      if (diffDays < 0) {
        return 'countdown-overdue'
      } else if (diffDays === 0) {
        return 'countdown-today'
      } else if (diffDays <= 7) {
        return 'countdown-urgent'
      } else if (diffDays <= 30) {
        return 'countdown-warning'
      } else {
        return 'countdown-normal'
      }
    }
  }
}
</script>

<style scoped>
.order-item {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  /* 使用flex布局，使按钮固定在底部 */
  display: flex;
  flex-direction: column;
  height: 100%;
}

.order-item .figure-image {
  width: 100%;
  height: 200px;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 15px;
  background-color: #f5f5f5;
}

.order-item .figure-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  content-visibility: auto;
}

.order-item h3 {
  margin-bottom: 10px;
  color: #333;
}

.order-item p {
  margin-bottom: 5px;
  color: #666;
}

.figure-name-link {
  color: #333;
  text-decoration: none;
  cursor: pointer;
  transition: color 0.3s ease;
}

.figure-name-link:hover {
  color: #2196F3;
}

.countdown-tag {
  display: inline-block;
  margin-left: 10px;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: 2px solid transparent;
}

.countdown-normal {
  background-color: #e8f5e9;
  color: #2e7d32;
  border-color: #4caf50;
}

.countdown-warning {
  background-color: #fff3e0;
  color: #e65100;
  border-color: #ff9800;
}

.countdown-urgent {
  background-color: #ffebee;
  color: #c62828;
  border-color: #f44336;
  animation: pulse 2s infinite;
}

.countdown-today {
  background-color: #e3f2fd;
  color: #1565c0;
  border-color: #2196f3;
  animation: pulse 2s infinite;
}

.countdown-overdue {
  background-color: #f5f5f5;
  color: #616161;
  border-color: #9e9e9e;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(244, 67, 54, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(244, 67, 54, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(244, 67, 54, 0);
  }
}

.order-actions {
  display: flex;
  justify-content: center;
  margin-top: auto; /* 将按钮推到容器底部 */
  padding-top: 15px;
  border-top: 1px solid #eee;
}

/* Element Plus 按钮组样式优化 - 按钮居中分布 */
.action-button-group {
  display: flex;
  gap: 0;
}

.action-button-group :deep(.el-button) {
  min-width: 80px;
}
</style>
