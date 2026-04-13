<template>
  <div class="activity-feed">
    <div class="section-title">
      <el-icon><ChatDotRound /></el-icon> 动态流
    </div>
    <div class="activities">
      <div 
        v-for="(activity, index) in collectorData?.activities || []" 
        :key="index"
        class="activity-item"
      >
        <div class="activity-date">
          📅 {{ activity.date }}
        </div>
        <div class="activity-content">
          {{ activity.content }}
        </div>
        <div class="activity-actions">
          <el-button 
            v-for="action in activity.actions" 
            :key="action"
            size="small"
            @click="handleActivityAction(action, activity)"
          >
            {{ action }}
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ChatDotRound } from '@element-plus/icons-vue'

export default {
  name: 'ActivityFeed',
  components: { ChatDotRound },
  props: {
    collectorData: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['activity-action'],
  methods: {
    handleActivityAction(action, activity) {
      this.$emit('activity-action', action, activity)
    }
  }
}
</script>

<style scoped>
.activity-feed {
  margin-bottom: 30px;
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
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

.activities {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.activity-item {
  position: relative;
  padding-left: 20px;
  border-left: 3px solid #409EFF;
  transition: transform 0.3s ease;
}

.activity-item:hover {
  transform: translateX(5px);
}

.activity-date {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.activity-content {
  font-size: 14px;
  color: #333;
  margin-bottom: 12px;
  line-height: 1.4;
}

.activity-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .activity-actions {
    justify-content: flex-start;
  }
}
</style>
