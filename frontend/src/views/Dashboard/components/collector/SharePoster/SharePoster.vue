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
          <div ref="posterCanvas" class="poster-canvas" :class="'poster-' + selectedTemplate">

            <!-- ========== 资产概览海报 ========== -->
            <template v-if="selectedTemplate === 'overview'">
              <div class="overview-top">
                <div class="overview-badge">PLASTIC ASSETS</div>
                <div class="overview-title">我的塑料资产</div>
                <div class="overview-subtitle">以热爱为尺，不以涨跌为度</div>
                <div class="overview-stats">
                  <div class="overview-stat-item">
                    <div class="overview-stat-num">{{ totalCount }}</div>
                    <div class="overview-stat-label">藏品</div>
                  </div>
                  <div class="overview-stat-item">
                    <div class="overview-stat-num">+{{ monthNewCount }}</div>
                    <div class="overview-stat-label">本月</div>
                  </div>
                  <div class="overview-stat-item">
                    <div class="overview-stat-num">{{ soldCount }}</div>
                    <div class="overview-stat-label">已出</div>
                  </div>
                </div>
              </div>
              <div class="overview-body">
                <!-- 收藏柜分类（始终显示） -->
                <div class="overview-section-title">我的收藏柜</div>
                <div class="overview-cabinet-grid">
                  <div v-for="cab in posterCabinets" :key="cab.key" class="overview-cabinet-item">
                    <div class="overview-cabinet-icon">{{ cab.icon }}</div>
                    <div class="overview-cabinet-name">{{ cab.name }}</div>
                    <div class="overview-cabinet-count">{{ cab.count }}体</div>
                  </div>
                </div>

                <!-- 精选藏品（full/names_only 展示，stats_only 隐藏） -->
                <template v-if="posterLevel !== 'stats_only' && posterFigureList.length > 0">
                  <div class="overview-section-title">精选藏品</div>
                  <div class="overview-figure-list">
                    <div v-for="fig in posterFigureList" :key="fig.name" class="overview-figure-item">
                      <div class="overview-figure-thumb">
                        <img v-if="fig.image" :src="fig.image" :alt="fig.name" class="overview-figure-img" />
                        <span v-else>🧸</span>
                      </div>
                      <div class="overview-figure-name">{{ fig.name }}</div>
                      <div v-if="posterLevel === 'full'" class="overview-figure-price">¥{{ formatPrice(fig.price) }}</div>
                    </div>
                  </div>
                </template>

                <!-- 标签云（full / names_only 显示，stats_only 隐藏） -->
                <template v-if="posterLevel !== 'stats_only' && posterTags.length > 0">
                  <div class="overview-section-title">标签云</div>
                  <div class="overview-tag-row">
                    <span v-for="t in posterTags" :key="t.name" class="overview-tag">#{{ t.name }}({{ t.count }})</span>
                  </div>
                </template>

                <!-- 总资产（仅 full 显示） -->
                <template v-if="posterLevel === 'full'">
                  <div class="overview-section-title">资产概览</div>
                  <div class="overview-asset-row">
                    <span class="overview-asset-label">总资产价值</span>
                    <span class="overview-asset-value">¥{{ formatPrice(totalAsset) }}</span>
                  </div>
                </template>
              </div>
              <div class="overview-bottom">
                <img v-if="qrDataUrl" :src="qrDataUrl" class="poster-qr-img" alt="QR Code" />
                <div v-else class="overview-qr-placeholder">📱</div>
                <div class="overview-qr-text">扫码查看我的收藏</div>
                <div class="overview-footer">—— 手办收藏家 · 我的塑料资产 ——</div>
              </div>
            </template>

            <!-- ========== 藏品陈列海报 ========== -->
            <template v-if="selectedTemplate === 'gallery'">
              <div class="gallery-top">
                <div class="gallery-title">我的收藏柜</div>
                <div class="gallery-subtitle">{{ totalCount }} 体藏品 · {{ activeCabinetCount }} 个分类</div>
                <div class="gallery-grid">
                  <div v-for="(fig, idx) in galleryFigureItems" :key="idx" class="gallery-item" :class="{ 'gallery-item-featured': idx === 0 }">
                    <img v-if="fig.image" :src="fig.image" :alt="fig.name" class="gallery-item-img" />
                    <div v-else class="gallery-item-icon">🧸</div>
                    <div v-if="idx === 0 && posterLevel !== 'stats_only'" class="gallery-item-badge">NEW</div>
                  </div>
                </div>
              </div>
              <div class="gallery-body">
                <!-- 主藏品信息（仅 full / names_only 显示） -->
                <template v-if="posterLevel !== 'stats_only' && galleryFigureItems.length > 0">
                  <div class="gallery-feature-info">
                    <div class="gallery-feature-name">{{ galleryFigureItems[0].name }}</div>
                    <div class="gallery-feature-desc">{{ galleryFigureItems[0].spec || '' }}</div>
                    <div v-if="posterLevel === 'full'" class="gallery-feature-price">¥{{ formatPrice(galleryFigureItems[0].price) }}</div>
                  </div>
                </template>
                <!-- 底部统计 -->
                <div class="gallery-stats-bar">
                  <div class="gallery-stat-item">
                    <div class="gallery-stat-num">{{ totalCount }}</div>
                    <div class="gallery-stat-label">藏品</div>
                  </div>
                  <div class="gallery-stat-item">
                    <div class="gallery-stat-num">+{{ monthNewCount }}</div>
                    <div class="gallery-stat-label">本月</div>
                  </div>
                  <div class="gallery-stat-item">
                    <div class="gallery-stat-num">{{ companionDays }}</div>
                    <div class="gallery-stat-label">陪伴天</div>
                  </div>
                </div>
              </div>
              <div class="gallery-bottom">
                <img v-if="qrDataUrl" :src="qrDataUrl" class="poster-qr-img" alt="QR Code" />
                <div v-else class="overview-qr-placeholder">📱</div>
                <div class="overview-qr-text">扫码查看我的收藏</div>
                <div class="overview-footer">—— 手办收藏家 · 我的塑料资产 ——</div>
              </div>
            </template>

            <!-- ========== 极简数据海报 ========== -->
            <template v-if="selectedTemplate === 'minimal'">
              <div class="minimal-badge">PLASTIC ASSETS</div>
              <div class="minimal-title">我的塑料资产</div>
              <div class="minimal-big-num">{{ totalCount }}</div>
              <div class="minimal-big-label">藏品总数</div>
              <div class="minimal-data-list">
                <div class="minimal-data-item">
                  <span class="minimal-data-label">本月新入柜</span>
                  <span class="minimal-data-value accent">+{{ monthNewCount }} 体</span>
                </div>
                <div class="minimal-data-item">
                  <span class="minimal-data-label">已出藏品</span>
                  <span class="minimal-data-value">{{ soldCount }} 体</span>
                </div>
                <div class="minimal-data-item">
                  <span class="minimal-data-label">平均陪伴</span>
                  <span class="minimal-data-value">{{ companionDays }} 天</span>
                </div>
                <!-- 总资产 + 收益率（仅 full 显示） -->
                <template v-if="posterLevel === 'full'">
                  <div class="minimal-data-item">
                    <span class="minimal-data-label">总资产</span>
                    <span class="minimal-data-value accent">¥{{ formatPrice(totalAsset) }}</span>
                  </div>
                  <div class="minimal-data-item">
                    <span class="minimal-data-label">收益率</span>
                    <span :class="['minimal-data-value', posterProfitRate.startsWith('+') ? 'red' : 'green']">{{ posterProfitRate }}</span>
                  </div>
                </template>
              </div>
              <!-- 藏品名称（仅 stats_only 不显示） -->
              <div v-if="posterLevel !== 'stats_only'" class="minimal-figure-names">
                {{ posterFigureNames }}
              </div>
              <img v-if="qrDataUrl" :src="qrDataUrl" class="minimal-qr" alt="QR Code" />
              <div v-else class="minimal-qr-placeholder">📱</div>
              <div class="minimal-qr-text">扫码查看我的收藏</div>
              <div class="minimal-footer">—— 手办收藏家 · 我的塑料资产 ——</div>
            </template>

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
      { key: 'overview', name: '资产概览', desc: '统计+分类+列表', icon: '📊', bg: 'linear-gradient(135deg,#FDF6EE,#fff)' },
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
    const uniqueWorks = computed(() => props.collectorData?.summary?.unique_works || 0)
    const uniqueManufacturers = computed(() => props.collectorData?.summary?.unique_manufacturers || 0)
    const recentFiguresText = computed(() => props.collectorData?.summary?.recent_figures || '暂无新入库')
    const companionDaysFormatted = computed(() => {
      const days = companionDays.value
      if (!days || days <= 0) return '0 天'
      return `${Number(days).toLocaleString()} 天`
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

    // 海报数据控制（纯由「海报展示数据」驱动，与「数据展示」独立）
    const posterLevel = computed(() => props.collectorData?.privacy?.poster_level || 'full')

    /** 格式化价格 */
    function formatPrice(val) {
      if (val === undefined || val === null || val === 0) return '0'
      return Number(val).toLocaleString()
    }

    // 收藏柜列表（8个）
    const posterCabinets = computed(() => {
      return props.collectorData?.cabinets || []
    })

    // 用于概览海报的藏品列表
    const posterFigureList = computed(() => {
      // 第一优先级：从 summary.recent_figures_detail 获取（后端结构化数据，含名称+价格+图片）
      const detail = props.collectorData?.summary?.recent_figures_detail
      if (detail && detail.length > 0) {
        return detail.slice(0, 6).map(fig => ({
          id: fig.name,
          name: fig.name,
          price: fig.price || 0,
          image: fig.image || '',
          spec: fig.spec || ''
        }))
      }
      // 第二优先级：从 cabinet.items 收集
      const cabinets = props.collectorData?.cabinets || []
      const items = []
      const seen = new Set()
      for (const cab of cabinets) {
        if (cab.items && cab.items.length > 0) {
          for (const fig of cab.items) {
            if (!seen.has(fig.id || fig.name)) {
              seen.add(fig.id || fig.name)
              items.push({
                id: fig.id,
                name: fig.name,
                price: fig.price || 0,
                image: fig.image || '',
                spec: fig.spec || ''
              })
            }
          }
        }
      }
      // 第三优先级：从 summary.recent_figures 文本提取名称
      if (items.length === 0) {
        const names = (props.collectorData?.summary?.recent_figures || '')
          .split(' / ')
          .map(s => s.trim())
          .filter(Boolean)
        names.forEach(name => {
          if (!seen.has(name)) {
            seen.add(name)
            items.push({ id: name, name, price: 0, image: '', spec: '' })
          }
        })
      }
      return items.slice(0, 6)
    })

    // 用于概览海报的标签云
    const posterTags = computed(() => {
      const tags = props.collectorData?.tags || []
      // 确保无论如何都展示标签数据（不按 count 过滤）
      if (tags.length > 0) return tags
      // 降级：从 system_tags / user_tags 合并
      const sys = props.collectorData?.system_tags || []
      const user = props.collectorData?.user_tags || []
      const merged = [...sys, ...user]
      if (merged.length > 0) return merged
      // 无数据时返回空
      return []
    })

    // 藏品陈列海报的拼图项（第1项为主藏品，不补齐占位）
    const galleryFigureItems = computed(() => {
      const list = posterFigureList.value
      if (list.length === 0) {
        return []
      }
      const result = []
      // 主藏品
      result.push(list[0])
      // 其余藏品
      for (let i = 1; i < list.length; i++) {
        result.push(list[i])
      }
      return result
    })

    // 有藏品的分类数
    const activeCabinetCount = computed(() => {
      const cabinets = props.collectorData?.cabinets || []
      return cabinets.filter(c => c.count > 0).length
    })

    // 极简海报的藏品名称串
    const posterFigureNames = computed(() => {
      const list = posterFigureList.value
      if (list.length === 0) return '暂无藏品数据'
      return list.map(f => f.name).join(' · ')
    })

    // 收益率（从 summary 获取）
    const posterProfitRate = computed(() => {
      const rate = props.collectorData?.summary?.profit_rate
      if (rate !== undefined && rate !== null && rate !== '') return rate
      return '+0.0%'
    })

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
          width: 600,
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
      recentFigures, uniqueWorks, uniqueManufacturers, recentFiguresText, companionDaysFormatted, topFigures,
      posterLevel, formatPrice,
      posterCabinets, posterFigureList, posterTags, galleryFigureItems, activeCabinetCount,
      posterFigureNames, posterProfitRate,
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

.poster-title { font-size: 22px; font-weight: 700; margin-bottom: 4px; color: #1F1F1F; }
.poster-subtitle { font-size: 13px; color: #999; margin-bottom: 24px; }

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

/* ===== Poster Preview Area ===== */
.poster-preview-area {
  background: #E8E5E0; border-radius: 16px; padding: 20px;
  display: flex; justify-content: center; margin-bottom: 20px;
}
.poster-canvas {
  width: 320px; min-height: 480px; background: #fff; border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.12); overflow: hidden;
  display: flex; flex-direction: column; position: relative;
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
}

/* ===== Poster: Overview (资产概览) ===== */
.poster-overview .overview-top {
  background: linear-gradient(135deg, #FAF6F1 0%, #FDF6EE 50%, #FFF9F2 100%);
  padding: 24px 20px 20px; text-align: center; border-bottom: 1px solid #EBE8E4;
}
.poster-overview .overview-badge {
  display: inline-block; font-size: 10px; padding: 2px 8px; border-radius: 10px;
  background: #FDF6EE; color: #C49A6C; border: 1px solid #E8D5C0;
  margin-bottom: 8px; letter-spacing: 1px;
}
.poster-overview .overview-title { font-size: 20px; font-weight: 700; color: #1F1F1F; margin-bottom: 4px; }
.poster-overview .overview-subtitle { font-size: 11px; color: #999; }
.poster-overview .overview-stats {
  display: flex; justify-content: center; gap: 16px; margin-top: 16px;
}
.poster-overview .overview-stat-item {
  background: rgba(255,255,255,0.7); border-radius: 10px; padding: 10px 14px;
  border: 1px solid #E8D5C0; text-align: center; min-width: 70px;
}
.poster-overview .overview-stat-num { font-size: 22px; font-weight: 700; color: #C49A6C; }
.poster-overview .overview-stat-label { font-size: 10px; color: #999; margin-top: 2px; }
.poster-overview .overview-body { padding: 16px 20px; flex: 1; }
.poster-overview .overview-section-title {
  font-size: 12px; font-weight: 600; color: #666; margin-bottom: 10px;
  display: flex; align-items: center; gap: 4px;
}
.poster-overview .overview-section-title::before {
  content: ""; display: inline-block; width: 3px; height: 12px; background: #C49A6C; border-radius: 2px;
}
.poster-overview .overview-cabinet-grid {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; margin-bottom: 14px;
}
.poster-overview .overview-cabinet-item {
  background: #FAFAFA; border-radius: 8px; padding: 8px 4px; text-align: center; border: 1px solid #EBE8E4;
}
.poster-overview .overview-cabinet-icon { font-size: 16px; margin-bottom: 2px; }
.poster-overview .overview-cabinet-name { font-size: 9px; color: #666; }
.poster-overview .overview-cabinet-count { font-size: 9px; color: #999; }
.poster-overview .overview-figure-list { margin-bottom: 14px; }
.poster-overview .overview-figure-item {
  display: flex; align-items: center; gap: 8px; padding: 6px 0; border-bottom: 1px solid #F0F0F0;
  font-size: 11px; color: #666;
}
.poster-overview .overview-figure-item:last-child { border-bottom: none; }
.poster-overview .overview-figure-thumb {
  width: 28px; height: 28px; background: #F0EEEB; border-radius: 6px;
  display: flex; align-items: center; justify-content: center; font-size: 14px; flex-shrink: 0; overflow: hidden;
}
.poster-overview .overview-figure-img {
  width: 100%; height: 100%; object-fit: cover; border-radius: 6px;
}
.poster-overview .overview-figure-name { flex: 1; font-weight: 500; color: #1F1F1F; }
.poster-overview .overview-figure-price { font-size: 10px; color: #C49A6C; font-weight: 600; }
.poster-overview .overview-tag-row { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 14px; }
.poster-overview .overview-tag {
  font-size: 9px; padding: 2px 6px; border-radius: 8px; background: #FDF6EE; color: #C49A6C;
}
.poster-overview .overview-asset-row {
  display: flex; justify-content: space-between; align-items: center;
  background: #FAFAFA; padding: 8px 10px; border-radius: 8px; margin-bottom: 8px;
}
.poster-overview .overview-asset-label { font-size: 12px; color: #666; }
.poster-overview .overview-asset-value { font-size: 12px; color: #C49A6C; font-weight: 600; }
.poster-overview .overview-bottom {
  padding: 14px 20px; text-align: center; border-top: 1px solid #EBE8E4; background: #FAFAFA;
}
.poster-overview .poster-qr-img {
  width: 80px; height: 80px; border-radius: 8px; margin: 0 auto 6px;
  display: block;
}
.poster-overview .overview-qr-placeholder {
  width: 80px; height: 80px; background: #fff; border-radius: 8px; margin: 0 auto 6px;
  display: flex; align-items: center; justify-content: center; font-size: 36px;
  border: 1px solid #EBE8E4;
}
.poster-overview .overview-qr-text { font-size: 9px; color: #999; }
.poster-overview .overview-footer { font-size: 10px; color: #999; margin-top: 8px; }

/* ===== Poster: Gallery (藏品陈列) ===== */
.poster-gallery .gallery-top {
  background: linear-gradient(180deg, #E8F5E9 0%, #fff 40%);
  padding: 20px; text-align: center;
}
.poster-gallery .gallery-title { font-size: 18px; font-weight: 700; margin-bottom: 4px; }
.poster-gallery .gallery-subtitle { font-size: 11px; color: #999; margin-bottom: 14px; }
.poster-gallery .gallery-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px;
}
.poster-gallery .gallery-item {
  aspect-ratio: 1; background: #F0EEEB; border-radius: 8px;
  display: flex; align-items: center; justify-content: center; font-size: 24px;
  border: 1px solid #EBE8E4; position: relative; overflow: hidden;
}
.poster-gallery .gallery-item-img {
  width: 100%; height: 100%; object-fit: cover; display: block;
}
.poster-gallery .gallery-item-featured {
  grid-column: span 2; grid-row: span 2; font-size: 48px; background: linear-gradient(135deg, #FDF6EE, #F0EEEB);
}
.poster-gallery .gallery-item-badge {
  position: absolute; top: 4px; right: 4px; font-size: 8px; padding: 1px 4px; border-radius: 4px;
  background: #C49A6C; color: #fff;
}
.poster-gallery .gallery-body { padding: 16px 20px; flex: 1; }
.poster-gallery .gallery-feature-info { text-align: center; margin-bottom: 14px; }
.poster-gallery .gallery-feature-name { font-size: 14px; font-weight: 600; }
.poster-gallery .gallery-feature-desc { font-size: 10px; color: #999; margin-top: 2px; }
.poster-gallery .gallery-feature-price { font-size: 12px; color: #C49A6C; font-weight: 600; margin-top: 4px; }
.poster-gallery .gallery-stats-bar {
  display: flex; justify-content: center; gap: 20px;
}
.poster-gallery .gallery-stat-item { text-align: center; }
.poster-gallery .gallery-stat-num { font-size: 18px; font-weight: 700; color: #C49A6C; }
.poster-gallery .gallery-stat-label { font-size: 10px; color: #999; }
.poster-gallery .gallery-bottom {
  padding: 14px 20px; text-align: center; border-top: 1px solid #EBE8E4; background: #FAFAFA;
}
.poster-gallery .poster-qr-img {
  width: 80px; height: 80px; border-radius: 8px; margin: 0 auto 6px;
  display: block;
}
.poster-gallery .overview-qr-placeholder {
  width: 80px; height: 80px; background: #fff; border-radius: 8px; margin: 0 auto 6px;
  display: flex; align-items: center; justify-content: center; font-size: 36px;
  border: 1px solid #EBE8E4;
}
.poster-gallery .overview-qr-text { font-size: 9px; color: #999; }
.poster-gallery .overview-footer { font-size: 10px; color: #999; margin-top: 8px; }

/* ===== Poster: Minimal (极简数据) ===== */
.poster-canvas.poster-minimal {
  background: linear-gradient(180deg, #F3E5F5 0%, #FAFAFA 60%, #fff 100%);
  padding: 40px 24px; text-align: center; align-items: center;
}
.poster-minimal .minimal-badge {
  display: inline-block; font-size: 10px; padding: 3px 10px; border-radius: 12px;
  background: rgba(155,126,216,0.1); color: #9B7ED8; border: 1px solid rgba(155,126,216,0.2);
  margin-bottom: 20px;
}
.poster-minimal .minimal-title { font-size: 16px; font-weight: 600; color: #666; margin-bottom: 24px; }
.poster-minimal .minimal-big-num { font-size: 64px; font-weight: 800; color: #C49A6C; line-height: 1; margin-bottom: 8px; }
.poster-minimal .minimal-big-label { font-size: 14px; color: #666; margin-bottom: 32px; }
.poster-minimal .minimal-data-list { text-align: left; width: 100%; max-width: 200px; margin: 0 auto 32px; }
.poster-minimal .minimal-data-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 0; border-bottom: 1px solid #EBE8E4; font-size: 13px;
}
.poster-minimal .minimal-data-item:last-child { border-bottom: none; }
.poster-minimal .minimal-data-label { color: #666; }
.poster-minimal .minimal-data-value { color: #1F1F1F; font-weight: 600; }
.poster-minimal .minimal-data-value.accent { color: #C49A6C; }
.poster-minimal .minimal-data-value.green { color: #7EB8A2; }
.poster-minimal .minimal-data-value.red { color: #D66A6A; }
.poster-minimal .minimal-figure-names { font-size: 11px; color: #999; margin-bottom: 32px; line-height: 1.8; width: 100%; }
.poster-minimal .minimal-qr {
  width: 80px; height: 80px; border-radius: 10px; margin: 0 auto 6px; display: block;
}
.poster-minimal .minimal-qr-placeholder {
  width: 80px; height: 80px; background: #fff; border-radius: 10px; margin: 0 auto 6px;
  display: flex; align-items: center; justify-content: center; font-size: 36px;
  border: 1px solid #EBE8E4; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.poster-minimal .minimal-qr-text { font-size: 10px; color: #999; margin-bottom: 16px; }
.poster-minimal .minimal-footer { font-size: 11px; color: #999; }
</style>
