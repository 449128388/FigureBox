<!--
  PanelAvatar.vue - 头像设置面板
  props: active / avatarSrc
  emits: trigger-file-input（请求父级打开文件选择器）/ preview（文件预览）/ save（保存）
-->
<template>
  <div class="panel" :class="{ active: active }">
    <div class="panel-header">头像设置</div>
    <div class="panel-body">
      <div class="avatar-section">
        <div class="avatar-preview-box">
          <div class="label">当前头像</div>
          <img :src="avatarSrc" class="avatar-large" alt="当前头像">
          <br>
          <a class="avatar-change-link" @click="$emit('trigger-file-input', avatarInput)">更换头像</a>
          <input
            type="file"
            ref="avatarInput"
            accept="image/*"
            style="display:none"
            @change="$emit('preview', $event)"
          />
          <div class="avatar-tips">
            支持 jpg、jpeg、png、gif 格式<br>
            文件大小不超过 5MB<br>
            建议尺寸 200×200 像素以上
          </div>
        </div>
        <div class="avatar-preview-box">
          <div class="label">预览头像</div>
          <img :src="avatarSrc" class="avatar-circle" alt="预览头像">
        </div>
      </div>
      <div class="form-actions" style="margin-top:24px;">
        <button class="btn btn-primary" @click="$emit('save')">保存</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PanelAvatar',
  props: {
    active: { type: Boolean, default: false },
    avatarSrc: { type: String, default: '' }
  },
  emits: ['trigger-file-input', 'preview', 'save'],
  data() {
    return {
      avatarInput: null
    }
  },
  mounted() {
    this.avatarInput = this.$refs.avatarInput
  }
}
</script>

<style scoped>
.panel { background: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); overflow: hidden; display: none; }
.panel.active { display: block; animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
.panel-header { padding: 20px 24px; border-bottom: 1px solid #e3e5e7; font-size: 18px; font-weight: 700; color: #18191c; }
.panel-body { padding: 24px 32px 32px; }

.avatar-section { display: flex; gap: 40px; align-items: flex-start; }
.avatar-preview-box { text-align: center; }
.avatar-preview-box .label { font-size: 13px; color: #9499a0; margin-bottom: 12px; }
.avatar-large {
  width: 200px; height: 200px; border-radius: 8px; background: #f6f7f8;
  object-fit: cover; border: 1px solid #e3e5e7;
}
.avatar-circle {
  width: 100px; height: 100px; border-radius: 50%; background: #f6f7f8;
  object-fit: cover; border: 1px solid #e3e5e7;
}
.avatar-change-link {
  display: inline-block; margin-top: 12px; color: #00a1d6; font-size: 14px;
  cursor: pointer; text-decoration: none;
}
.avatar-change-link:hover { text-decoration: underline; }
.avatar-tips {
  margin-top: 24px; padding: 12px 16px; background: #f6f7f8; border-radius: 6px;
  font-size: 12px; color: #9499a0; line-height: 1.8; max-width: 320px;
}

.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 6px;
  padding: 9px 24px; border-radius: 6px; font-size: 14px; font-weight: 500;
  cursor: pointer; border: none; outline: none; transition: all 0.2s;
}
.btn-primary { background: #00a1d6; color: #fff; }
.btn-primary:hover { background: #008db1; }
.form-actions { margin-top: 8px; padding-left: 130px; display: flex; gap: 16px; }

@media (max-width: 900px) {
  .form-actions { padding-left: 0; }
  .avatar-section { flex-direction: column; align-items: center; }
}
</style>
