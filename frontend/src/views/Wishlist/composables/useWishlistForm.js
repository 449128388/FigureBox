/**
 * useWishlistForm.js - 手动录入 composable
 *
 * 2026-07-29 重构：标签字段从空格分隔字符串（form.tags）改为字符串数组（form.tag_names），
 * 与手办库模块的 FormTagsTab 组件契约保持一致，便于复用同一标签录入 UI
 */
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { wishlistApi } from '../api/wishlistApi'

const initialForm = () => ({
  name: '',
  japanese_name: '',
  price: 0,
  currency: 'CNY',
  market_price: 0,
  release_date: '',
  manufacturer: '',
  scale: '',
  work: '',
  material: '',
  painting: '',
  original_art: '',
  images: '',
  source_url: '',
  tag_names: [],
  note: '',
  wishlist_status: 'wish'
})

export function useWishlistForm() {
  const visible = ref(false)
  const isEditing = ref(false)
  const editingId = ref(null)
  const form = reactive(initialForm())
  const saving = ref(false)

  const openForCreate = () => {
    Object.assign(form, initialForm())
    isEditing.value = false
    editingId.value = null
    visible.value = true
  }

  const openForEdit = (item) => {
    Object.assign(form, initialForm())
    form.name = item.name || ''
    form.japanese_name = item.japanese_name || ''
    form.price = item.price || 0
    form.currency = item.currency || 'CNY'
    form.market_price = item.market_price || 0
    form.release_date = item.release_date || ''
    form.manufacturer = item.manufacturer || ''
    form.scale = item.scale || ''
    form.work = item.work || ''
    form.material = item.material || ''
    form.painting = item.painting || ''
    form.original_art = item.original_art || ''
    form.images = (item.images || []).join(', ')
    form.source_url = item.source_url || ''
    form.tag_names = Array.isArray(item.tags) ? [...item.tags] : []
    form.note = item.note || ''
    form.wishlist_status = item.status || 'wish'
    isEditing.value = true
    editingId.value = item.id
    visible.value = true
  }

  const close = () => {
    visible.value = false
  }

  const save = async () => {
    if (!form.name.trim()) {
      ElMessage.warning('请输入手办名称')
      return false
    }
    saving.value = true
    try {
      // 2026-07-29 重构：tag_names 已是字符串数组，直接去重后提交
      const tagNames = Array.isArray(form.tag_names)
        ? Array.from(new Set(form.tag_names.filter(t => t && String(t).trim())))
        : []
      const images = (form.images || '').split(/[,\s]+/).filter(Boolean)
      const payload = {
        ...form,
        tag_names: tagNames,
        images
      }
      delete payload.tags
      let result
      if (isEditing.value && editingId.value) {
        result = await wishlistApi.update(editingId.value, payload)
        ElMessage.success('更新成功')
      } else {
        result = await wishlistApi.create(payload)
        ElMessage.success('添加成功')
      }
      close()
      return result
    } catch (e) {
      ElMessage.error(e?.response?.data?.detail || '保存失败')
      return false
    } finally {
      saving.value = false
    }
  }

  return {
    visible, isEditing, form, saving, editingId,
    openForCreate, openForEdit, close, save
  }
}
