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
  - 收货按钮仅在订单状态为 '已支付' 时显示
  - 按钮点击事件通过 editOrder、receiveOrder、deleteOrder 事件向父组件传递
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
    <p>定金: ¥{{ order.deposit }}</p>
    <p>尾款: ¥{{ order.balance }}</p>
    <p>出荷日期: {{ order.due_date }}</p>
    <p>尾款状态: {{ order.status }}</p>
    <p v-if="order.shop_name">购买店铺: {{ order.shop_name }}</p>
    <p v-if="order.shop_contact">店铺联系方式: {{ order.shop_contact }}</p>
    <p v-if="order.tracking_number">物流订单: {{ order.tracking_number }}</p>
    <button class="btn btn-edit" @click="$emit('editOrder', order)">编辑</button>
    <button v-if="order.status === '已支付'" class="btn btn-receive" @click="$emit('receiveOrder', order)">收货</button>
    <button class="btn btn-delete" @click="$emit('deleteOrder', order.id)">删除</button>
  </div>
</template>

<script>
export default {
  name: 'OrderItem',
  props: {
    order: {
      type: Object,
      required: true
    }
  },
  emits: ['editOrder', 'receiveOrder', 'deleteOrder'],
  methods: {
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

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  margin-right: 10px;
  margin-top: 10px;
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

.btn-receive {
  background-color: #4CAF50;
  color: white;
}

.btn-receive:hover {
  background-color: #45a049;
}
</style>