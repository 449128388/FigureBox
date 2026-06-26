<!--
  PrivacySettings.vue - 隐私设置组件

  功能说明：
  - 控制用户收藏数据的可见范围
  - 支持访问权限、数据展示、分享设置三类配置

  使用:
  <PrivacySettings :visible.sync="visible" />
-->
<template>
  <div v-if="visible" class="modal-overlay" @click="close">
    <div class="modal" @click.stop>
      <div class="modal-header">
        <div class="modal-title">🔒 隐私设置</div>
        <div class="modal-close" @click="close">×</div>
      </div>
      <div class="modal-body" style="padding:0;">

        <!-- 访问权限 -->
        <div class="privacy-section" style="border-radius:0;box-shadow:none;margin-bottom:0;border-bottom:8px solid #F7F5F2;">
          <div class="privacy-section-title">访问权限</div>
          <div class="privacy-item" style="cursor:pointer;" @click="openSelector('home_visibility')">
            <div class="privacy-item-left">
              <div class="privacy-item-title">个人主页可见性</div>
              <div class="privacy-item-desc">控制谁可以访问你的收藏主页</div>
            </div>
            <div class="privacy-item-right">
              <span class="privacy-item-value">{{ getOptionLabel('home_visibility') }}</span>
              <span class="privacy-item-arrow">›</span>
            </div>
          </div>
        </div>

        <!-- 数据展示 -->
        <div class="privacy-section" style="border-radius:0;box-shadow:none;margin-bottom:0;border-bottom:8px solid #F7F5F2;">
          <div class="privacy-section-title">数据展示</div>
          <div class="privacy-item">
            <div class="privacy-item-left">
              <div class="privacy-item-title">藏品总数</div>
              <div class="privacy-item-desc">是否对外展示藏品统计数量</div>
            </div>
            <div class="privacy-item-right">
              <div class="switch" :data-on="settings.show_total" @click="toggleSwitch('show_total')">
                <div class="switch-track"><div class="switch-thumb"></div></div>
              </div>
            </div>
          </div>
          <div class="privacy-item">
            <div class="privacy-item-left">
              <div class="privacy-item-title">具体藏品列表</div>
              <div class="privacy-item-desc">是否展示手办明细信息</div>
            </div>
            <div class="privacy-item-right">
              <div class="switch" :data-on="settings.show_figures" @click="toggleSwitch('show_figures')">
                <div class="switch-track"><div class="switch-thumb"></div></div>
              </div>
            </div>
          </div>
          <div class="privacy-item">
            <div class="privacy-item-left">
              <div class="privacy-item-title">标签云</div>
              <div class="privacy-item-desc">是否展示手办标签偏好信息</div>
            </div>
            <div class="privacy-item-right">
              <div class="switch" :data-on="settings.show_tags" @click="toggleSwitch('show_tags')">
                <div class="switch-track"><div class="switch-thumb"></div></div>
              </div>
            </div>
          </div>
          <div class="privacy-item">
            <div class="privacy-item-left">
              <div class="privacy-item-title">动态流</div>
              <div class="privacy-item-desc">买入/卖出等操作记录是否对外展示</div>
            </div>
            <div class="privacy-item-right">
              <div class="switch" :data-on="settings.show_feed" @click="toggleSwitch('show_feed')">
                <div class="switch-track"><div class="switch-thumb"></div></div>
              </div>
            </div>
          </div>
          <div class="privacy-item">
            <div class="privacy-item-left">
              <div class="privacy-item-title">主页资产金额</div>
              <div class="privacy-item-desc">包含成本价、市值、盈亏等敏感数据</div>
            </div>
            <div class="privacy-item-right">
              <div class="switch" :data-on="settings.show_asset" @click="toggleSwitch('show_asset')">
                <div class="switch-track"><div class="switch-thumb"></div></div>
              </div>
            </div>
          </div>
        </div>

        <!-- 分享设置 -->
        <div class="privacy-section" style="border-radius:0;box-shadow:none;margin-bottom:0;">
          <div class="privacy-section-title">分享设置</div>
          <div class="privacy-item" style="cursor:pointer;" @click="openSelector('poster_level')">
            <div class="privacy-item-left">
              <div class="privacy-item-title">海报展示数据</div>
              <div class="privacy-item-desc">控制分享海报中展示的内容粒度</div>
            </div>
            <div class="privacy-item-right">
              <span class="privacy-item-value">{{ getOptionLabel('poster_level') }}</span>
              <span class="privacy-item-arrow">›</span>
            </div>
          </div>
          <div class="privacy-item">
            <div class="privacy-item-left">
              <div class="privacy-item-title">二维码域名/IP</div>
              <div class="privacy-item-desc">海报二维码扫码后跳转的地址，留空使用自动检测</div>
            </div>
            <div class="privacy-item-right" style="flex:1;max-width:200px;">
              <input
                v-model="settings.share_domain"
                class="domain-input"
                placeholder="如 192.168.1.100:25600"
              />
            </div>
          </div>
        </div>

      </div>
      <div class="modal-footer" style="border-top:none;padding-top:0;">
        <button class="save-btn" @click="handleSave" :disabled="saving">
          {{ saving ? '保存中...' : '保存设置' }}
        </button>
      </div>
    </div>

    <!-- Selector Modal -->
    <div v-if="selectorKey" class="modal-overlay show select-overlay" @click="closeSelector">
      <div class="modal" style="max-width:360px;" @click.stop>
        <div class="modal-header">
          <div class="modal-title">{{ selectorTitle }}</div>
          <div class="modal-close" @click="closeSelector">×</div>
        </div>
        <div class="modal-body" style="padding:0;">
          <div
            v-for="opt in selectorOptions"
            :key="opt.value"
            class="selector-option"
            :class="{ 'is-disabled': opt.disabled }"
            @click="selectOption(opt.value)"
          >
            <div class="selector-radio" :class="{ selected: opt.value === settings[selectorKey] }"></div>
            <div class="selector-text">
              <div class="selector-title-row">
                <span class="selector-title">{{ opt.label }}</span>
                <span v-if="opt.disabled && opt.disabledTip" class="selector-tip">{{ opt.disabledTip }}</span>
              </div>
              <div class="selector-desc">{{ opt.desc }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { usePrivacy } from './composables/usePrivacy.js'

export default {
  name: 'PrivacySettings',
  props: {
    visible: Boolean
  },
  emits: ['update:visible', 'saved'],
  setup(props, { emit }) {
    const { loading, saving, settings, loadSettings, saveSettings, updateField, getSelector, getOptionLabel } = usePrivacy()

    const selectorKey = ref(null)

    const selectorTitle = computed(() => {
      if (!selectorKey.value) return ''
      const s = getSelector(selectorKey.value)
      return s ? s.title : ''
    })
    const selectorOptions = computed(() => {
      if (!selectorKey.value) return []
      const s = getSelector(selectorKey.value)
      return s ? s.options : []
    })

    watch(() => props.visible, (v) => {
      if (v) loadSettings()
    })

    function close() {
      emit('update:visible', false)
    }

    function toggleSwitch(key) {
      updateField(key, !settings[key])
    }

    function openSelector(key) {
      selectorKey.value = key
    }

    function closeSelector() {
      selectorKey.value = null
    }

    function selectOption(value) {
      if (!selectorKey.value) return
      const opts = selectorOptions.value || []
      const opt = opts.find(o => o.value === value)
      if (opt && opt.disabled) {
        ElMessage.info((opt.disabledTip || '该选项暂未开放') + '，暂不可选')
        return
      }
      updateField(selectorKey.value, value)
      closeSelector()
    }

    async function handleSave() {
      const ok = await saveSettings()
      if (ok) {
        emit('saved')
        close()
      }
    }

    return {
      settings, loading, saving,
      getOptionLabel, toggleSwitch, openSelector, closeSelector, selectOption,
      selectorKey, selectorTitle, selectorOptions, close, handleSave
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
.modal-overlay.select-overlay { z-index: 210; }
.modal {
  background: #fff; border-radius: 12px; width: 100%; max-width: 480px;
  max-height: 90vh; overflow-y: auto;
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
.modal-footer { padding: 12px 20px 20px; display: flex; justify-content: flex-end; gap: 10px; }

.privacy-section {
  background: #fff; border-radius: 12px; padding: 20px;
  margin-bottom: 16px;
}
.privacy-section-title {
  font-size: 14px; font-weight: 600; color: #666; margin-bottom: 14px;
  display: flex; align-items: center; gap: 6px;
}
.privacy-section-title::before {
  content: ""; display: inline-block; width: 3px; height: 14px;
  background: #C49A6C; border-radius: 2px;
}
.privacy-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 0; border-bottom: 1px solid #EBE8E4;
}
.privacy-item:last-child { border-bottom: none; padding-bottom: 0; }
.privacy-item-left { flex: 1; }
.privacy-item-title { font-size: 14px; font-weight: 500; margin-bottom: 3px; }
.privacy-item-desc { font-size: 12px; color: #999; }
.privacy-item-right { display: flex; align-items: center; gap: 10px; }
.privacy-item-value { font-size: 13px; color: #666; }
.privacy-item-arrow { font-size: 14px; color: #999; }

.switch { cursor: pointer; }
.switch-track {
  width: 44px; height: 24px; border-radius: 12px;
  background: #E0E0E0; position: relative; transition: background 0.3s;
}
.switch[data-on="true"] .switch-track { background: #C49A6C; }
.switch-thumb {
  width: 20px; height: 20px; border-radius: 50%; background: #fff;
  position: absolute; top: 2px; left: 2px;
  transition: transform 0.3s; box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}
.switch[data-on="true"] .switch-thumb { transform: translateX(20px); }

.selector-option {
  padding: 14px 16px; border-bottom: 1px solid #EBE8E4;
  cursor: pointer; display: flex; align-items: center; gap: 12px; transition: background 0.2s;
}
.selector-option:last-child { border-bottom: none; }
.selector-option:hover { background: #FAFAFA; }
.selector-option.is-disabled { cursor: not-allowed; opacity: 0.55; }
.selector-option.is-disabled:hover { background: transparent; }
.selector-title-row { display: flex; align-items: center; gap: 8px; }
.selector-tip {
  display: inline-block;
  font-size: 11px;
  color: #fff;
  background: #B8B8B8;
  padding: 1px 6px;
  border-radius: 8px;
  line-height: 1.4;
}
.selector-radio {
  width: 18px; height: 18px; border-radius: 50%; border: 2px solid #EBE8E4;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.selector-radio.selected { border-color: #C49A6C; }
.selector-radio.selected::after {
  content: ""; width: 10px; height: 10px; border-radius: 50%; background: #C49A6C;
}
.selector-text { flex: 1; }
.selector-title { font-size: 14px; color: #1F1F1F; }
.selector-desc { font-size: 12px; color: #999; margin-top: 2px; }

.save-btn {
  width: 100%; padding: 12px 0; text-align: center;
  background: #C49A6C; border: none; border-radius: 8px;
  font-size: 15px; font-weight: 600; color: #fff; cursor: pointer;
  transition: background 0.2s; margin-top: 8px;
}
.save-btn:hover { background: #B08A5C; }
.save-btn:disabled { background: #E0E0E0; cursor: not-allowed; }

.domain-input {
  width: 100%; padding: 6px 10px; border: 1px solid #EBE8E4; border-radius: 6px;
  font-size: 13px; color: #1F1F1F; outline: none; transition: border-color 0.2s;
  background: #FAFAFA;
}
.domain-input:focus { border-color: #C49A6C; background: #fff; }
.domain-input::placeholder { color: #999; }
</style>
