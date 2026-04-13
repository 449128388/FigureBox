<template>
  <div class="research-section">
    <div class="section-title">💡 智能投研</div>
    <div class="research-card">
      <div class="research-item">
        <div class="research-label">评级:</div>
        <div class="research-value">{{ marketData?.research?.rating || 'GSC 初音韶华 买入' }}</div>
      </div>
      <div class="research-item">
        <div class="research-label">机构:</div>
        <div class="research-value">{{ marketData?.research?.institution || 'Hpoi研究院' }}</div>
      </div>
      <div class="research-item">
        <div class="research-label">目标价:</div>
        <div class="research-value">{{ marketData?.research?.target_price || '¥2,800 (+40%)' }}</div>
      </div>
      <div class="research-item">
        <div class="research-label">止损价:</div>
        <div class="research-value">{{ marketData?.research?.stop_loss || '¥1,600 (-20%)' }}</div>
      </div>
      <div class="research-item">
        <div class="research-label">推荐理由:</div>
        <div class="research-value">{{ marketData?.research?.reason || '再版停产公告+海景房属性+即将出荷' }}</div>
      </div>
      <div class="research-item">
        <div class="research-label">发布日期:</div>
        <div class="research-value">{{ marketData?.research?.date || '2026-04-01' }}</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ResearchSection',
  props: {
    marketData: {
      type: Object,
      default: () => ({})
    }
  }
}
</script>

<style scoped>
/* 投研观点 */
.research-section {
  margin-bottom: 30px;
}

.research-card {
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 20px;
}

.research-item {
  display: flex;
  margin-bottom: 15px;
  align-items: flex-start;
}

.research-label {
  width: 100px;
  font-size: 14px;
  font-weight: 600;
  color: #666;
}

.research-value {
  flex: 1;
  font-size: 14px;
  color: #333;
  line-height: 1.5;
}

.research-date {
  font-size: 12px;
  color: #999;
  text-align: right;
}

@media (max-width: 768px) {
  .research-targets {
    flex-direction: column;
    gap: 10px;
  }
}
</style>