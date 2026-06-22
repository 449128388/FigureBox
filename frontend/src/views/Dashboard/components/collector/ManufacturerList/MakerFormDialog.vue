<!--
  MakerFormDialog.vue - 添加/编辑本命厂商弹窗组件

  功能说明：
  - 提供本命厂商的新增和编辑表单
  - 表单字段：厂商名称（必填）、日文名称、描述、官网链接、推特链接、Logo URL
  - 支持表单校验，厂商名称不能为空

  交互流程：
  - 点击「添加本命厂商」或「编辑」按钮时打开本弹窗
  - 填写信息后点击「保存」提交
  - 保存成功后自动关闭弹窗并刷新列表
-->
<template>
  <div v-if="visible" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <div class="modal-header">
        <div class="modal-title">{{ isEditing ? '编辑本命厂商' : '添加本命厂商' }}</div>
        <div class="modal-close" @click="$emit('close')">×</div>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label class="form-label">
            厂商名称（中文）<span class="required">*</span>
          </label>
          <input
            type="text"
            class="form-input"
            v-model="form.name"
            placeholder="例如：BINDing"
          />
          <div class="form-hint">可自定义名称，将显示在收藏柜中</div>
        </div>
        <div class="form-group">
          <label class="form-label">厂商名称（日文/原文）</label>
          <input
            type="text"
            class="form-input"
            v-model="form.name_jp"
            placeholder="例如：バインディング"
          />
        </div>
        <div class="form-group">
          <label class="form-label">厂商描述</label>
          <textarea
            class="form-textarea"
            v-model="form.description"
            placeholder="例如：该社系FREEing的里界品牌..."
          ></textarea>
        </div>
        <div class="form-group">
          <label class="form-label">官网链接</label>
          <input
            type="text"
            class="form-input"
            v-model="form.website_url"
            placeholder="https://..."
          />
        </div>
        <div class="form-group">
          <label class="form-label">推特/X 链接</label>
          <input
            type="text"
            class="form-input"
            v-model="form.twitter_url"
            placeholder="https://twitter.com/..."
          />
        </div>
        <div class="form-group">
          <label class="form-label">Logo URL（可选）</label>
          <input
            type="text"
            class="form-input"
            v-model="form.logo_url"
            placeholder="https://..."
          />
          <div class="form-hint">留空将使用默认图标</div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn-modal" @click="$emit('close')">取消</button>
        <button class="btn-modal btn-modal-primary" @click="handleSave">
          保存
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'MakerFormDialog',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    isEditing: {
      type: Boolean,
      default: false
    },
    formData: {
      type: Object,
      default: () => ({
        name: '',
        name_jp: '',
        description: '',
        logo_url: '',
        website_url: '',
        twitter_url: ''
      })
    }
  },
  emits: ['close', 'save'],
  setup(props, { emit }) {
    const form = reactive({
      name: '',
      name_jp: '',
      description: '',
      logo_url: '',
      website_url: '',
      twitter_url: ''
    })

    // 监听 formData 变化
    watch(
      () => props.formData,
      (newVal) => {
        if (newVal) {
          form.name = newVal.name || ''
          form.name_jp = newVal.name_jp || ''
          form.description = newVal.description || ''
          form.logo_url = newVal.logo_url || ''
          form.website_url = newVal.website_url || ''
          form.twitter_url = newVal.twitter_url || ''
        }
      },
      { immediate: true, deep: true }
    )

    // 监听弹窗打开重置
    watch(
      () => props.visible,
      (newVal) => {
        if (newVal && !props.isEditing) {
          form.name = ''
          form.name_jp = ''
          form.description = ''
          form.logo_url = ''
          form.website_url = ''
          form.twitter_url = ''
        }
      }
    )

    const handleSave = () => {
      if (!form.name || !form.name.trim()) {
        ElMessage.warning('请填写厂商名称')
        return
      }
      emit('save', { ...form })
    }

    return {
      form,
      handleSave
    }
  }
}
</script>

<style scoped>
/* Modal Overlay */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.4);
  z-index: 200;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(4px);
}

.modal {
  background: #fff;
  border-radius: 12px;
  width: 100%;
  max-width: 480px;
  margin: 20px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.12);
  overflow: hidden;
  animation: modalIn 0.3s ease;
}

@keyframes modalIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.modal-header {
  padding: 16px 20px;
  border-bottom: 1px solid #EBE8E4;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-title {
  font-size: 16px;
  font-weight: 600;
}

.modal-close {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 1px solid #EBE8E4;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 16px;
  color: #999;
  transition: all 0.2s;
}

.modal-close:hover {
  border-color: #D66A6A;
  color: #D66A6A;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #666;
  margin-bottom: 6px;
}

.required {
  color: #D66A6A;
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #EBE8E4;
  border-radius: 8px;
  font-size: 14px;
  color: #1F1F1F;
  background: #fff;
  transition: border-color 0.2s;
  font-family: inherit;
}

.form-input:focus {
  outline: none;
  border-color: #00BCD4;
}

.form-input::placeholder {
  color: #999;
}

.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #EBE8E4;
  border-radius: 8px;
  font-size: 14px;
  color: #1F1F1F;
  background: #fff;
  transition: border-color 0.2s;
  font-family: inherit;
  resize: vertical;
  min-height: 60px;
}

.form-textarea:focus {
  outline: none;
  border-color: #00BCD4;
}

.form-hint {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.modal-footer {
  padding: 12px 20px 20px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn-modal {
  padding: 8px 18px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #EBE8E4;
  background: #fff;
  color: #666;
}

.btn-modal:hover {
  border-color: #666;
}

.btn-modal-primary {
  background: #00BCD4;
  border-color: #00BCD4;
  color: #fff;
}

.btn-modal-primary:hover {
  background: #00ACC1;
  border-color: #00ACC1;
}
</style>
