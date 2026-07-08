<template>
  <el-dialog
    :model-value="visible"
    :title="isEditing ? '编辑愿望' : '手动添加愿望'"
    width="640px"
    :close-on-click-modal="false"
    @close="$emit('close')"
  >
    <el-form label-width="120px" label-position="right">
      <el-form-item label="手办名称 *" required>
        <el-input v-model="form.name" placeholder="请输入手办名称" />
      </el-form-item>
      <el-form-item label="日文名称">
        <el-input v-model="form.japanese_name" placeholder="日文原名" />
      </el-form-item>

      <el-form-item label="官方定价">
        <el-input v-model.number="form.price" type="number" placeholder="0.00" />
      </el-form-item>
      <el-form-item label="定价币种">
        <el-select v-model="form.currency" style="width: 100%">
          <el-option value="CNY" label="CNY" />
          <el-option value="JPY" label="JPY" />
          <el-option value="USD" label="USD" />
          <el-option value="EUR" label="EUR" />
        </el-select>
      </el-form-item>

      <el-form-item label="市场价">
        <el-input v-model.number="form.market_price" type="number" placeholder="0.00" />
      </el-form-item>
      <el-form-item label="发售日期">
        <el-date-picker
          v-model="form.release_date"
          type="date"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item label="厂商">
        <el-select v-model="form.manufacturer" allow-create filterable placeholder="请选择" style="width: 100%">
          <el-option value="Alter" label="Alter" />
          <el-option value="GSC" label="GSC" />
          <el-option value="Max Factory" label="Max Factory" />
          <el-option value="Native" label="Native" />
          <el-option value="BINDing" label="BINDing" />
        </el-select>
      </el-form-item>
      <el-form-item label="比例">
        <el-select v-model="form.scale" allow-create filterable placeholder="请选择" style="width: 100%">
          <el-option value="1/1" label="1/1" />
          <el-option value="1/4" label="1/4" />
          <el-option value="1/6" label="1/6" />
          <el-option value="1/7" label="1/7" />
          <el-option value="1/8" label="1/8" />
          <el-option value="1/12" label="1/12" />
          <el-option value="Non" label="Non" />
        </el-select>
      </el-form-item>

      <el-form-item label="作品出处">
        <el-input v-model="form.work" placeholder="动漫/游戏/原创" />
      </el-form-item>
      <el-form-item label="材质">
        <el-input v-model="form.material" placeholder="PVC, ABS, 树脂..." />
      </el-form-item>

      <el-form-item label="涂装师">
        <el-input v-model="form.painting" />
      </el-form-item>
      <el-form-item label="原画作者">
        <el-input v-model="form.original_art" />
      </el-form-item>

      <el-form-item label="图片链接">
        <el-input v-model="form.images" placeholder="https://...（多个用逗号分隔）" />
      </el-form-item>
      <el-form-item label="来源链接">
        <el-input v-model="form.source_url" placeholder="商品详情页URL" />
      </el-form-item>
      <el-form-item label="标签">
        <el-input v-model="form.tags" placeholder="花嫁 婚纱 限定（用空格分隔）" />
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="form.wishlist_status" style="width: 100%">
          <el-option value="wish" label="愿望中" />
          <el-option value="released" label="已发售" />
          <el-option value="purchased" label="已购买" />
          <el-option value="cancelled" label="已取消" />
        </el-select>
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="form.note" type="textarea" :rows="3" placeholder="记录一些购买注意事项..." />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="$emit('close')">取消</el-button>
      <el-button type="primary" :loading="saving" @click="onSave">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { useWishlistForm } from '../composables/useWishlistForm'

const props = defineProps({
  visible: { type: Boolean, default: false },
  isEditing: { type: Boolean, default: false },
  form: { type: Object, required: true },
  saving: { type: Boolean, default: false }
})
const emit = defineEmits(['close', 'save'])

const onSave = () => {
  emit('save')
}
</script>

<style scoped>
.el-form-item { margin-bottom: 14px; }
</style>
