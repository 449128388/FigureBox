<!--
  FigureBasicInfo.vue - 藏品基本信息子组件

  Props:
  - figure: Object - 藏品数据
  - cabinetName: String - 收藏柜名称
  - statusLabel: String - 状态标签文本
  - statusColor: String - 状态颜色
-->
<template>
  <div class="section">
    <div class="section-title">基本信息</div>
    <div class="info-grid">
      <div class="info-item">
        <div class="info-label">当前库存</div>
        <div class="info-value">{{ figure.stock || 0 }} 体</div>
        <div class="info-value-sub" v-if="figure.avg_cost">加权平均成本: ¥{{ figure.avg_cost }}/体</div>
      </div>
      <div class="info-item">
        <div class="info-label">作品/IP</div>
        <div class="info-value">{{ figure.work || '未知' }}</div>
      </div>
      <div class="info-item">
        <div class="info-label">当前状态</div>
        <div class="info-value">
          <span
            v-for="(st, idx) in statusesList"
            :key="idx"
            class="status-badge"
            :style="{ color: st.cls === 'st-in' ? '#7EB8A2' : st.cls === 'st-air' ? '#9B7ED8' : st.cls === 'st-air-paid' ? '#4A90D9' : st.cls === 'st-fix' ? '#E6A23C' : '#999' }"
          >{{ st.text }}<template v-if="idx < statusesList.length - 1">、</template></span>
        </div>
      </div>
      <div class="info-item">
        <div class="info-label">收藏柜分类</div>
        <div class="info-value">{{ cabinetName }}</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FigureBasicInfo',

  props: {
    figure: {
      type: Object,
      required: true
    },
    cabinetName: {
      type: String,
      default: ''
    },
    statusLabel: {
      type: String,
      default: '✅ 在柜 · 完好'
    },
    statusColor: {
      type: String,
      default: '#7EB8A2'
    },
    statusesList: {
      type: Array,
      default: () => []
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

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.info-item {
  background: #FAFAFA;
  border-radius: 8px;
  padding: 12px 14px;
  border: 1px solid #EBE8E4;
}

.info-label {
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
}

.info-value {
  font-size: 14px;
  font-weight: 600;
  color: #1F1F1F;
}

.info-value-sub {
  font-size: 12px;
  color: #666;
  margin-top: 2px;
}
</style>
