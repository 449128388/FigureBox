<!--
  PanelPush.vue - 推送设置面板
  props: active / toggles
  emits: toggle-switch（key）/ save
-->
<template>
  <div class="panel" :class="{ active: active }">
    <div class="panel-header">推送设置</div>
    <div class="panel-body">
      <div class="setting-group">
        <div class="switch-row">
          <div>
            <div class="switch-label">尾款到期提醒</div>
            <div class="switch-hint">手办尾款支付截止前 3 天推送通知</div>
          </div>
          <div
            class="toggle"
            :class="{ active: toggles.push_balance_remind }"
            @click="$emit('toggle-switch', 'push_balance_remind')"
          ></div>
        </div>
        <div class="switch-row">
          <div>
            <div class="switch-label">价格预警推送</div>
            <div class="switch-hint">关注的手办市场价达到设定阈值时通知</div>
          </div>
          <div
            class="toggle"
            :class="{ active: toggles.push_price_alert }"
            @click="$emit('toggle-switch', 'push_price_alert')"
          ></div>
        </div>
        <div class="switch-row">
          <div>
            <div class="switch-label">系统公告</div>
            <div class="switch-hint">FigureBox 功能更新与维护通知</div>
          </div>
          <div
            class="toggle"
            :class="{ active: toggles.push_system_notice }"
            @click="$emit('toggle-switch', 'push_system_notice')"
          ></div>
        </div>
        <div class="switch-row">
          <div>
            <div class="switch-label">邮件周报</div>
            <div class="switch-hint">每周一发送资产收益周报至绑定邮箱</div>
          </div>
          <div
            class="toggle"
            :class="{ active: toggles.push_weekly_report }"
            @click="$emit('toggle-switch', 'push_weekly_report')"
          ></div>
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
  name: 'PanelPush',
  props: {
    active: { type: Boolean, default: false },
    toggles: { type: Object, required: true }
  },
  emits: ['toggle-switch', 'save']
}
</script>

<style scoped>
.panel { background: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); overflow: hidden; display: none; }
.panel.active { display: block; animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
.panel-header { padding: 20px 24px; border-bottom: 1px solid #e3e5e7; font-size: 18px; font-weight: 700; color: #18191c; }
.panel-body { padding: 24px 32px 32px; }

.setting-group { margin-bottom: 28px; }
.switch-row { display: flex; align-items: center; justify-content: space-between; padding: 12px 0; }
.switch-label { font-size: 14px; color: #18191c; }
.switch-hint { font-size: 12px; color: #9499a0; margin-top: 2px; }

.toggle {
  position: relative; width: 40px; height: 22px; background: #c9cdd4;
  border-radius: 11px; cursor: pointer; transition: background 0.3s; flex-shrink: 0;
}
.toggle::after {
  content: ""; position: absolute; top: 2px; left: 2px;
  width: 18px; height: 18px; background: #fff; border-radius: 50%;
  transition: transform 0.3s; box-shadow: 0 1px 3px rgba(0,0,0,0.15);
}
.toggle.active { background: #00a1d6; }
.toggle.active::after { transform: translateX(18px); }

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
}
</style>
