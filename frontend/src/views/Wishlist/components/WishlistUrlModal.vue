<template>
  <el-dialog
    :model-value="visible"
    title="从链接添加愿望"
    width="560px"
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
      <p class="form-hint">支持 HPOI、Amiami、MyFigureCollection 等站点</p>
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
      <div class="result-title">
        <i class="ri-check-double-line"></i>
        抓取成功
      </div>
      <img v-if="result.image" :src="result.image" class="preview-image" alt="预览" />
      <div class="result-item">
        <span>名称</span>
        <span style="font-weight:600">{{ result.name || '-' }}</span>
      </div>
      <div class="result-item">
        <span>定价</span>
        <span style="color:#ff4d4f;font-weight:600">
          {{ result.price ? `¥${result.price.toLocaleString()}` : '-' }} {{ result.currency }}
        </span>
      </div>
      <div class="result-item">
        <span>发售时间</span>
        <span>{{ result.release_date || '-' }}</span>
      </div>
      <div class="result-item">
        <span>厂商</span>
        <span>{{ result.manufacturer || '-' }}</span>
      </div>
      <div class="result-item">
        <span>比例</span>
        <span>{{ result.scale || '-' }}</span>
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
.fetch-result {
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 16px;
}
.result-title {
  color: #52c41a;
  font-weight: 600;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.preview-image {
  width: 100%;
  max-height: 200px;
  object-fit: contain;
  background: #fff;
  border-radius: 4px;
  margin-bottom: 8px;
}
.result-item {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  font-size: 13px;
  color: #666;
}
.result-item span:last-child { color: #333; }
</style>
