<template>
  <el-dialog
    :model-value="visible"
    title="从链接添加愿望"
    width="780px"
    :close-on-click-modal="false"
    @close="$emit('close')"
  >
    <div class="form-group">
      <label class="form-label">商品链接 <span class="required">*</span></label>
      <div class="url-input-group">
        <input
          v-model="url"
          type="text"
          class="form-input"
          placeholder="https://www.hpoi.net/hobby/116383"
        />
        <button class="btn-fetch" :disabled="loading" @click="fetchFromUrl">
          <i class="ri-magic-line"></i> 抓取
        </button>
      </div>
      <p class="form-hint">支持 HPOI 等站点</p>
    </div>

    <div v-if="fetching" class="fetch-loading">
      <div class="spinner"></div>
      <span>{{ progressText || '正在解析页面，提取手办信息...' }}</span>
    </div>

    <div v-if="error" class="fetch-error">
      <i class="ri-error-warning-line"></i>
      <span>{{ error }}</span>
    </div>

    <div v-if="result" class="fetch-result">
      <!-- 中文名称 -->
      <div class="result-chinese-name">
        <span class="label">中文名称:</span>
        <span class="value">{{ result.name || '-' }}</span>
      </div>

      <!-- 左图右信息 -->
      <div class="result-body">
        <div class="result-image-wrap">
          <img v-if="result.image" :src="result.image" class="preview-image" alt="预览" />
          <div v-else class="preview-image preview-placeholder">
            <i class="ri-image-line"></i>
          </div>
        </div>

        <div class="result-info">
          <div class="info-row">
            <span class="info-label">名称</span>
            <span class="info-value">{{ result.japanese_name || '-' }}</span>
          </div>
          <div v-if="result.attributes" class="info-row">
            <span class="info-label">属性</span>
            <span class="info-value text-green">{{ Array.isArray(result.attributes) ? result.attributes.join('、') : result.attributes }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">定价</span>
            <span class="info-value">
              <template v-if="result.price_text">
                {{ result.price_text }}
              </template>
              <template v-else-if="result.price">
                <template v-if="result.currency === 'CNY'">¥{{ result.price.toLocaleString() }} CNY</template>
                <template v-else>¥{{ result.price.toLocaleString() }} JPY</template>
              </template>
              <template v-else>-</template>
            </span>
          </div>
          <div class="info-row">
            <span class="info-label">出货日</span>
            <span class="info-value text-green">{{ result.release_date_text || result.release_date || '-' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">比例</span>
            <span class="info-value text-green">{{ result.scale || '-' }}</span>
          </div>
          <div v-if="result.production" class="info-row">
            <span class="info-label">制作</span>
            <span class="info-value text-blue">{{ result.production }}</span>
          </div>
          <div v-if="result.manufacturer" class="info-row">
            <span class="info-label">发行</span>
            <span class="info-value text-blue">{{ result.manufacturer }}</span>
          </div>
          <div v-if="result.painter" class="info-row">
            <span class="info-label">涂装</span>
            <span class="info-value text-blue">{{ result.painter }}</span>
          </div>
          <div v-if="result.original_art" class="info-row">
            <span class="info-label">原画</span>
            <span class="info-value text-blue">{{ result.original_art }}</span>
          </div>
          <div v-if="result.work" class="info-row">
            <span class="info-label">作品</span>
            <span class="info-value text-blue">{{ result.work }}</span>
          </div>
          <div v-if="result.size" class="info-row">
            <span class="info-label">尺寸</span>
            <span class="info-value text-green">{{ result.size }}</span>
          </div>
          <div v-if="result.material" class="info-row">
            <span class="info-label">材质</span>
            <span class="info-value text-green">{{ result.material }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="form-group" style="margin-top:20px">
      <label class="form-label">状态</label>
      <select v-model="status" class="form-select">
        <option value="wish">愿望中</option>
        <option value="released">已发售</option>
        <option value="purchased">已购买</option>
      </select>
    </div>
    <div class="form-group">
      <label class="form-label">备注</label>
      <textarea
        v-model="note"
        class="form-textarea"
        placeholder="记录一些购买注意事项..."
        rows="3"
      ></textarea>
    </div>

    <template #footer>
      <el-button @click="$emit('close')">取消</el-button>
      <el-button type="primary" :loading="saving" @click="onSave">保存到愿望清单</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useWishlistUrlFetch } from '../composables/useWishlistUrlFetch'

const props = defineProps({
  visible: { type: Boolean, default: false }
})
const emit = defineEmits(['close', 'saved'])

const {
  url, loading, fetching, progressText, result, error, note, status,
  reset, fetchFromUrl, saveFromUrl
} = useWishlistUrlFetch()
const saving = ref(false)

watch(() => props.visible, (v) => {
  if (v) reset()
  else reset()
})

const onSave = async () => {
  if (!result.value) {
    ElMessage.warning('请先抓取链接')
    return
  }
  saving.value = true
  const ok = await saveFromUrl((created) => {
    emit('saved', created)
  })
  saving.value = false
  if (ok) {
    emit('close')
  }
}
</script>

<style scoped>
.form-group { margin-bottom: 16px; }
.form-label {
  display: block;
  margin-bottom: 6px;
  color: #333;
  font-size: 14px;
  font-weight: 500;
}
.required { color: #ff4d4f; }
.url-input-group { display: flex; gap: 8px; }
.form-input, .form-textarea, .form-select {
  width: 100%;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 14px;
  outline: none;
  transition: all 0.3s;
  font-family: inherit;
  box-sizing: border-box;
}
.form-input:focus, .form-textarea:focus, .form-select:focus {
  border-color: #1890ff;
  box-shadow: 0 0 0 3px rgba(24,144,255,0.1);
}
.btn-fetch {
  padding: 8px 16px;
  background: #722ed1;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
  font-size: 14px;
  font-weight: 500;
}
.btn-fetch:hover:not(:disabled) { background: #531dab; }
.btn-fetch:disabled { opacity: 0.6; cursor: not-allowed; }
.form-hint { font-size: 12px; color: #999; margin-top: 6px; margin-bottom: 0; }
.fetch-loading {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f0f5ff;
  border-radius: 6px;
  margin-bottom: 16px;
  color: #1890ff;
}
.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #1890ff;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.fetch-error {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #fff2f0;
  border: 1px solid #ffccc7;
  border-radius: 6px;
  margin-bottom: 16px;
  color: #ff4d4f;
  font-size: 13px;
}

/* === 抓取成功（深色主题） === */
.fetch-result {
  background: linear-gradient(135deg, #1a0f2e 0%, #2d1b4e 50%, #1a0f2e 100%);
  border-radius: 10px;
  padding: 18px 20px;
  margin-bottom: 16px;
  color: #e0d9f0;
  box-shadow: 0 4px 16px rgba(114, 46, 209, 0.15);
}
.result-chinese-name {
  display: flex;
  align-items: baseline;
  gap: 8px;
  padding-bottom: 14px;
  margin-bottom: 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.result-chinese-name .label {
  font-size: 14px;
  color: #b8a8d9;
  flex-shrink: 0;
}
.result-chinese-name .value {
  font-size: 15px;
  font-weight: 600;
  color: #ffffff;
  word-break: break-all;
}
.result-body {
  display: flex;
  gap: 18px;
  align-items: flex-start;
}
.result-image-wrap {
  width: 180px;
  flex-shrink: 0;
}
.preview-image {
  width: 180px;
  height: 240px;
  object-fit: cover;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  display: block;
}
.preview-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.3);
  font-size: 32px;
}
.result-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}
.info-row {
  display: flex;
  align-items: baseline;
  font-size: 13px;
  line-height: 1.6;
}
.info-label {
  color: #b8a8d9;
  width: 56px;
  flex-shrink: 0;
  text-align: left;
}
.info-value {
  color: #e8e0f5;
  word-break: break-all;
  flex: 1;
  min-width: 0;
}
.text-green { color: #4ade80; }
.text-blue { color: #60a5fa; }
</style>
