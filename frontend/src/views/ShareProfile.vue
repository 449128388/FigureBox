<!--
  ShareProfile.vue - 收藏家分享主页（无需登录，复用收藏家组件）

  根据隐私设置展示不同级别的数据：
  - 公开 + 完整数据：展示完整收藏家主页（复用 CollectorOverview、CollectionCabinets 等）
  - 公开 + 仅统计：只展示统计卡片和提示
  - 私密：提示用户主页已设为私密
-->
<template>
  <div class="share-page" v-if="!loading">
    <!-- 私密 -->
    <div v-if="profileData && profileData.visible === false" class="private-container">
      <div class="private-icon">🔒</div>
      <h2 class="private-title">该用户主页已设为私密</h2>
      <p class="private-desc">仅自己可见</p>
    </div>

    <!-- Token 失效 -->
    <div v-else-if="error" class="private-container">
      <div class="private-icon">⚠️</div>
      <h2 class="private-title">链接已失效</h2>
      <p class="private-desc">{{ error }}</p>
    </div>

    <!-- 公开数据 — 复用收藏家组件 -->
    <div v-else-if="profileData" class="profile-wrapper">
      <div class="share-header">
        <div class="share-header-left">
          <div class="share-avatar">🧸</div>
          <div class="share-info">
            <div class="share-nickname">{{ profileData.nickname }}</div>
            <div class="share-subtitle">手办收藏家</div>
          </div>
        </div>
        <div class="share-badge" v-if="profileData.from_poster">📸 来自海报</div>
      </div>

      <!-- 仅统计模式 - 简化展示 -->
      <div v-if="profileData.summary_only" class="share-stats">
        <div class="share-stat-card" v-if="profileData.summary?.total_collection !== undefined">
          <div class="share-stat-value">{{ profileData.summary.total_collection }}</div>
          <div class="share-stat-label">藏品总数</div>
        </div>
        <div class="share-stat-card" v-if="profileData.summary?.this_month_count !== undefined">
          <div class="share-stat-value green">+{{ profileData.summary.this_month_count }}</div>
          <div class="share-stat-label">本月新入柜</div>
        </div>
        <div class="share-stat-card" v-if="profileData.summary?.total_sold_count !== undefined">
          <div class="share-stat-value">{{ profileData.summary.total_sold_count }}</div>
          <div class="share-stat-label">已出藏品</div>
        </div>
      </div>
      <div v-if="profileData.summary_only" class="share-notice">
        <span class="share-notice-icon">📊</span> 该用户未公开藏品明细
      </div>

      <!-- 仅藏品名模式 -->
      <div v-if="profileData.names_only" class="share-stats">
        <div class="share-stat-card">
          <div class="share-stat-value">{{ profileData.summary?.total_collection ?? '--' }}</div>
          <div class="share-stat-label">藏品总数</div>
        </div>
        <div class="share-stat-card">
          <div class="share-stat-value">{{ profileData.summary?.total_sold_count ?? '--' }}</div>
          <div class="share-stat-label">已出藏品</div>
        </div>
      </div>
      <div v-if="profileData.names_only" class="share-notice names-only">
        <span class="share-notice-icon">🏷️</span> 该用户仅公开藏品名称
      </div>

      <!-- 完整数据模式 - 复用收藏家组件 -->
      <template v-if="!profileData.summary_only && !profileData.names_only">
        <CollectorOverview :collector-data="profileData" />
        <CollectionCabinets :collector-data="profileData" />
        <TagCloud :collector-data="profileData" />
        <ActivityFeed :collector-data="profileData" />
      </template>
    </div>

    <!-- 加载中 -->
    <div v-else class="loading-container">
      <div class="loading-spinner"></div>
      <div class="loading-text">加载中...</div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from '@/axios'

import CollectorOverview from './Dashboard/components/collector/CollectorOverview.vue'
import CollectionCabinets from './Dashboard/components/collector/CollectionCabinets.vue'
import TagCloud from './Dashboard/components/collector/TagCloud.vue'
import ActivityFeed from './Dashboard/components/collector/ActivityFeed.vue'

export default {
  name: 'ShareProfile',
  components: {
    CollectorOverview,
    CollectionCabinets,
    TagCloud,
    ActivityFeed
  },
  setup() {
    const route = useRoute()
    const profileData = ref(null)
    const loading = ref(true)
    const error = ref('')

    onMounted(async () => {
      const userId = route.params.userId
      const token = route.query.token
      const poster = route.query.poster || '0'

      if (!token) {
        error.value = '缺少分享鉴权令牌'
        loading.value = false
        return
      }

      const authParams = { token, poster }

      try {
        // 1. 先获取 profile（含隐私级别信息）
        const profile = await axios.get(`/collector/share/profile/${userId}`, {
          params: authParams
        })

        // 2. 根据每个隐私开关按需请求对应接口
        const promiseMap = []
        // show_total → summary
        if (profile.show_total) {
          promiseMap.push({ key: 'summary', idx: promiseMap.length })
        }
        // show_figures (完整数据模式) → cabinets
        if (profile.show_figures) {
          promiseMap.push({ key: 'cabinets', idx: promiseMap.length })
        }
        // show_tags (完整数据模式) → tags
        if (profile.show_tags) {
          promiseMap.push({ key: 'tags', idx: promiseMap.length })
        }
        // show_feed (完整数据模式) → activities
        if (profile.show_feed) {
          promiseMap.push({ key: 'activities', idx: promiseMap.length })
        }

        const promises = promiseMap.map(entry =>
          axios.get(`/collector/share/${entry.key}/${userId}`, { params: { token } })
        )

        const results = await Promise.all(promises)

        // 3. 合并数据
        const merged = {
          ...profile,
          summary: {},
          cabinets: [],
          tags: { tags: [], system_tags: [], user_tags: [] },
          activities: []
        }

        for (let i = 0; i < results.length; i++) {
          const key = promiseMap[i].key
          if (key === 'summary') merged.summary = results[i] || {}
          else if (key === 'cabinets') merged.cabinets = results[i] || []
          else if (key === 'tags') merged.tags = results[i] || { tags: [], system_tags: [], user_tags: [] }
          else if (key === 'activities') merged.activities = results[i] || []
        }

        profileData.value = merged
      } catch (e) {
        if (e.response?.status === 403) {
          error.value = '链接已失效，请让收藏家重新生成分享链接'
        } else {
          error.value = e.response?.data?.detail || '加载失败'
        }
      } finally {
        loading.value = false
      }
    })

    return { profileData, loading, error }
  }
}
</script>

<style scoped>
.share-page {
  min-height: 100vh;
  background: #F7F5F2;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}
.private-container, .loading-container {
  max-width: 360px;
  margin: 80px auto;
  text-align: center;
  background: #fff;
  border-radius: 16px;
  padding: 48px 32px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.private-icon { font-size: 48px; margin-bottom: 16px; }
.private-title { font-size: 18px; font-weight: 600; margin-bottom: 8px; color: #1F1F1F; }
.private-desc { font-size: 14px; color: #999; }
.profile-wrapper { max-width: 900px; margin: 0 auto; }

.share-header {
  background: #fff;
  border-radius: 12px;
  padding: 20px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.share-header-left { display: flex; align-items: center; gap: 14px; }
.share-avatar {
  width: 52px; height: 52px; border-radius: 50%;
  background: linear-gradient(135deg, #E8D5C0, #C49A6C);
  display: flex; align-items: center; justify-content: center;
  font-size: 26px;
}
.share-nickname { font-size: 18px; font-weight: 700; color: #1F1F1F; }
.share-subtitle { font-size: 13px; color: #999; margin-top: 2px; }
.share-badge {
  font-size: 12px; color: #C49A6C; background: #FDF6EE;
  padding: 4px 12px; border-radius: 12px; border: 1px solid #E8D5C0;
}

.share-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}
.share-stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px 12px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.share-stat-value { font-size: 24px; font-weight: 700; color: #C49A6C; margin-bottom: 4px; }
.share-stat-value.green { color: #7EB8A2; }
.share-stat-label { font-size: 13px; color: #999; }

.share-notice {
  background: #FDF6EE;
  border: 1px solid #E8D5C0;
  border-radius: 10px;
  padding: 14px 16px;
  text-align: center;
  font-size: 14px;
  color: #C49A6C;
  margin-bottom: 20px;
}
.share-notice-icon { margin-right: 6px; }
.share-notice.names-only { background: #E8F5E9; border-color: #C8E6D5; color: #7EB8A2; }

.loading-spinner {
  width: 36px; height: 36px;
  border: 3px solid #EBE8E4;
  border-top-color: #C49A6C;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 12px;
}
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text { font-size: 14px; color: #999; }
</style>
