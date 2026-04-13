<template>
  <div class="collector-header">
    <div class="avatar">[头像]</div>
    <h3>我的塑料资产</h3>
    <div class="header-actions">
      <el-button @click="sharePoster">分享海报</el-button>
      <el-button @click="privacySettings">
        隐私设置 <el-icon><View /></el-icon>
      </el-button>
    </div>
  </div>
</template>

<script>
import { View } from '@element-plus/icons-vue'

export default {
  name: 'CollectorHeader',
  components: { View },
  emits: ['share-poster', 'privacy-settings'],
  methods: {
    sharePoster() {
      this.$emit('share-poster')
    },
    privacySettings() {
      this.$emit('privacy-settings')
    }
  }
}
</script>

<style scoped>
.collector-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 30px;
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #666;
}

.collector-header h3 {
  margin: 0;
  color: #333;
  font-size: 20px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 10px;
}

@media (max-width: 768px) {
  .collector-header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .header-actions {
    width: 100%;
    justify-content: center;
  }
}
</style>
