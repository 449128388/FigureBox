<!--
  SharePoster.vue - 分享海报组件

  功能说明：
  - 选择海报模板（资产概览/藏品陈列/极简数据）
  - 使用 dom-to-image 生成海报图片
  - 支持保存和分享

  使用:
  <SharePoster :visible.sync="visible" :collectorData="data" />
-->
<template>
  <div v-if="visible" class="modal-overlay" @click="close">
    <div class="modal" @click.stop>
      <div class="modal-header">
        <div class="modal-title">📤 分享海报</div>
        <div class="modal-close" @click="close">×</div>
      </div>

      <!-- Step 1: 选择模板 -->
      <div v-if="step === 1" class="modal-body">
        <div style="font-size:14px;color:var(--text-secondary,#666);margin-bottom:14px;">选择海报模板</div>
        <div class="poster-template-grid">
          <div
            v-for="tpl in templates" :key="tpl.key"
            class="poster-template-card"
            :class="{ selected: selectedTemplate === tpl.key }"
            @click="selectedTemplate = tpl.key"
          >
            <div class="poster-template-preview" :style="{ background: tpl.bg }">{{ tpl.icon }}</div>
            <div class="poster-template-name">{{ tpl.name }}</div>
            <div class="poster-template-desc">{{ tpl.desc }}</div>
          </div>
        </div>
        <div class="share-actions">
          <button class="share-btn share-btn-primary" @click="generatePoster">生成海报</button>
        </div>
      </div>

      <!-- Step 2: 预览 -->
      <div v-else class="modal-body">
        <div class="poster-preview-area">
          <div ref="posterCanvas" class="poster-canvas" :class="selectedTemplate">
            <div class="poster-title">我的塑料资产</div>
            <div class="poster-subtitle">以热爱为尺，不以涨跌为度</div>

            <template v-if="selectedTemplate === 'overview'">
              <div class="poster-stats-row">
                <div class="poster-stat-box">
                  <div class="poster-stat-num">{{ showStats ? totalCount : '--' }}</div>
                  <div class="poster-stat-label">藏品</div>
                </div>
                <div class="poster-stat-box">
                  <div class="poster-stat-num">{{ showStats ? soldCount : '--' }}</div>
                  <div class="poster-stat-label">已出</div>
                </div>
              </div>
              <div v-if="showNames" class="poster-figure-list">
                <div style="font-weight:600;margin-bottom:6px;">本月新入柜 +{{ monthNewCount }} 体</div>
                <div v-for="fig in recentFigures" :key="fig" style="font-size:12px;line-height:1.8;">· {{ fig }}</div>
              </div>
              <div v-if="showAmount && totalAsset" class="poster-data-row" style="margin-bottom:12px;">
                总资产价值 <span>¥{{ totalAsset }}</span>
              </div>
            </template>

            <template v-if="selectedTemplate === 'gallery'">
              <div class="poster-title">我的收藏柜</div>
              <div class="poster-subtitle">{{ showStats ? totalCount + ' 体藏品 · 陪伴最长 ' + companionDays + ' 天' : '' }}</div>
              <div class="poster-gallery-grid">
                <div v-for="n in 6" :key="n" class="poster-gallery-item">🧸</div>
              </div>
              <div v-if="showNames && topFigures.length > 0" class="poster-gallery-feature">🧸</div>
              <div v-if="showNames && topFigures.length > 0" style="font-size:14px;font-weight:600;margin-bottom:4px;color:#1F1F1F;">{{ topFigures[0]?.name || '' }}</div>
              <div v-if="showNames && topFigures.length > 0" style="font-size:12px;color:#999;margin-bottom:12px;">陪伴 {{ topFigures[0]?.days || 0 }} 天</div>
            </template>

            <template v-if="selectedTemplate === 'minimal'">
              <div style="margin-top:30px;"></div>
              <div class="poster-big-num">{{ showStats ? totalCount : '--' }}</div>
              <div class="poster-big-label">藏品总数</div>
              <div style="margin-top:30px;">
                <div class="poster-data-row">+{{ monthNewCount }} 体 <span>本月新入柜</span></div>
                <div class="poster-data-row">{{ soldCount }} 体 <span>已出藏品</span></div>
                <div class="poster-data-row">{{ companionDays }} 天 <span>平均陪伴时长</span></div>
                <div v-if="showAmount && totalAsset" class="poster-data-row">¥{{ totalAsset }} <span>总资产价值</span></div>
              </div>
            </template>

            <img v-if="qrDataUrl" :src="qrDataUrl" class="poster-qr" alt="QR Code" />
            <div v-else class="poster-qr">📱</div>
            <div class="poster-qr-text">扫码查看我的收藏</div>
            <div class="poster-footer">—— 手办收藏家 · 我的塑料资产 ——</div>
          </div>
        </div>
        <div class="share-actions">
          <button class="share-btn" @click="saveImage">💾 保存图片</button>
          <button class="share-btn" @click="copyLink">🔗 复制链接</button>
        </div>
        <div style="text-align:center;margin-top:10px;">
          <button class="share-btn" style="width:auto;padding:6px 16px;" @click="step = 1">← 重新选择模板</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import QRCode from 'qrcode'
import axios from '@/axios'

export default {
  name: 'SharePoster',
  props: {
    visible: Boolean,
    collectorData: { type: Object, default: () => ({}) }
  },
  emits: ['update:visible'],
  setup(props, { emit }) {
    const step = ref(1)
    const selectedTemplate = ref('overview')
    const posterCanvas = ref(null)
    const shareUrl = ref('')
    const qrDataUrl = ref('')
    const generatingShare = ref(false)

    const templates = [
      { key: 'overview', name: '资产概览', desc: '统计数据为主', icon: '📊', bg: 'linear-gradient(135deg,#FDF6EE,#fff)' },
      { key: 'gallery', name: '藏品陈列', desc: '手办拼图展示', icon: '🖼️', bg: 'linear-gradient(135deg,#E8F5E9,#fff)' },
      { key: 'minimal', name: '极简数据', desc: '大数字极简风', icon: '✨', bg: 'linear-gradient(135deg,#F3E5F5,#fff)' }
    ]

    const totalCount = computed(() => props.collectorData?.summary?.total_collection || 0)
    const soldCount = computed(() => props.collectorData?.summary?.total_sold_count || 0)
    const monthNewCount = computed(() => props.collectorData?.summary?.this_month_count || 0)
    const companionDays = computed(() => props.collectorData?.summary?.total_companion_days || 0)
    const totalAsset = computed(() => {
      return props.collectorData?.summary?.total_asset_value || 0
    })
    const recentFigures = computed(() => {
      const text = props.collectorData?.summary?.recent_figures || ''
      return text.split(' / ').filter(Boolean)
    })
    const topFigures = computed(() => {
      const cabinets = props.collectorData?.cabinets || []
      const items = []
      for (const cab of cabinets) {
        if (cab.items && cab.items.length > 0) {
          cab.items.slice(0, 3).forEach(fig => {
            if (!items.find(i => i.id === fig.id)) {
              items.push({ id: fig.id, name: fig.name, days: fig.holding_days })
            }
          })
        }
      }
      return items.slice(0, 6)
    })

    // 隐私设置控制
    const privacy = computed(() => props.collectorData?.privacy || {})
    const showStats = computed(() => privacy.value.show_total !== false)
    const showNames = computed(() => (privacy.value.poster_level || 'stats_only') !== 'stats_only')
    const showAmount = computed(() =>
      (privacy.value.poster_level || 'stats_only') === 'full' && privacy.value.show_asset !== false
    )

    watch(() => props.visible, (v) => {
      if (v) {
        step.value = 1
        qrDataUrl.value = ''
        shareUrl.value = ''
      }
    })

    /** 生成分享链接和二维码 */
    async function genShareLinkAndQR() {
      if (generatingShare.value) return
      generatingShare.value = true
      try {
        const res = await axios.post('/collector/share/generate')
        const url = res.share_url
        shareUrl.value = url
        // 生成二维码 data URL
        qrDataUrl.value = await QRCode.toDataURL(url, {
          width: 400,
          margin: 4,
          color: { dark: '#1F1F1F', light: '#FFFFFF' }
        })
      } catch (e) {
        ElMessage.error('生成分享链接失败')
        qrDataUrl.value = ''
      } finally {
        generatingShare.value = false
      }
    }

    function close() {
      emit('update:visible', false)
      step.value = 1
    }

    function generatePoster() {
      // 生成海报前先获取分享链接
      genShareLinkAndQR()
      step.value = 2
    }

    async function saveImage() {
      if (!posterCanvas.value) return
      try {
        const domtoimage = (await import('dom-to-image')).default
        const scale = 3
        // 1. 先输出 SVG（无损矢量）
        const svgDataUrl = await domtoimage.toSvg(posterCanvas.value)
        // 2. 用 Image 对象加载 SVG，再绘制到高分辨率 Canvas 上
        const img = new Image()
        await new Promise((resolve, reject) => {
          img.onload = resolve
          img.onerror = reject
          img.src = svgDataUrl
        })
        const canvas = document.createElement('canvas')
        canvas.width = img.naturalWidth * scale
        canvas.height = img.naturalHeight * scale
        const ctx = canvas.getContext('2d')
        ctx.imageSmoothingEnabled = false
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
        const dataUrl = canvas.toDataURL('image/png')
        const link = document.createElement('a')
        link.download = `我的塑料资产-${Date.now()}.png`
        link.href = dataUrl
        link.click()
        ElMessage.success('海报已保存')
      } catch (e) {
        ElMessage.error('保存失败: ' + e.message)
      }
    }

    function copyLink() {
      if (shareUrl.value) {
        navigator.clipboard.writeText(shareUrl.value).then(() => {
          ElMessage.success('分享链接已复制')
        }).catch(() => {
          ElMessage.success('分享链接: ' + shareUrl.value)
        })
      } else {
        const text = `我的塑料资产 - 藏品${totalCount.value}体，已出${soldCount.value}体`
        navigator.clipboard.writeText(text).catch(() => {})
        ElMessage.success('文本已复制: ' + text)
      }
    }

    return {
      step, selectedTemplate, posterCanvas, templates, qrDataUrl, generatingShare,
      totalCount, soldCount, monthNewCount, companionDays, totalAsset,
      recentFigures, topFigures,
      showStats, showNames, showAmount,
      close, generatePoster, saveImage, copyLink
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5); z-index: 200;
  display: flex; align-items: center; justify-content: center;
  backdrop-filter: blur(4px); padding: 20px;
}
.modal {
  background: #fff; border-radius: 12px; width: 100%; max-width: 640px;
  max-height: 92vh; overflow-y: auto;
  scrollbar-width: none;
  box-shadow: 0 8px 32px rgba(0,0,0,0.12);
  animation: modalIn 0.3s ease;
}
.modal::-webkit-scrollbar { display: none; }
@keyframes modalIn {
  from { opacity: 0; transform: translateY(20px) scale(0.96); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
.modal-header {
  padding: 16px 20px; border-bottom: 1px solid #EBE8E4;
  display: flex; align-items: center; justify-content: space-between;
  position: sticky; top: 0; background: #fff; z-index: 1;
}
.modal-title { font-size: 16px; font-weight: 600; }
.modal-close {
  width: 28px; height: 28px; border-radius: 50%; border: 1px solid #EBE8E4;
  background: #fff; display: flex; align-items: center; justify-content: center;
  cursor: pointer; font-size: 16px; color: #999; transition: all 0.2s;
}
.modal-close:hover { border-color: #D66A6A; color: #D66A6A; }
.modal-body { padding: 20px; }

.poster-template-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 20px;
}
.poster-template-card {
  border: 2px solid #EBE8E4; border-radius: 10px; padding: 12px;
  cursor: pointer; transition: all 0.2s; text-align: center;
  background: #FAFAFA;
}
.poster-template-card:hover { border-color: #E8D5C0; }
.poster-template-card.selected { border-color: #C49A6C; background: #FDF6EE; }
.poster-template-preview {
  height: 80px; border-radius: 6px; margin-bottom: 8px;
  display: flex; align-items: center; justify-content: center; font-size: 24px;
}
.poster-template-name { font-size: 13px; font-weight: 500; }
.poster-template-desc { font-size: 11px; color: #999; margin-top: 2px; }

.poster-preview-area {
  background: #F5F5F5; border-radius: 10px; padding: 28px; margin-bottom: 20px;
  display: flex; justify-content: center;
}
.poster-canvas {
  width: 320px; min-height: 480px; background: #fff; border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1); padding: 28px;
  display: flex; flex-direction: column; align-items: center; text-align: center;
  position: relative; overflow: hidden;
}
.poster-canvas.overview {
  background: linear-gradient(180deg, #FDF6EE 0%, #fff 60%);
}
.poster-canvas.gallery {
  background: linear-gradient(180deg, #E8F5E9 0%, #fff 60%);
}
.poster-canvas.minimal {
  background: linear-gradient(180deg, #F3E5F5 0%, #fff 60%);
}
.poster-title { font-size: 22px; font-weight: 700; margin-bottom: 4px; color: #1F1F1F; }
.poster-subtitle { font-size: 13px; color: #999; margin-bottom: 24px; }
.poster-stats-row { display: flex; gap: 16px; margin-bottom: 20px; }
.poster-stat-box {
  background: rgba(255,255,255,0.8); border-radius: 10px; padding: 12px 16px;
  border: 1px solid #EBE8E4; min-width: 80px;
}
.poster-stat-num { font-size: 22px; font-weight: 700; color: #C49A6C; }
.poster-stat-label { font-size: 11px; color: #999; margin-top: 2px; }
.poster-figure-list {
  font-size: 12px; color: #666; line-height: 1.8; margin-bottom: 16px;
  text-align: left; width: 100%;
}
.poster-qr {
  width: 180px; height: 180px; border-radius: 8px;
  margin-bottom: 12px;
  object-fit: contain;
}
.poster-qr-text { font-size: 12px; color: #999; }
.poster-footer { font-size: 11px; color: #999; margin-top: auto; padding-top: 16px; }
.poster-big-num { font-size: 48px; font-weight: 700; color: #C49A6C; margin: 20px 0; }
.poster-big-label { font-size: 14px; color: #666; }
.poster-data-row { font-size: 14px; color: #666; margin: 8px 0; }
.poster-data-row span { font-weight: 600; color: #1F1F1F; }

.poster-gallery-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin-bottom: 16px; width: 100%;
}
.poster-gallery-item {
  aspect-ratio: 1; background: #F0EEEB; border-radius: 6px;
  display: flex; align-items: center; justify-content: center; font-size: 20px;
}
.poster-gallery-feature {
  width: 100%; height: 100px; background: #F0EEEB; border-radius: 8px;
  display: flex; align-items: center; justify-content: center; font-size: 40px; margin-bottom: 8px;
}

.share-actions { display: flex; gap: 10px; margin-bottom: 16px; }
.share-btn {
  flex: 1; padding: 10px 0; text-align: center; border: 1px solid #EBE8E4;
  background: #fff; border-radius: 8px; font-size: 13px; color: #666;
  cursor: pointer; transition: all 0.2s;
}
.share-btn:hover { border-color: #C49A6C; color: #C49A6C; background: #FDF6EE; }
.share-btn-primary {
  background: #C49A6C; border-color: #C49A6C; color: #fff;
}
.share-btn-primary:hover { background: #B08A5C; border-color: #B08A5C; color: #fff; }
</style>
