<!--
  ShareProfile.vue - 收藏家分享主页（无需登录，复用收藏家组件）

  数据展示规则（纯由「数据展示」开关驱动，与「海报展示数据」无关）：
  - show_total → 展示 CollectorOverview（统计数据）
  - show_figures → 展示 CollectionCabinets（收藏柜）
  - show_tags → 展示 TagCloud（标签云）
  - show_feed → 展示 ActivityFeed（动态流）
  - 全部关闭 → 提示未公开
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
      <div class="profile-hero">
        <div class="profile-left">
          <div class="avatar">
            <img v-if="profileData.avatar_url" :src="profileData.avatar_url" class="avatar-img" />
            <span v-else>🧸</span>
          </div>
          <div class="profile-info">
            <div class="profile-title">{{ profileData.nickname }} 的塑料资产</div>
            <div class="profile-sub">藏品陈列室 · 以热爱为尺，不以涨跌为度</div>
          </div>
        </div>
        <div v-if="profileData.from_poster" class="share-badge">📸 来自海报</div>
      </div>

      <!-- 按「数据展示」各开关独立控制对应模块 -->
      <CollectorOverview v-if="profileData.show_total" :collector-data="profileData" />
      <CollectionCabinets v-if="profileData.show_figures" :collector-data="profileData" />
      <TagCloud v-if="profileData.show_tags" :collector-data="profileData" />
      <ActivityFeed v-if="profileData.show_feed" :collector-data="profileData" />

      <!-- 所有数据展示开关均关闭时提示 -->
      <div v-if="!profileData.show_total && !profileData.show_figures && !profileData.show_tags && !profileData.show_feed" class="share-notice">
        <span class="share-notice-icon">🔒</span> 该用户未公开任何数据
      </div>
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
          tags: [],
          system_tags: [],
          user_tags: [],
          activities: []
        }

        for (let i = 0; i < results.length; i++) {
          const key = promiseMap[i].key
          if (key === 'summary') merged.summary = results[i] || {}
          else if (key === 'cabinets') merged.cabinets = results[i] || []
          else if (key === 'tags') {
            const t = results[i] || {}
            merged.tags = t.tags || []
            merged.system_tags = t.system_tags || []
            merged.user_tags = t.user_tags || []
          }
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
.profile-wrapper { max-width: 1200px; margin: 0 auto; }

.profile-hero {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.profile-left { display: flex; align-items: center; gap: 16px; }
.avatar {
  width: 56px; height: 56px; border-radius: 50%;
  background: linear-gradient(135deg, #E8D5C0, #C49A6C);
  display: flex; align-items: center; justify-content: center;
  font-size: 24px; color: #fff; flex-shrink: 0; overflow: hidden;
}
.avatar-img {
  width: 100%; height: 100%; object-fit: cover;
}
.profile-info { display: flex; flex-direction: column; gap: 2px; }
.profile-title { font-size: 20px; font-weight: 600; color: #1F1F1F; }
.profile-sub { font-size: 13px; color: #999; }

.share-badge {
  font-size: 12px; color: #C49A6C; background: #FDF6EE;
  padding: 4px 12px; border-radius: 12px; border: 1px solid #E8D5C0;
}

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
