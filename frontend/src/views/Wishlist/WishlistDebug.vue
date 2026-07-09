<template>
  <div class="debug-page">
    <TopHeader />
    <div class="main-content">
      <div class="debug-container">
        <div class="page-title">
          <router-link to="/wishlist" class="back-btn">
            <i class="ri-arrow-left-s-line"></i>
            返回
          </router-link>
          <i class="ri-bug-line"></i>
          <span>HTML 抓取调试</span>
        </div>

        <div class="info-tip">
          <i class="ri-information-line"></i>
          <span>
            输入已在愿望清单中抓取过的 HPOI 商品链接，查看缓存中的原始 HTML 和解析数据。
            先使用「URL 智能抓取」后再来调试。
          </span>
        </div>

        <div class="input-row">
          <input
            v-model="url"
            type="text"
            placeholder="https://www.hpoi.net/hobby/116383"
            class="url-input"
            @keyup.enter="fetchHtml"
          />
          <button
            class="btn btn-primary"
            :disabled="loading"
            @click="fetchHtml"
          >
            <i :class="loading ? 'ri-loader-4-line ri-spin' : 'ri-search-line'"></i>
            {{ loading ? '查询中...' : '查看 HTML' }}
          </button>
        </div>

        <div v-if="error" class="error-box">
          <i class="ri-close-circle-line"></i>
          <span>{{ error }}</span>
        </div>

        <div v-if="data" class="result-section">
          <div class="section-header">
            <i class="ri-file-list-3-line"></i>
            <span>解析数据</span>
            <span class="badge">{{ data.source_url }}</span>
          </div>
          <pre class="json-block">{{ JSON.stringify(data.parsed_data, null, 2) }}</pre>
        </div>

        <div v-if="data" class="result-section">
          <div class="section-header">
            <i class="ri-html5-line"></i>
            <span>原始 HTML</span>
            <span class="badge">{{ formatSize(data.raw_html_size) }}</span>
            <button class="btn btn-sm" @click="copyHtml">
              <i class="ri-file-copy-line"></i>
              复制
            </button>
          </div>
          <pre class="html-block"><code>{{ data.raw_html }}</code></pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import TopHeader from '../../components/TopHeader.vue'
import { ElMessage } from 'element-plus'
import axios from '../../axios'

const url = ref('')
const loading = ref(false)
const error = ref('')
const data = ref(null)

async function fetchHtml() {
  if (!url.value.trim() || !url.value.startsWith('http')) {
    error.value = '请输入有效的 https:// 链接'
    return
  }

  loading.value = true
  error.value = ''
  data.value = null

  try {
    const res = await axios.get('/wishlist/debug/raw-html', {
      params: { url: url.value.trim() }
    })
    data.value = res
  } catch (e) {
    if (e.response?.status === 404) {
      error.value = '未找到该 URL 的缓存数据。请先在愿望清单中使用「URL 智能抓取」。'
    } else {
      error.value = '查询失败: ' + (e.response?.data?.detail || e.message)
    }
  } finally {
    loading.value = false
  }
}

function formatSize(bytes) {
  if (!bytes) return ''
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 / 1024).toFixed(1) + ' MB'
}

async function copyHtml() {
  if (!data.value?.raw_html) return
  try {
    await navigator.clipboard.writeText(data.value.raw_html)
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.warning('复制失败')
  }
}
</script>

<style scoped>
.debug-page {
  min-height: 100vh;
  background: #f5f5f5;
  padding-top: 64px;
}
.main-content {
  padding: 20px;
  max-width: 960px;
  margin: 0 auto;
}
.debug-container {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.page-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 16px;
}
.page-title i { color: #722ed1; }
.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  color: #666;
  text-decoration: none;
  font-size: 14px;
  font-weight: 400;
  padding: 4px 8px;
  border-radius: 6px;
  transition: all 0.2s;
  margin-right: 4px;
}
.back-btn:hover { background: #f5f5f5; color: #722ed1; }
.info-tip {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  background: #f0f5ff;
  border: 1px solid #d6e4ff;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 20px;
  color: #666;
  font-size: 13px;
  line-height: 1.5;
}
.info-tip i { color: #1677ff; margin-top: 2px; flex-shrink: 0; }
.input-row {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}
.url-input {
  flex: 1;
  height: 42px;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  padding: 0 16px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}
.url-input:focus { border-color: #1677ff; box-shadow: 0 0 0 2px rgba(22,119,255,0.1); }
.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 42px;
  padding: 0 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-primary { background: #1677ff; color: #fff; }
.btn-primary:hover:not(:disabled) { background: #4096ff; }
.btn-sm {
  height: 32px;
  padding: 0 12px;
  font-size: 13px;
  background: #f5f5f5;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
}
.btn-sm:hover { background: #e8e8e8; }
.error-box {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fff2f0;
  border: 1px solid #ffccc7;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 16px;
  color: #ff4d4f;
  font-size: 13px;
}
.error-box i { font-size: 16px; }
.result-section {
  margin-top: 16px;
}
.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
  color: #333;
}
.section-header .badge {
  font-size: 12px;
  color: #999;
  font-weight: 400;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 400px;
}
.json-block {
  background: #fafafa;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 16px;
  font-size: 13px;
  line-height: 1.6;
  overflow-x: auto;
  max-height: 300px;
  overflow-y: auto;
}
.html-block {
  background: #1e1e1e;
  color: #d4d4d4;
  border-radius: 8px;
  padding: 16px;
  font-size: 12px;
  line-height: 1.5;
  overflow-x: auto;
  max-height: 500px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-all;
}
.html-block code { font-family: 'JetBrains Mono', 'Fira Code', monospace; }
</style>
