<!--
  StarRating.vue - 星级评分交互组件

  功能说明：
  - 展示当前评分（5星显示）
  - 支持点击展开编辑模式（5颗可点击星星）
  - 支持点击设置评分（1-5星）
  - 支持设置评分后自动保存

  Props:
  - rating: Number - 当前评分值（0-5）
  - isEditing: Boolean - 是否处于编辑模式
  - size: String - 星星大小 'default' | 'small' | 'mini'

  Events:
  - click: 点击组件时触发
  - set-rating: 设置评分时触发，参数 { rating }
-->
<template>
  <div
    class="star-rating"
    :class="{ 'is-editing': isEditing, [`size-${size}`]: true }"
    @click.stop="handleClick"
  >
    <template v-if="isEditing">
      <span
        v-for="s in 5"
        :key="s"
        class="star-btn"
        :class="{ filled: s <= tempValue }"
        @click.stop="handleSetRating(s)"
      >★</span>
    </template>
    <template v-else>
      <span
        v-for="s in 5"
        :key="s"
        class="star-display"
        :class="{ filled: s <= displayRating }"
      >★</span>
    </template>
  </div>
</template>

<script>
export default {
  name: 'StarRating',

  emits: ['click', 'set-rating'],

  props: {
    rating: {
      type: Number,
      default: 0
    },
    isEditing: {
      type: Boolean,
      default: false
    },
    size: {
      type: String,
      default: 'default',
      validator: (value) => ['default', 'small', 'mini'].includes(value)
    }
  },

  data() {
    return {
      tempValue: 0
    }
  },

  computed: {
    /**
     * 展示的评分值
     */
    displayRating() {
      return this.rating || 0
    }
  },

  watch: {
    isEditing: {
      immediate: true,
      handler(val) {
        if (val) {
          this.tempValue = this.rating || 0
        }
      }
    }
  },

  methods: {
    /**
     * 处理点击事件
     */
    handleClick() {
      this.$emit('click')
    },

    /**
     * 处理设置评分
     * @param {number} rating - 评分值
     */
    handleSetRating(rating) {
      this.$emit('set-rating', { rating })
    }
  }
}
</script>

<style scoped>
.star-rating {
  display: inline-flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.9);
  padding: 3px 8px;
  border-radius: 10px;
  font-size: 13px;
  color: #E6A23C;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
  letter-spacing: 1px;
}

.star-rating:hover {
  background: rgba(255, 255, 255, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
}

.star-rating.is-editing {
  background: #fff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  padding: 4px 10px;
}

/* 尺寸变体 */
.star-rating.size-small {
  font-size: 11px;
  padding: 2px 6px;
}

.star-rating.size-mini {
  font-size: 10px;
  padding: 1px 4px;
}

.star-display,
.star-btn {
  display: inline-block;
  transition: transform 0.15s, color 0.15s;
  color: #ddd;
}

.star-display.filled,
.star-btn.filled {
  color: #E6A23C;
}

.star-btn {
  cursor: pointer;
}

.star-btn:hover {
  transform: scale(1.3);
  color: #E6A23C;
}
</style>
