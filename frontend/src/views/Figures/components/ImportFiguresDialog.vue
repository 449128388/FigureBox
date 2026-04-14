<template>
  <div class="dialog-overlay" v-if="show" @click.self="$emit('close')">
    <div class="dialog-container">
      <h3>导入手办数据</h3>
      <div class="dialog-content">
        <div class="upload-area">
          <input
            type="file"
            ref="fileInput"
            accept=".json"
            @change="handleFileChange"
            style="display: none"
          />
          <div
            class="upload-box"
            :class="{ 'has-file': selectedFile, 'drag-over': isDragOver }"
            @click="$refs.fileInput.click()"
            @dragover.prevent="isDragOver = true"
            @dragleave.prevent="isDragOver = false"
            @drop.prevent="handleDrop"
          >
            <i class="fa-solid fa-cloud-upload-alt upload-icon"></i>
            <p v-if="!selectedFile" class="upload-text">
              点击选择文件或拖拽JSON文件到此处
            </p>
            <p v-else class="file-name">
              <i class="fa-solid fa-file-code"></i>
              {{ selectedFile.name }}
            </p>
            <p class="upload-hint">支持 .json 格式文件</p>
          </div>
        </div>

        <div v-if="importStatus === 'preview' && previewData.length > 0" class="preview-section">
          <h4>数据预览 (共 {{ previewData.length }} 条记录)</h4>
          <div class="preview-list">
            <div
              v-for="(item, index) in previewData.slice(0, 5)"
              :key="index"
              class="preview-item"
            >
              <span class="preview-name">{{ item.name || '未命名' }}</span>
              <span class="preview-orders" v-if="item.orders && item.orders.length > 0">
                ({{ item.orders.length }} 个订单)
              </span>
            </div>
            <div v-if="previewData.length > 5" class="preview-more">
              ...还有 {{ previewData.length - 5 }} 条记录
            </div>
          </div>
        </div>

        <div v-if="importStatus === 'success'" class="result-section success">
          <i class="fa-solid fa-check-circle"></i>
          <p>导入成功！</p>
          <p class="result-detail">
            成功导入 {{ importResult.imported }} 个手办，{{ importResult.orders }} 个订单
          </p>
        </div>

        <div v-if="importStatus === 'error'" class="result-section error">
          <i class="fa-solid fa-exclamation-circle"></i>
          <p>导入失败</p>
          <p class="result-detail">{{ errorMessage }}</p>
        </div>
      </div>

      <div class="dialog-actions">
        <button class="btn btn-cancel" @click="$emit('close')" :disabled="isImporting">
          {{ importStatus === 'success' ? '关闭' : '取消' }}
        </button>
        <button
          class="btn btn-import"
          @click="handleImport"
          :disabled="!selectedFile || isImporting || importStatus === 'success'"
        >
          <i v-if="isImporting" class="fa-solid fa-spinner fa-spin"></i>
          <span v-else>开始导入</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'

export default {
  name: 'ImportFiguresDialog',
  props: {
    show: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close', 'import'],
  setup(props, { emit }) {
    const fileInput = ref(null)
    const selectedFile = ref(null)
    const isDragOver = ref(false)
    const isImporting = ref(false)
    const importStatus = ref('idle') // idle, preview, success, error
    const previewData = ref([])
    const importResult = ref({ imported: 0, orders: 0 })
    const errorMessage = ref('')

    // 重置状态当对话框关闭时
    watch(() => props.show, (newVal) => {
      if (!newVal) {
        resetState()
      }
    })

    const resetState = () => {
      selectedFile.value = null
      isImporting.value = false
      importStatus.value = 'idle'
      previewData.value = []
      importResult.value = { imported: 0, orders: 0 }
      errorMessage.value = ''
    }

    const handleFileChange = (event) => {
      const file = event.target.files[0]
      if (file) {
        processFile(file)
      }
    }

    const handleDrop = (event) => {
      isDragOver.value = false
      const file = event.dataTransfer.files[0]
      if (file && file.name.endsWith('.json')) {
        processFile(file)
      }
    }

    const processFile = (file) => {
      selectedFile.value = file
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const data = JSON.parse(e.target.result)
          if (Array.isArray(data)) {
            previewData.value = data
            importStatus.value = 'preview'
          } else {
            throw new Error('数据格式错误：期望数组格式')
          }
        } catch (error) {
          importStatus.value = 'error'
          errorMessage.value = '文件解析失败：' + error.message
        }
      }
      reader.readAsText(file)
    }

    const handleImport = async () => {
      if (!selectedFile.value) return

      isImporting.value = true
      try {
        const result = await emit('import', previewData.value)
        if (result && result.success) {
          importResult.value = {
            imported: result.imported || 0,
            orders: result.orders || 0
          }
          importStatus.value = 'success'
        } else {
          throw new Error(result?.message || '导入失败')
        }
      } catch (error) {
        importStatus.value = 'error'
        errorMessage.value = error.message || '导入过程中发生错误'
      } finally {
        isImporting.value = false
      }
    }

    return {
      fileInput,
      selectedFile,
      isDragOver,
      isImporting,
      importStatus,
      previewData,
      importResult,
      errorMessage,
      handleFileChange,
      handleDrop,
      handleImport
    }
  }
}
</script>

<style scoped>
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.dialog-container {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.dialog-container h3 {
  margin: 0;
  padding: 20px 24px;
  border-bottom: 1px solid #e0e0e0;
  font-size: 18px;
  color: #333;
}

.dialog-content {
  padding: 24px;
}

.upload-area {
  margin-bottom: 20px;
}

.upload-box {
  border: 2px dashed #ccc;
  border-radius: 8px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-box:hover,
.upload-box.drag-over {
  border-color: #9C27B0;
  background-color: #f3e5f5;
}

.upload-box.has-file {
  border-color: #4CAF50;
  background-color: #e8f5e9;
}

.upload-icon {
  font-size: 48px;
  color: #9C27B0;
  margin-bottom: 16px;
}

.upload-text {
  font-size: 16px;
  color: #666;
  margin: 0 0 8px;
}

.file-name {
  font-size: 16px;
  color: #333;
  margin: 0 0 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.upload-hint {
  font-size: 12px;
  color: #999;
  margin: 0;
}

.preview-section {
  margin-top: 20px;
  padding: 16px;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.preview-section h4 {
  margin: 0 0 12px;
  font-size: 14px;
  color: #333;
}

.preview-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.preview-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: white;
  border-radius: 4px;
  font-size: 13px;
}

.preview-name {
  font-weight: 500;
  color: #333;
}

.preview-orders {
  color: #666;
  font-size: 12px;
}

.preview-more {
  text-align: center;
  color: #999;
  font-size: 12px;
  padding: 8px;
}

.result-section {
  margin-top: 20px;
  padding: 24px;
  border-radius: 8px;
  text-align: center;
}

.result-section.success {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.result-section.error {
  background-color: #ffebee;
  color: #c62828;
}

.result-section i {
  font-size: 48px;
  margin-bottom: 12px;
}

.result-section p {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
}

.result-detail {
  margin-top: 8px !important;
  font-size: 14px !important;
  font-weight: normal !important;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #e0e0e0;
}

.btn {
  padding: 10px 24px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-cancel {
  background-color: #e0e0e0;
  color: #333;
}

.btn-cancel:hover:not(:disabled) {
  background-color: #bdbdbd;
}

.btn-import {
  background-color: #9C27B0;
  color: white;
}

.btn-import:hover:not(:disabled) {
  background-color: #7B1FA2;
}
</style>
