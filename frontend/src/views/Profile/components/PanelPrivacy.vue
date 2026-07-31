<!--
  PanelPrivacy.vue - 隐私设置面板
  props: active / privacySettings / homeVisibilityText
  emits: show-home-visibility（弹窗）/ toggle-privacy（key）
-->
<template>
  <div class="panel" :class="{ active: active }">
    <div class="panel-header">隐私设置</div>
    <div class="panel-body" style="padding: 20px 28px 28px;">
      <div class="privacy-section">
        <div class="privacy-section-title">访问权限</div>
        <div class="privacy-item" @click="$emit('show-home-visibility')">
          <div class="privacy-item-info">
            <div class="privacy-item-title">个人主页可见性</div>
            <div class="privacy-item-desc">控制谁可以访问你的收藏主页</div>
          </div>
          <div class="privacy-link">
            {{ homeVisibilityText }}
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
          </div>
        </div>
      </div>
      <div class="privacy-section">
        <div class="privacy-section-title">数据展示</div>
        <div class="privacy-item" @click="$emit('toggle-privacy', 'show_total')">
          <div class="privacy-item-info">
            <div class="privacy-item-title">藏品总数</div>
            <div class="privacy-item-desc">是否对外展示藏品统计数量</div>
          </div>
          <div class="toggle-v2" :class="{ active: privacySettings.show_total }"></div>
        </div>
        <div class="privacy-item" @click="$emit('toggle-privacy', 'show_figures')">
          <div class="privacy-item-info">
            <div class="privacy-item-title">具体藏品列表</div>
            <div class="privacy-item-desc">是否展示手办明细信息</div>
          </div>
          <div class="toggle-v2" :class="{ active: privacySettings.show_figures }"></div>
        </div>
        <div class="privacy-item" @click="$emit('toggle-privacy', 'show_tags')">
          <div class="privacy-item-info">
            <div class="privacy-item-title">标签云</div>
            <div class="privacy-item-desc">是否展示手办标签偏好信息</div>
          </div>
          <div class="toggle-v2" :class="{ active: privacySettings.show_tags }"></div>
        </div>
        <div class="privacy-item" @click="$emit('toggle-privacy', 'show_feed')">
          <div class="privacy-item-info">
            <div class="privacy-item-title">动态流</div>
            <div class="privacy-item-desc">买入卖出等操作记录是否对外展示</div>
          </div>
          <div class="toggle-v2" :class="{ active: privacySettings.show_feed }"></div>
        </div>
        <div class="privacy-item" @click="$emit('toggle-privacy', 'show_asset')">
          <div class="privacy-item-info">
            <div class="privacy-item-title">主页资产金额</div>
            <div class="privacy-item-desc">包含成本价、市值、盈亏等敏感数据</div>
          </div>
          <div class="toggle-v2" :class="{ active: privacySettings.show_asset }"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PanelPrivacy',
  props: {
    active: { type: Boolean, default: false },
    privacySettings: { type: Object, required: true },
    homeVisibilityText: { type: String, default: '公开' }
  },
  emits: ['show-home-visibility', 'toggle-privacy']
}
</script>

<style scoped>
.panel { background: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); overflow: hidden; display: none; }
.panel.active { display: block; animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
.panel-header { padding: 20px 24px; border-bottom: 1px solid #e3e5e7; font-size: 18px; font-weight: 700; color: #18191c; }
.panel-body { padding: 24px 32px 32px; }

.privacy-section { margin-bottom: 28px; }
.privacy-section:last-child { margin-bottom: 0; }
.privacy-section-title {
  font-size: 14px; font-weight: 600; color: #18191c; margin-bottom: 8px;
  display: flex; align-items: center; gap: 6px; padding-left: 8px;
}
.privacy-section-title::before {
  content: ""; display: inline-block; width: 3px; height: 14px;
  background: #c9a96e; border-radius: 2px;
}
.privacy-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 8px; border-bottom: 1px solid #f0f0f0;
  cursor: pointer; transition: background 0.15s; border-radius: 6px;
}
.privacy-item:hover { background: #fafafa; }
.privacy-item:last-child { border-bottom: none; }
.privacy-item-info { display: flex; flex-direction: column; gap: 4px; }
.privacy-item-title { font-size: 15px; font-weight: 500; color: #18191c; }
.privacy-item-desc { font-size: 12px; color: #9499a0; }

.toggle-v2 {
  position: relative; width: 44px; height: 24px; background: #d8d8d8;
  border-radius: 12px; cursor: pointer; transition: background 0.3s;
  flex-shrink: 0; -webkit-tap-highlight-color: transparent;
}
.toggle-v2::after {
  content: ""; position: absolute; top: 2px; left: 2px;
  width: 20px; height: 20px; background: #fff; border-radius: 50%;
  transition: transform 0.3s; box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}
.toggle-v2.active { background: #c9a96e; }
.toggle-v2.active::after { transform: translateX(20px); }

.privacy-link {
  display: flex; align-items: center; gap: 4px; font-size: 14px;
  color: #9499a0; transition: color 0.2s;
}
.privacy-item:hover .privacy-link { color: #61666d; }
.privacy-link svg { width: 14px; height: 14px; }
</style>
