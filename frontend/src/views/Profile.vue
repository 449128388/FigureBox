<template>
  <TopHeader />

  <div class="profile-page">
    <!-- Sidebar -->
    <aside class="profile-sidebar">
      <div
        v-for="item in sidebarItems"
        :key="item.id"
        class="sidebar-item"
        :class="{ active: activePanel === item.id }"
        @click="switchPanel(item.id)"
      >
        <span class="sidebar-icon" v-html="item.icon"></span>
        <span>{{ item.label }}</span>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="profile-main">
      <!-- 基本资料 -->
      <div class="panel" :class="{ active: activePanel === 'panel-basic' }">
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
                <input type="text" :value="userStore.profile?.id || userStore.currentUser?.id || ''" readonly>
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
            <button class="btn btn-primary" @click="saveBasic">保存</button>
          </div>
        </div>
      </div>

      <!-- 头像设置 -->
      <div class="panel" :class="{ active: activePanel === 'panel-avatar' }">
        <div class="panel-header">头像设置</div>
        <div class="panel-body">
          <div class="avatar-section">
            <div class="avatar-preview-box">
              <div class="label">当前头像</div>
              <img :src="avatarSrc" class="avatar-large" alt="当前头像">
              <br>
              <a class="avatar-change-link" @click="triggerAvatarInput">更换头像</a>
              <input type="file" id="avatar-input" ref="avatarInput" accept="image/*" style="display:none" @change="previewAvatar">
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
            <button class="btn btn-primary" @click="saveAvatar">保存</button>
          </div>
        </div>
      </div>

      <!-- 隐私设置 -->
      <div class="panel" :class="{ active: activePanel === 'panel-privacy' }">
        <div class="panel-header">隐私设置</div>
        <div class="panel-body" style="padding: 20px 28px 28px;">
          <div class="privacy-section">
            <div class="privacy-section-title">访问权限</div>
            <div class="privacy-item" @click="showHomeVisibility">
              <div class="privacy-item-info">
                <div class="privacy-item-title">个人主页可见性</div>
                <div class="privacy-item-desc">控制谁可以访问你的收藏主页</div>
              </div>
              <div class="privacy-link">
                {{ homeVisibilityText }}
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
              </div>
            </div>
          </div>
          <div class="privacy-section">
            <div class="privacy-section-title">数据展示</div>
            <div class="privacy-item" @click="togglePrivacy('show_total')">
              <div class="privacy-item-info">
                <div class="privacy-item-title">藏品总数</div>
                <div class="privacy-item-desc">是否对外展示藏品统计数量</div>
              </div>
              <div class="toggle-v2" :class="{ active: privacySettings.show_total }"></div>
            </div>
            <div class="privacy-item" @click="togglePrivacy('show_figures')">
              <div class="privacy-item-info">
                <div class="privacy-item-title">具体藏品列表</div>
                <div class="privacy-item-desc">是否展示手办明细信息</div>
              </div>
              <div class="toggle-v2" :class="{ active: privacySettings.show_figures }"></div>
            </div>
            <div class="privacy-item" @click="togglePrivacy('show_tags')">
              <div class="privacy-item-info">
                <div class="privacy-item-title">标签云</div>
                <div class="privacy-item-desc">是否展示手办标签偏好信息</div>
              </div>
              <div class="toggle-v2" :class="{ active: privacySettings.show_tags }"></div>
            </div>
            <div class="privacy-item" @click="togglePrivacy('show_feed')">
              <div class="privacy-item-info">
                <div class="privacy-item-title">动态流</div>
                <div class="privacy-item-desc">买入卖出等操作记录是否对外展示</div>
              </div>
              <div class="toggle-v2" :class="{ active: privacySettings.show_feed }"></div>
            </div>
            <div class="privacy-item" @click="togglePrivacy('show_asset')">
              <div class="privacy-item-info">
                <div class="privacy-item-title">主页资产金额</div>
                <div class="privacy-item-desc">包含成本价、市值、盈亏等敏感数据</div>
              </div>
              <div class="toggle-v2" :class="{ active: privacySettings.show_asset }"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 推送设置 -->
      <div class="panel" :class="{ active: activePanel === 'panel-push' }">
        <div class="panel-header">推送设置</div>
        <div class="panel-body">
          <div class="setting-group">
            <div class="switch-row">
              <div>
                <div class="switch-label">尾款到期提醒</div>
                <div class="switch-hint">手办尾款支付截止前 3 天推送通知</div>
              </div>
              <div class="toggle" :class="{ active: toggles.push_balance_remind }" @click="toggleSwitch('push_balance_remind')"></div>
            </div>
            <div class="switch-row">
              <div>
                <div class="switch-label">价格预警推送</div>
                <div class="switch-hint">关注的手办市场价达到设定阈值时通知</div>
              </div>
              <div class="toggle" :class="{ active: toggles.push_price_alert }" @click="toggleSwitch('push_price_alert')"></div>
            </div>
            <div class="switch-row">
              <div>
                <div class="switch-label">系统公告</div>
                <div class="switch-hint">FigureBox 功能更新与维护通知</div>
              </div>
              <div class="toggle" :class="{ active: toggles.push_system_notice }" @click="toggleSwitch('push_system_notice')"></div>
            </div>
            <div class="switch-row">
              <div>
                <div class="switch-label">邮件周报</div>
                <div class="switch-hint">每周一发送资产收益周报至绑定邮箱</div>
              </div>
              <div class="toggle" :class="{ active: toggles.push_weekly_report }" @click="toggleSwitch('push_weekly_report')"></div>
            </div>
          </div>
          <div class="form-actions">
            <button class="btn btn-primary" @click="saveSettings('push')">保存</button>
          </div>
        </div>
      </div>

      <!-- 账号安全 -->
      <div class="panel" :class="{ active: activePanel === 'panel-security' }">
        <div class="panel-header">账号安全</div>
        <div class="panel-body">
          <div class="security-list">
            <div class="security-item">
              <div class="security-info">
                <div class="security-title">邮箱地址</div>
                <div class="security-desc">{{ userStore.currentUser?.email || '未设置' }}</div>
              </div>
              <button class="btn btn-outline btn-sm" disabled>修改邮箱</button>
            </div>
            <div class="security-item">
              <div class="security-info">
                <div class="security-title">登录密码</div>
                <div class="security-desc">已设置密码</div>
              </div>
              <button class="btn btn-outline btn-sm" disabled>修改密码</button>
            </div>
            <div class="security-item">
              <div class="security-info">
                <div class="security-title">用户名</div>
                <div class="security-desc">{{ userStore.currentUser?.username || '' }}</div>
              </div>
              <button class="btn btn-outline btn-sm" disabled>修改用户名</button>
            </div>
          </div>
        </div>
      </div>

      <!-- MinIO 设置 -->
      <div class="panel" :class="{ active: activePanel === 'panel-minio' }">
        <div class="panel-header">MinIO 图床设置</div>
        <div class="panel-body">
          <div class="minio-status-card" :class="minioStatusClass">
            <!-- 未知状态：圆形感叹号 -->
            <svg v-if="minioStatusClass === 'warning'" class="status-icon" viewBox="0 0 24 24" fill="none" stroke-width="2">
              <circle cx="12" cy="12" r="10" :stroke="minioStatusIconColor"/>
              <line x1="12" y1="8" x2="12" y2="13" :stroke="minioStatusIconColor" stroke-linecap="round"/>
              <circle cx="12" cy="16.5" r="1" :fill="minioStatusIconColor"/>
            </svg>
            <!-- 成功/失败状态：对勾 -->
            <svg v-else class="status-icon" viewBox="0 0 24 24" fill="none" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" :stroke="minioStatusIconColor"/>
              <polyline points="22 4 12 14.01 9 11.01" :stroke="minioStatusIconColor"/>
            </svg>
            <div class="status-text">
              <div>{{ minioStatusText }}</div>
              <div class="detail">{{ minioStatusDetail }}</div>
            </div>
          </div>

          <div class="form-row">
            <label class="form-label">服务器地址</label>
            <div class="form-control">
              <div class="input-wrap medium">
                <input type="url" v-model="minioConfig.endpoint" placeholder="http://localhost:9000">
              </div>
              <div class="form-hint">MinIO API 端点地址，包含协议与端口</div>
            </div>
          </div>

          <div class="form-row">
            <label class="form-label">Access Key</label>
            <div class="form-control">
              <div class="input-wrap medium">
                <input type="text" v-model="minioConfig.access_key" placeholder="Access Key">
              </div>
            </div>
          </div>

          <div class="form-row">
            <label class="form-label">Secret Key</label>
            <div class="form-control">
              <div class="input-wrap medium">
                <input type="text" v-model="minioConfig.secret_key" placeholder="Secret Key">
              </div>
              <div class="form-hint">密钥仅保存在本地浏览器，不会上传至 FigureBox 服务器</div>
            </div>
          </div>

          <div class="form-row">
            <label class="form-label">Bucket 名称</label>
            <div class="form-control">
              <div class="input-wrap medium">
                <input type="text" v-model="minioConfig.bucket" placeholder="Bucket 名称">
              </div>
            </div>
          </div>

          <div class="form-row">
            <label class="form-label">图片访问域名</label>
            <div class="form-control">
              <div class="input-wrap medium">
                <input type="url" v-model="minioConfig.public_url" placeholder="http://localhost:25620/figurebox-images">
              </div>
              <div class="form-hint">前端拼接图片 URL 的基地址，通常与服务器地址一致</div>
            </div>
          </div>

          <div class="form-row">
            <label class="form-label">安全连接</label>
            <div class="form-control">
              <div class="radio-group">
                <label class="radio-item"><input type="radio" v-model="minioConfig.secure" :value="false"> HTTP（内网）</label>
                <label class="radio-item"><input type="radio" v-model="minioConfig.secure" :value="true"> HTTPS（公网）</label>
              </div>
            </div>
          </div>

          <div class="form-row">
            <label class="form-label">区域 Region</label>
            <div class="form-control">
              <div class="input-wrap small">
                <input type="text" v-model="minioConfig.region" placeholder="us-east-1">
              </div>
              <div class="form-hint">一般使用默认即可，MinIO 单节点通常填 us-east-1</div>
            </div>
          </div>

          <div class="form-actions" style="margin-top:24px;">
            <button class="btn btn-success" @click="testMinIOConnection" :disabled="testingConnection">
              <span v-if="testingConnection">测试中...</span>
              <span v-else>测试连接</span>
            </button>
            <button class="btn btn-primary" @click="saveMinIOConfig">保存配置</button>
          </div>
        </div>
      </div>

      <!-- 超时登出设置 -->
      <div class="panel" :class="{ active: activePanel === 'panel-timeout' }">
        <div class="panel-header">超时登出设置</div>
        <div class="panel-body">
          <div class="timeout-info-card">
            <svg class="timeout-info-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
            <div class="timeout-info-text">
              <strong>安全提示</strong>：当页面在设定时间内无任何操作（鼠标移动、点击、键盘输入），系统将自动退出登录状态，防止他人未经授权访问你的资产数据。该设置仅对当前设备生效，建议公共场合使用较短时长。
            </div>
          </div>

          <div class="form-row">
            <label class="form-label">超时时间</label>
            <div class="form-control">
              <div class="timeout-options">
                <label class="timeout-option" :class="{ selected: timeoutConfig.timeout_minutes === 30 }" @click="selectTimeout(30)">
                  <input type="radio" name="timeout" :value="30" :checked="timeoutConfig.timeout_minutes === 30">
                  <div class="timeout-option-text">
                    <div class="timeout-option-label">30分钟</div>
                    <div class="timeout-option-desc">适合公共场所或多人共用设备</div>
                  </div>
                </label>
                <label class="timeout-option" :class="{ selected: timeoutConfig.timeout_minutes === 60 }" @click="selectTimeout(60)">
                  <input type="radio" name="timeout" :value="60" :checked="timeoutConfig.timeout_minutes === 60">
                  <div class="timeout-option-text">
                    <div class="timeout-option-label">1小时</div>
                    <div class="timeout-option-desc">兼顾安全与便利的推荐设置</div>
                  </div>
                </label>
                <label class="timeout-option" :class="{ selected: timeoutConfig.timeout_minutes === 120 }" @click="selectTimeout(120)">
                  <input type="radio" name="timeout" :value="120" :checked="timeoutConfig.timeout_minutes === 120">
                  <div class="timeout-option-text">
                    <div class="timeout-option-label">2小时</div>
                    <div class="timeout-option-desc">适合办公室等相对安全的环境</div>
                  </div>
                </label>
                <label class="timeout-option" :class="{ selected: timeoutConfig.timeout_minutes === 180 }" @click="selectTimeout(180)">
                  <input type="radio" name="timeout" :value="180" :checked="timeoutConfig.timeout_minutes === 180">
                  <div class="timeout-option-text">
                    <div class="timeout-option-label">3 小时</div>
                    <div class="timeout-option-desc">适合家庭个人电脑等私密环境</div>
                  </div>
                </label>
                <label class="timeout-option" :class="{ selected: timeoutConfig.timeout_minutes === 0 }" @click="selectTimeout(0)">
                  <input type="radio" name="timeout" :value="0" :checked="timeoutConfig.timeout_minutes === 0">
                  <div class="timeout-option-text">
                    <div class="timeout-option-label">从不超时 <span class="not-recommend">（不推荐）</span></div>
                    <div class="timeout-option-desc">保持永久登录，仅在手动退出时失效（不推荐）</div>
                  </div>
                </label>
              </div>
            </div>
          </div>

          <div class="form-row">
            <label class="form-label">倒计时提醒</label>
            <div class="form-control">
              <div class="radio-group">
                <label class="radio-item"><input type="radio" v-model="timeoutConfig.timeout_warning" :value="true"> 超时前 30 秒弹窗提醒</label>
                <label class="radio-item"><input type="radio" v-model="timeoutConfig.timeout_warning" :value="false"> 直接登出，不提醒</label>
              </div>
              <div class="form-hint">开启提醒后可在弹窗中点击"保持登录"延长当前会话</div>
            </div>
          </div>

          <div class="form-actions">
            <button class="btn btn-primary" @click="saveTimeoutConfig" :disabled="savingTimeout">
              <span v-if="savingTimeout">保存中...</span>
              <span v-else>保存设置</span>
            </button>
          </div>
        </div>
      </div>

      <!-- 账号注销 -->
      <div class="panel" :class="{ active: activePanel === 'panel-delete' }">
        <div class="panel-header">账号注销</div>
        <div class="panel-body">
          <div class="danger-zone">
            <div class="danger-zone-title">⚠️ 注销账号</div>
            <div class="danger-zone-desc">
              注销后，你的个人资料、收藏柜数据、交易记录、收益统计等所有信息将被永久删除且无法恢复。<br>
              请确保已备份重要数据，并确认当前账号无未完成的尾款订单或纠纷。
            </div>
            <button class="btn btn-danger" @click="showDeleteConfirm">申请注销账号</button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import TopHeader from '../components/TopHeader.vue'
import { useProfile } from './Profile/composables/useProfile'
import { useUserStore } from '../store'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from '../axios'

export default {
  name: 'Profile',
  components: { TopHeader },
  setup() {
    const profile = useProfile()
    const userStore = useUserStore()

    const yearRange = computed(() => {
      const y = new Date().getFullYear()
      return Array.from({ length: 100 }, (_, i) => y - i)
    })

    const avatarSrc = ref('')
    const selectedAvatarFile = ref(null)

    const sidebarItems = [
      { id: 'panel-basic', label: '基本资料', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>' },
      { id: 'panel-avatar', label: '头像设置', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>' },
      { id: 'panel-privacy', label: '隐私设置', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>' },
      { id: 'panel-push', label: '推送设置', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>' },
      { id: 'panel-security', label: '账号安全', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>' },
      { id: 'panel-minio', label: 'MinIO 设置', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/><path d="M15 12l3-3"/><path d="M9 6l3-3"/></svg>' },
      { id: 'panel-timeout', label: '超时登出', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>' },
      { id: 'panel-delete', label: '账号注销', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>' },
    ]

    const triggerAvatarInput = () => {
      document.getElementById('avatar-input')?.click()
    }

    const previewAvatar = (e) => {
      const file = e.target.files?.[0]
      if (file) {
        selectedAvatarFile.value = file
        const reader = new FileReader()
        reader.onload = (ev) => { avatarSrc.value = ev.target.result }
        reader.readAsDataURL(file)
      }
    }

    const saveAvatar = async () => {
      if (!selectedAvatarFile.value) {
        ElMessage.warning('请先选择要上传的头像')
        return
      }

      const formData = new FormData()
      formData.append('file', selectedAvatarFile.value)

      try {
        const uploadResponse = await axios.post('/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })

        if (uploadResponse.url) {
          await userStore.updateAvatar(uploadResponse.url)
          ElMessage.success('头像已更新')
        } else {
          ElMessage.error('头像上传失败')
        }
      } catch (error) {
        console.error('头像上传失败:', error)
        ElMessage.error('头像上传失败，请稍后重试')
      }
    }

    const showDeleteConfirm = () => {
      ElMessageBox.confirm(
        '注销后所有数据将永久删除且无法恢复，确认要注销吗？',
        '确认注销账号',
        { confirmButtonText: '确认注销', cancelButtonText: '取消', type: 'warning' }
      ).then(() => {
        ElMessage.info('请联系管理员完成注销流程')
      }).catch(() => {})
    }

    const minioConfig = ref({
      endpoint: '',
      access_key: '',
      secret_key: '',
      bucket: '',
      public_url: '',
      secure: false,
      region: 'us-east-1'
    })

    const minioStatusText = ref('当前连接状态未知')
    const minioStatusDetail = ref('')
    const minioStatusClass = ref('warning')
    const minioStatusIconColor = ref('#faad14')
    const testingConnection = ref(false)

    const savingTimeout = ref(false)

    const timeoutConfig = ref({
      timeout_minutes: 30,
      timeout_warning: true
    })

    const selectTimeout = (minutes) => {
      timeoutConfig.value.timeout_minutes = minutes
    }

    const loadTimeoutConfig = async () => {
      try {
        const response = await axios.get('/timeout/config')
        if (response) {
          timeoutConfig.value = {
            timeout_minutes: response.timeout_minutes ?? 30,
            timeout_warning: response.timeout_warning ?? true
          }
        }
      } catch (error) {
        console.error('加载超时登出配置失败:', error)
      }
    }

    const saveTimeoutConfig = async () => {
      savingTimeout.value = true
      try {
        await axios.put('/timeout/config', {
          timeout_minutes: timeoutConfig.value.timeout_minutes,
          timeout_warning: timeoutConfig.value.timeout_warning
        })
        ElMessage.success('超时登出设置已保存')
      } catch (error) {
        console.error('保存超时登出配置失败:', error)
        ElMessage.error('保存失败，请稍后重试')
      } finally {
        savingTimeout.value = false
      }
    }

    const loadMinIOConfig = async () => {
      try {
        const response = await axios.get('/minio/config')
        if (response) {
          minioConfig.value = {
            endpoint: response.endpoint || '',
            access_key: response.access_key || '',
            secret_key: response.secret_key || '',
            bucket: response.bucket || '',
            public_url: response.public_url || '',
            secure: response.secure || false,
            region: response.region || 'us-east-1'
          }
        }
      } catch (error) {
        console.error('加载 MinIO 配置失败:', error)
      }
    }

    const testMinIOConnection = async () => {
      testingConnection.value = true
      minioStatusText.value = '正在测试连接...'
      minioStatusDetail.value = ''
      minioStatusClass.value = 'warning'
      minioStatusIconColor.value = '#faad14'

      try {
        const response = await axios.post('/minio/test', {
          endpoint: minioConfig.value.endpoint,
          access_key: minioConfig.value.access_key,
          secret_key: minioConfig.value.secret_key,
          bucket: minioConfig.value.bucket,
          secure: minioConfig.value.secure,
          region: minioConfig.value.region
        })

        if (response.success) {
          minioStatusText.value = response.message
          minioStatusDetail.value = `延迟 ${response.latency}ms`
          minioStatusClass.value = ''
          minioStatusIconColor.value = '#52c41a'
          ElMessage.success('MinIO 连接测试成功')
        } else {
          minioStatusText.value = '连接失败'
          minioStatusDetail.value = response.message
          minioStatusClass.value = 'error'
          minioStatusIconColor.value = '#ff4d4f'
          ElMessage.error('MinIO 连接测试失败')
        }
      } catch (error) {
        minioStatusText.value = '连接测试异常'
        minioStatusDetail.value = error.response?.data?.detail || '网络错误'
        minioStatusClass.value = 'error'
        minioStatusIconColor.value = '#ff4d4f'
        ElMessage.error('MinIO 连接测试失败，请稍后重试')
      } finally {
        testingConnection.value = false
      }
    }

    const saveMinIOConfig = async () => {
      try {
        await axios.put('/minio/config', {
          endpoint: minioConfig.value.endpoint,
          access_key: minioConfig.value.access_key,
          secret_key: minioConfig.value.secret_key,
          bucket: minioConfig.value.bucket,
          public_url: minioConfig.value.public_url,
          secure: minioConfig.value.secure,
          region: minioConfig.value.region
        })
        ElMessage.success('MinIO 配置已保存')
      } catch (error) {
        console.error('保存 MinIO 配置失败:', error)
        ElMessage.error('保存失败，请稍后重试')
      }
    }

    onMounted(() => {
      avatarSrc.value = userStore.currentUser?.avatar_url || userStore.profile?.avatar_url || '/imgs/none.jpg'
      loadMinIOConfig()
      loadTimeoutConfig()
    })

    return {
      ...profile,
      sidebarItems,
      years: yearRange,
      avatarSrc,
      triggerAvatarInput,
      previewAvatar,
      saveAvatar,
      showDeleteConfirm,
      minioConfig,
      minioStatusText,
      minioStatusDetail,
      minioStatusClass,
      minioStatusIconColor,
      testingConnection,
      loadMinIOConfig,
      testMinIOConnection,
      saveMinIOConfig,
      timeoutConfig,
      savingTimeout,
      selectTimeout,
      loadTimeoutConfig,
      saveTimeoutConfig
    }
  }
}
</script>

<style scoped>
/* ===== Top Header ===== */
.top-header {
  background: #fff;
  border-bottom: 1px solid #e3e5e7;
  padding: 0 24px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  width: 100%;
  box-sizing: border-box;
}
.logo-area {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 18px;
  font-weight: 700;
  color: #18191c;
}
.logo-area img { width: 32px; height: 32px; border-radius: 8px; }
.header-nav {
  display: flex;
  gap: 24px;
  font-size: 14px;
  color: #61666d;
}
.header-nav a,
.header-nav router-link {
  text-decoration: none;
  color: inherit;
  transition: color 0.2s;
  cursor: pointer;
}
.header-nav a:hover, .header-nav a.active,
.header-nav router-link:hover, .header-nav router-link.active,
.header-nav router-link.router-link-active { color: #00a1d6; }
.header-user {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: #61666d;
}
.header-avatar {
  width: 36px; height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex; align-items: center; justify-content: center;
  color: #fff; font-weight: 600; font-size: 14px;
  cursor: pointer;
}

/* ===== Page Layout ===== */
.profile-page {
  max-width: 960px;
  margin: 24px auto;
  padding: 88px 24px 0;
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

/* Sidebar */
.profile-sidebar {
  width: 180px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  overflow: hidden;
  flex-shrink: 0;
  position: sticky;
  top: 24px;
}
.sidebar-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  font-size: 14px;
  color: #61666d;
  cursor: pointer;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}
.sidebar-item:hover {
  background: #f6f7f8;
  color: #18191c;
}
.sidebar-item.active {
  background: rgba(0, 161, 214, 0.08);
  color: #00a1d6;
  border-left-color: #00a1d6;
  font-weight: 600;
}
.sidebar-icon {
  width: 18px;
  height: 18px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  opacity: 0.8;
}
.sidebar-icon svg {
  width: 18px;
  height: 18px;
}

/* Main */
.profile-main {
  flex: 1;
  min-width: 0;
}
.panel {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  overflow: hidden;
  display: none;
}
.panel.active {
  display: block;
  animation: fadeIn 0.3s ease;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
.panel-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e3e5e7;
  font-size: 18px;
  font-weight: 700;
  color: #18191c;
}
.panel-body { padding: 24px 32px 32px; }

/* Form */
.form-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 24px;
}
.form-label {
  width: 110px;
  text-align: right;
  padding-right: 20px;
  padding-top: 9px;
  font-size: 14px;
  color: #61666d;
  flex-shrink: 0;
  white-space: nowrap;
}
.form-control { flex: 1; min-width: 0; }
.input-wrap { position: relative; max-width: 480px; }
.input-wrap.small { max-width: 200px; }
.input-wrap.large { max-width: 600px; }

input[type="text"], input[type="email"], input[type="password"], input[type="url"],
textarea, select {
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
input:focus, textarea:focus, select:focus {
  border-color: #00a1d6;
  box-shadow: 0 0 0 3px rgba(0, 161, 214, 0.15);
}
input::placeholder, textarea::placeholder { color: #9499a0; }
input:read-only {
  background: #f6f7f8;
  color: #9499a0;
  cursor: default;
}

.char-count {
  position: absolute;
  right: 10px;
  bottom: 9px;
  font-size: 12px;
  color: #9499a0;
  pointer-events: none;
  background: rgba(255,255,255,0.9);
  padding: 0 4px;
  border-radius: 4px;
}
textarea + .char-count { bottom: 10px; }
textarea {
  resize: vertical;
  min-height: 120px;
  line-height: 1.6;
  padding-bottom: 28px;
}
.form-hint { margin-top: 6px; font-size: 12px; color: #9499a0; }

/* Radio */
.radio-group { display: flex; gap: 24px; padding-top: 6px; }
.radio-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #18191c;
  cursor: pointer;
  user-select: none;
}
.radio-item input[type="radio"] {
  appearance: none;
  width: 16px; height: 16px;
  border: 2px solid #c9cdd4;
  border-radius: 50%;
  outline: none;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  padding: 0;
}
.radio-item input[type="radio"]:checked { border-color: #00a1d6; }
.radio-item input[type="radio"]:checked::after {
  content: "";
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  width: 8px; height: 8px;
  background: #00a1d6;
  border-radius: 50%;
}

/* Select */
.select-group { display: flex; gap: 10px; }
.select-group select {
  width: auto;
  min-width: 100px;
  padding-right: 28px;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg width='10' height='6' viewBox='0 0 10 6' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%239499a0' stroke-width='1.5' fill='none' fill-rule='evenodd'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 9px 24px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  outline: none;
  transition: all 0.2s;
}
.btn-primary { background: #00a1d6; color: #fff; }
.btn-primary:hover { background: #008db1; }
.btn-outline {
  background: #fff;
  color: #61666d;
  border: 1px solid #c9cdd4;
}
.btn-outline:hover { border-color: #00a1d6; color: #00a1d6; }
.btn-danger { background: #f25d8e; color: #fff; }
.btn-danger:hover { background: #d94d7a; }
.btn-sm { padding: 6px 16px; font-size: 13px; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.form-actions { margin-top: 8px; padding-left: 130px; display: flex; gap: 16px; }

/* Avatar */
.avatar-section { display: flex; gap: 40px; align-items: flex-start; }
.avatar-preview-box { text-align: center; }
.avatar-preview-box .label { font-size: 13px; color: #9499a0; margin-bottom: 12px; }
.avatar-large {
  width: 200px; height: 200px;
  border-radius: 8px;
  background: #f6f7f8;
  object-fit: cover;
  border: 1px solid #e3e5e7;
}
.avatar-circle {
  width: 100px; height: 100px;
  border-radius: 50%;
  background: #f6f7f8;
  object-fit: cover;
  border: 1px solid #e3e5e7;
}
.avatar-change-link {
  display: inline-block;
  margin-top: 12px;
  color: #00a1d6;
  font-size: 14px;
  cursor: pointer;
  text-decoration: none;
}
.avatar-change-link:hover { text-decoration: underline; }
.avatar-tips {
  margin-top: 24px;
  padding: 12px 16px;
  background: #f6f7f8;
  border-radius: 6px;
  font-size: 12px;
  color: #9499a0;
  line-height: 1.8;
  max-width: 320px;
}

/* Switch */
.setting-group { margin-bottom: 28px; }
.setting-group-title {
  font-size: 15px;
  font-weight: 600;
  color: #18191c;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e3e5e7;
}
.switch-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
}
.switch-label { font-size: 14px; color: #18191c; }
.switch-hint { font-size: 12px; color: #9499a0; margin-top: 2px; }
.toggle {
  position: relative;
  width: 40px;
  height: 22px;
  background: #c9cdd4;
  border-radius: 11px;
  cursor: pointer;
  transition: background 0.3s;
  flex-shrink: 0;
}
.toggle::after {
  content: "";
  position: absolute;
  top: 2px; left: 2px;
  width: 18px; height: 18px;
  background: #fff;
  border-radius: 50%;
  transition: transform 0.3s;
  box-shadow: 0 1px 3px rgba(0,0,0,0.15);
}
.toggle.active { background: #00a1d6; }
.toggle.active::after { transform: translateX(18px); }

/* Security */
.security-list { max-width: 640px; }
.security-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 0;
  border-bottom: 1px solid #e3e5e7;
}
.security-item:last-child { border-bottom: none; }
.security-info { display: flex; flex-direction: column; gap: 4px; }
.security-title { font-size: 14px; font-weight: 600; color: #18191c; }
.security-desc { font-size: 13px; color: #9499a0; }

/* Danger Zone */
.danger-zone {
  margin-top: 32px;
  padding: 24px;
  border: 1px solid #ffd6d6;
  border-radius: 8px;
  background: #fff8f8;
}
.danger-zone-title { font-size: 16px; font-weight: 700; color: #f25d8e; margin-bottom: 8px; }
.danger-zone-desc {
  font-size: 13px;
  color: #61666d;
  margin-bottom: 16px;
  line-height: 1.6;
}

/* ===== Privacy Settings ===== */
.privacy-section {
  margin-bottom: 28px;
}
.privacy-section:last-child {
  margin-bottom: 0;
}
.privacy-section-title {
  font-size: 14px;
  font-weight: 600;
  color: #18191c;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
  padding-left: 8px;
}
.privacy-section-title::before {
  content: "";
  display: inline-block;
  width: 3px;
  height: 14px;
  background: #c9a96e;
  border-radius: 2px;
}

.privacy-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 8px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background 0.15s;
  border-radius: 6px;
}
.privacy-item:hover {
  background: #fafafa;
}
.privacy-item:last-child {
  border-bottom: none;
}

.privacy-item-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.privacy-item-title {
  font-size: 15px;
  font-weight: 500;
  color: #18191c;
}
.privacy-item-desc {
  font-size: 12px;
  color: #9499a0;
}

/* Toggle Switch v2 (Brown/Gold) */
.toggle-v2 {
  position: relative;
  width: 44px;
  height: 24px;
  background: #d8d8d8;
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.3s;
  flex-shrink: 0;
  -webkit-tap-highlight-color: transparent;
}
.toggle-v2::after {
  content: "";
  position: absolute;
  top: 2px; left: 2px;
  width: 20px; height: 20px;
  background: #fff;
  border-radius: 50%;
  transition: transform 0.3s;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}
.toggle-v2.active {
  background: #c9a96e;
}
.toggle-v2.active::after {
  transform: translateX(20px);
}

/* Privacy Link (for visibility setting) */
.privacy-link {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: #9499a0;
  transition: color 0.2s;
}
.privacy-item:hover .privacy-link {
  color: #61666d;
}
.privacy-link svg {
  width: 14px; height: 14px;
}

/* Responsive */
@media (max-width: 900px) {
  .profile-page { flex-direction: column; }
  .profile-sidebar {
    width: 100%;
    position: static;
    display: flex;
    overflow-x: auto;
    gap: 4px;
    padding: 8px;
  }
  .sidebar-item {
    white-space: nowrap;
    border-left: none;
    border-bottom: 3px solid transparent;
  }
  .sidebar-item.active {
    border-left-color: transparent;
    border-bottom-color: #00a1d6;
  }
  .form-row { flex-direction: column; }
  .form-label { text-align: left; width: auto; padding: 0 0 6px; }
  .form-actions { padding-left: 0; }
  .avatar-section { flex-direction: column; align-items: center; }
}

/* ===== MinIO 设置面板 ===== */
.minio-status-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  border-radius: 8px;
  margin-bottom: 24px;
}
.minio-status-card.warning {
  background: #fffbe6;
  border-color: #ffe58f;
}
.minio-status-card.error {
  background: #fff2f0;
  border-color: #ffccc7;
}
.status-icon {
  width: 32px;
  height: 32px;
  flex-shrink: 0;
}
.status-text {
  font-size: 14px;
  color: #52c41a;
  font-weight: 500;
}
.minio-status-card.warning .status-text { color: #faad14; }
.minio-status-card.error .status-text { color: #ff4d4f; }
.status-text .detail {
  font-size: 12px;
  font-weight: normal;
  color: #9499a0;
  margin-top: 2px;
}

.btn-success {
  background: #52c41a;
  color: #fff;
}
.btn-success:hover { background: #389e0d; }
.btn-success:disabled {
  background: #a3d987;
  cursor: not-allowed;
}

/* ===== Timeout Panel ===== */
.timeout-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 480px;
}
.timeout-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border: 1px solid #e3e5e7;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  background: #fff;
}
.timeout-option:hover {
  border-color: #00a1d6;
  background: rgba(0, 161, 214, 0.04);
}
.timeout-option.selected {
  border-color: #00a1d6;
  background: rgba(0, 161, 214, 0.06);
  box-shadow: 0 0 0 3px rgba(0, 161, 214, 0.1);
}
.timeout-option input[type="radio"] {
  appearance: none;
  width: 18px; height: 18px;
  border: 2px solid #c9ccd0;
  border-radius: 50%;
  outline: none;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  flex-shrink: 0;
}
.timeout-option input[type="radio"]:checked {
  border-color: #00a1d6;
}
.timeout-option input[type="radio"]:checked::after {
  content: "";
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  width: 9px; height: 9px;
  background: #00a1d6;
  border-radius: 50%;
}
.timeout-option-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.timeout-option-label {
  font-size: 14px;
  font-weight: 500;
  color: #18191c;
}
.timeout-option-desc {
  font-size: 12px;
  color: #9499a0;
}
.not-recommend {
  color: #ff4d4f;
  font-size: 12px;
  font-weight: 400;
}

.timeout-info-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 20px;
  border-radius: 8px;
  background: #f6f7f8;
  border: 1px solid #e3e5e7;
  margin-bottom: 24px;
  max-width: 640px;
}
.timeout-info-icon {
  width: 20px; height: 20px;
  color: #00a1d6;
  flex-shrink: 0;
  margin-top: 1px;
}
.timeout-info-text {
  font-size: 13px;
  color: #61666d;
  line-height: 1.7;
}
.timeout-info-text strong {
  color: #18191c;
}

.form-actions .btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
</style>
