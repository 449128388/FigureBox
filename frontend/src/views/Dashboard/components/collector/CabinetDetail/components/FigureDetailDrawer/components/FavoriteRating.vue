<!--
  FavoriteRating.vue - 喜爱度评分子组件

  Props:
  - rating: Number - 当前评分值(0-5)

  Events:
  - update-rating: 评分变化时触发，参数 { rating }
-->
<template>
  <div class="section">
    <div class="section-title">喜爱度</div>
    <div class="favorite-editor">
      <div class="star-group">
        <span
          v-for="n in 5"
          :key="n"
          class="star"
          :class="{ active: n <= currentRating }"
          @click="setRating(n)"
        >★</span>
      </div>
      <span class="star-hint">{{ starHint }}</span>
    </div>
  </div>
</template>

<script>
import { STAR_LABELS } from '../constants/figureDetailConfig'

export default {
  name: 'FavoriteRating',

  props: {
    rating: {
      type: Number,
      default: 0
    }
  },

  data() {
    return {
      currentRating: this.rating,
      starLabels: STAR_LABELS
    }
  },

  computed: {
    starHint() {
      return this.starLabels[this.currentRating] || this.starLabels[0]
    }
  },

  watch: {
    rating(val) {
      this.currentRating = val
    }
  },

  methods: {
    setRating(n) {
      this.currentRating = n
      this.$emit('update-rating', { rating: n })
    }
  }
}
</script>

<style scoped>
.section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #1F1F1F;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.section-title::before {
  content: "";
  display: inline-block;
  width: 3px;
  height: 14px;
  background: #C49A6C;
  border-radius: 2px;
}

.favorite-editor {
  display: flex;
  align-items: center;
  gap: 12px;
}

.star-group {
  display: flex;
  gap: 4px;
  cursor: pointer;
}

.star {
  font-size: 22px;
  color: #DDD;
  transition: color 0.2s;
  user-select: none;
}

.star.active {
  color: #E6A23C;
}

.star:hover {
  color: #E6A23C;
}

.star-hint {
  font-size: 12px;
  color: #999;
}
</style>
