<!--
  PanelBasic.vue - 基本资料面板
  通过 props 接收 basicForm / nicknameLen / signatureLen / bioLen / years / userId
  通过 save 事件把保存动作交给父级
-->
<template>
  <div class="panel" :class="{ active: active }">
    <div class="panel-header">基本资料</div>
    <div class="panel-body">
      <div class="form-row">
        <label class="form-label">昵称</label>
        <div class="form-control">
          <div class="input-wrap">
            <input type="text" v-model="basicForm.nickname" maxlength="25" placeholder="请输入昵称">
            <span class="char-count" :style="{ color: nicknameLen >= 25 ? '#f25d8e' : '' }">{{ nicknameLen }}/25</span>
          </div>
          <div class="form-hint">昵称禁止使用特殊符号或空格</div>
        </div>
      </div>

      <div class="form-row">
        <label class="form-label">用户ID</label>
        <div class="form-control">
          <div class="input-wrap small">
            <input type="text" :value="userId" readonly>
          </div>
        </div>
      </div>

      <div class="form-row">
        <label class="form-label">签名</label>
        <div class="form-control">
          <div class="input-wrap">
            <input type="text" v-model="basicForm.signature" maxlength="24" placeholder="编辑个签名 showcase 一下自己吧">
            <span class="char-count" :style="{ color: signatureLen >= 24 ? '#f25d8e' : '' }">{{ signatureLen }}/24</span>
          </div>
        </div>
      </div>

      <div class="form-row">
        <label class="form-label">性别</label>
        <div class="form-control">
          <div class="radio-group">
            <label class="radio-item">
              <input type="radio" v-model="basicForm.gender" value="male"> 男
            </label>
            <label class="radio-item">
              <input type="radio" v-model="basicForm.gender" value="female"> 女
            </label>
            <label class="radio-item">
              <input type="radio" v-model="basicForm.gender" value="secret"> 保密
            </label>
          </div>
        </div>
      </div>

      <div class="form-row">
        <label class="form-label">生日</label>
        <div class="form-control">
          <div class="select-group">
            <select v-model.number="basicForm.birthday.year">
              <option v-for="y in years" :key="y" :value="y">{{ y }}年</option>
            </select>
            <select v-model="basicForm.birthday.month">
              <option v-for="m in 12" :key="m" :value="String(m).padStart(2,'0')">{{ String(m).padStart(2,'0') }}月</option>
            </select>
            <select v-model="basicForm.birthday.day">
              <option v-for="d in 31" :key="d" :value="String(d).padStart(2,'0')">{{ String(d).padStart(2,'0') }}日</option>
            </select>
          </div>
        </div>
      </div>

      <div class="form-row">
        <label class="form-label">自我介绍</label>
        <div class="form-control">
          <div class="input-wrap large">
            <textarea v-model="basicForm.bio" maxlength="500" placeholder="500字以内"></textarea>
            <span class="char-count" :style="{ color: bioLen >= 500 ? '#f25d8e' : '' }">{{ bioLen }}/500</span>
          </div>
        </div>
      </div>

      <div class="form-actions">
        <button class="btn btn-primary" @click="$emit('save')">保存</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PanelBasic',
  props: {
    active: { type: Boolean, default: false },
    basicForm: { type: Object, required: true },
    nicknameLen: { type: Number, default: 0 },
    signatureLen: { type: Number, default: 0 },
    bioLen: { type: Number, default: 0 },
    years: { type: Array, default: () => [] },
    userId: { type: [String, Number], default: '' }
  },
  emits: ['save']
}
</script>

<style scoped>
.panel { background: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); overflow: hidden; display: none; }
.panel.active { display: block; animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
.panel-header { padding: 20px 24px; border-bottom: 1px solid #e3e5e7; font-size: 18px; font-weight: 700; color: #18191c; }
.panel-body { padding: 24px 32px 32px; }

.form-row { display: flex; align-items: flex-start; margin-bottom: 24px; }
.form-label { width: 110px; text-align: right; padding-right: 20px; padding-top: 9px; font-size: 14px; color: #61666d; flex-shrink: 0; white-space: nowrap; }
.form-control { flex: 1; min-width: 0; }
.input-wrap { position: relative; max-width: 480px; }
.input-wrap.small { max-width: 200px; }
.input-wrap.large { max-width: 600px; }
.form-hint { margin-top: 6px; font-size: 12px; color: #9499a0; }

input[type="text"], textarea, select {
  width: 100%;
  padding: 9px 12px;
  border: 1px solid #e3e5e7;
  border-radius: 6px;
  background: #fff;
  font-size: 14px;
  color: #18191c;
  outline: none;
  transition: all 0.2s;
  font-family: inherit;
}
input:focus, textarea:focus, select:focus { border-color: #00a1d6; box-shadow: 0 0 0 3px rgba(0, 161, 214, 0.15); }
input::placeholder, textarea::placeholder { color: #9499a0; }
input:read-only { background: #f6f7f8; color: #9499a0; cursor: default; }

.char-count {
  position: absolute; right: 10px; bottom: 9px; font-size: 12px; color: #9499a0;
  pointer-events: none; background: rgba(255,255,255,0.9); padding: 0 4px; border-radius: 4px;
}
textarea + .char-count { bottom: 10px; }
textarea { resize: vertical; min-height: 120px; line-height: 1.6; padding-bottom: 28px; }

.radio-group { display: flex; gap: 24px; padding-top: 6px; }
.radio-item {
  display: flex; align-items: center; gap: 6px; font-size: 14px; color: #18191c; cursor: pointer; user-select: none;
}
.radio-item input[type="radio"] {
  appearance: none; width: 16px; height: 16px; border: 2px solid #c9cdd4; border-radius: 50%;
  outline: none; cursor: pointer; transition: all 0.2s; position: relative; padding: 0;
}
.radio-item input[type="radio"]:checked { border-color: #00a1d6; }
.radio-item input[type="radio"]:checked::after {
  content: ""; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
  width: 8px; height: 8px; background: #00a1d6; border-radius: 50%;
}

.select-group { display: flex; gap: 10px; }
.select-group select {
  width: auto; min-width: 100px; padding-right: 28px; appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg width='10' height='6' viewBox='0 0 10 6' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%239499a0' stroke-width='1.5' fill='none' fill-rule='evenodd'/%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: right 10px center;
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
  .form-row { flex-direction: column; }
  .form-label { text-align: left; width: auto; padding: 0 0 6px; }
  .form-actions { padding-left: 0; }
}
</style>
