<template>
  <el-dialog
    :model-value="visible"
    :title="isEditing ? '编辑愿望' : '手动添加愿望'"
    width="720px"
    :close-on-click-modal="false"
    @close="$emit('close')"
  >
    <!-- 基础信息 -->
    <div class="form-section">
      <div class="form-group">
        <label class="form-label">手办名称 (name) <span class="required">*</span></label>
        <input v-model="form.name" type="text" class="form-input" placeholder="请输入手办名称" />
      </div>
      <div class="form-group">
        <label class="form-label">日文名称 (japanese_name)</label>
        <input v-model="form.japanese_name" type="text" class="form-input" placeholder="日文原名" />
      </div>
    </div>

    <div class="form-row">
      <div class="form-group">
        <label class="form-label">官方定价 (price)</label>
        <input v-model.number="form.price" type="number" class="form-input" placeholder="0.00" />
      </div>
      <div class="form-group">
        <label class="form-label">定价币种 (currency)</label>
        <select v-model="form.currency" class="form-select">
          <option value="CNY">CNY</option>
          <option value="JPY">JPY</option>
          <option value="USD">USD</option>
        </select>
      </div>
    </div>

    <div class="form-row">
      <div class="form-group">
        <label class="form-label">市场价 (market_price)</label>
        <input v-model.number="form.market_price" type="number" class="form-input" placeholder="0.00" />
      </div>
      <div class="form-group">
        <label class="form-label">发售日期</label>
        <el-date-picker v-model="form.release_date" type="date" placeholder="选择发售日期" value-format="YYYY-MM-DD" style="width: 100%;" />
      </div>
    </div>

    <div class="form-row">
      <div class="form-group">
        <label class="form-label">厂商 (manufacturer)</label>
        <el-select v-model="form.manufacturer" allow-create filterable placeholder="请选择" style="width: 100%">
          <el-option v-for="m in manufacturers" :key="m" :value="m" :label="m" />
        </el-select>
      </div>
      <div class="form-group">
        <label class="form-label">比例 (scale)</label>
        <el-select v-model="form.scale" allow-create filterable placeholder="请选择" style="width: 100%">
          <el-option v-for="s in scales" :key="s" :value="s" :label="s" />
        </el-select>
      </div>
    </div>

    <div class="form-row">
      <div class="form-group">
        <label class="form-label">作品出处 (work)</label>
        <input v-model="form.work" type="text" class="form-input" placeholder="动漫/游戏/原创" />
      </div>
      <div class="form-group">
        <label class="form-label">材质 (material)</label>
        <input v-model="form.material" type="text" class="form-input" placeholder="PVC, ABS, 树脂..." />
      </div>
    </div>

    <div class="form-row">
      <div class="form-group">
        <label class="form-label">涂装师 (painting)</label>
        <input v-model="form.painting" type="text" class="form-input" placeholder="" />
      </div>
      <div class="form-group">
        <label class="form-label">原画作者 (original_art)</label>
        <input v-model="form.original_art" type="text" class="form-input" placeholder="" />
      </div>
    </div>

    <div class="form-section">
      <div class="form-group">
        <label class="form-label">图片链接 (images)</label>
        <input v-model="form.images" type="text" class="form-input" placeholder="https://...（多个用逗号分隔）" />
      </div>
      <div class="form-group">
        <label class="form-label">来源链接</label>
        <input v-model="form.source_url" type="text" class="form-input" placeholder="商品详情页URL" />
      </div>
      <!-- 2026-07-29 重构：复用手办库 FormTagsTab 组件，保持 UI 与契约一致 -->
      <FormTagsTab
        :figure="form"
        :tag-store="tagStore"
        @update:figure="onFigureUpdate"
      />
    </div>

    <div class="form-section">
      <div class="form-group">
        <label class="form-label">备注</label>
        <textarea v-model="form.note" class="form-textarea" placeholder="记录一些购买注意事项..."></textarea>
      </div>
    </div>

    <template #footer>
      <el-button @click="$emit('close')">取消</el-button>
      <el-button type="primary" :loading="saving" @click="$emit('save')">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { wishlistApi } from '../api/wishlistApi'
import { useTagStore } from '../../../store/index'
import FormTagsTab from '../../Figures/components/form/FormTagsTab.vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  isEditing: { type: Boolean, default: false },
  form: { type: Object, required: true },
  saving: { type: Boolean, default: false }
})
const emit = defineEmits(['close', 'save'])

const manufacturers = ref([])
const scales = ref([])
const tagStore = useTagStore()

const onFigureUpdate = (val) => {
  // 2026-07-29 重构：FormTagsTab 通过 update:figure 回传整个 form 对象，需同步到外部 props.form
  Object.assign(props.form, val)
}

onMounted(async () => {
  try {
    const mfrRes = await wishlistApi.manufacturers()
    manufacturers.value = mfrRes || []
  } catch {
    manufacturers.value = []
  }
  try {
    const scaleRes = await wishlistApi.scales()
    scales.value = scaleRes || []
  } catch {
    scales.value = []
  }
  // 2026-07-29 重构：标签下拉需 tagStore 标签名兜底
  try {
    if (!tagStore.tags || tagStore.tags.length === 0) {
      await tagStore.fetchTags()
    }
  } catch {
    // 静默失败：标签下拉为空时仍可手动输入
  }
})
</script>

<style scoped>
.form-group { margin-bottom: 16px; }
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}
.form-row .form-group { margin-bottom: 0; }
.form-section { margin-bottom: 16px; }
.form-label {
  display: block;
  margin-bottom: 6px;
  color: #333;
  font-size: 14px;
  font-weight: 500;
}
.required { color: #ff4d4f; }
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
  box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.1);
}
.form-textarea { min-height: 80px; resize: vertical; }
</style>
