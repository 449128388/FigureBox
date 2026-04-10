<template>
  <div class="form-overlay" v-if="show" @click.self="$emit('close')">
    <div class="form-container">
      <h3>{{ isEditing ? '编辑手办' : '添加手办' }}</h3>
      <form @submit.prevent="handleSubmit">
        <div class="form-layout">
          <el-tabs type="border-card" :tab-position="'left'" lazy v-model="localActiveTab" ref="formTabs">
            <!-- 基础页面 -->
            <el-tab-pane label="基础" name="basic">
              <template #label>
                <div class="tab-label">
                  <i class="fa-solid fa-home"></i>
                  <span>基础</span>
                </div>
              </template>
              <FormBasicTab
                v-model:figure="localFigure"
                :name-error="nameError"
                :japanese-name-error="japaneseNameError"
                :purchase-method-error="purchaseMethodError"
                @validate-name-input="$emit('validate-name-input')"
                @validate-japanese-name-input="$emit('validate-japanese-name-input')"
                @validate-purchase-method-input="$emit('validate-purchase-method-input')"
                @view-image="$emit('view-image', $event)"
                @remove-image="$emit('remove-image', $event)"
                @file-upload="$emit('file-upload', $event)"
              />
            </el-tab-pane>
            
            <!-- 作者页面 -->
            <el-tab-pane label="作者" name="author">
              <template #label>
                <div class="tab-label">
                  <i class="fa-solid fa-user"></i>
                  <span>作者</span>
                </div>
              </template>
              <FormAuthorTab
                v-model:figure="localFigure"
                :painting-error="paintingError"
                :original-art-error="originalArtError"
                :work-error="workError"
                @validate-painting-input="$emit('validate-painting-input')"
                @validate-original-art-input="$emit('validate-original-art-input')"
                @validate-work-input="$emit('validate-work-input')"
              />
            </el-tab-pane>
            
            <!-- 标签页面 -->
            <el-tab-pane label="标签" name="tags">
              <template #label>
                <div class="tab-label">
                  <i class="fa-solid fa-tags"></i>
                  <span>标签</span>
                </div>
              </template>
              <FormTagsTab
                v-model:figure="localFigure"
                :tag-store="tagStore"
                @tag-change="$emit('tag-change', $event)"
              />
            </el-tab-pane>
            
            <!-- 规格页面 -->
            <el-tab-pane label="规格" name="specs">
              <template #label>
                <div class="tab-label">
                  <i class="fa-solid fa-ruler"></i>
                  <span>规格</span>
                </div>
              </template>
              <FormSpecsTab
                v-model:figure="localFigure"
                :manufacturer-error="manufacturerError"
                :scale-error="scaleError"
                :material-error="materialError"
                :size-error="sizeError"
                @validate-manufacturer-input="$emit('validate-manufacturer-input')"
                @validate-scale-input="$emit('validate-scale-input')"
                @validate-material-input="$emit('validate-material-input')"
                @validate-size-input="$emit('validate-size-input')"
              />
            </el-tab-pane>
          </el-tabs>
        </div>
        
        <div class="form-actions">
          <el-button class="btn-cancel" @click="$emit('close')">取消</el-button>
          <el-button class="btn-submit" type="primary" native-type="submit">保存</el-button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import FormBasicTab from './form/FormBasicTab.vue'
import FormAuthorTab from './form/FormAuthorTab.vue'
import FormTagsTab from './form/FormTagsTab.vue'
import FormSpecsTab from './form/FormSpecsTab.vue'

export default {
  name: 'FigureForm',
  components: {
    FormBasicTab,
    FormAuthorTab,
    FormTagsTab,
    FormSpecsTab
  },
  props: {
    show: {
      type: Boolean,
      required: true
    },
    isEditing: {
      type: Boolean,
      default: false
    },
    figure: {
      type: Object,
      required: true
    },
    activeTab: {
      type: String,
      default: 'basic'
    },
    tagStore: {
      type: Object,
      required: true
    },
    nameError: String,
    japaneseNameError: String,
    purchaseMethodError: String,
    paintingError: String,
    originalArtError: String,
    workError: String,
    manufacturerError: String,
    scaleError: String,
    materialError: String,
    sizeError: String
  },
  emits: [
    'update:figure', 'update:activeTab', 'close', 'submit',
    'validate-name-input', 'validate-japanese-name-input', 'validate-purchase-method-input',
    'validate-painting-input', 'validate-original-art-input', 'validate-work-input',
    'validate-manufacturer-input', 'validate-scale-input', 'validate-material-input', 'validate-size-input',
    'view-image', 'remove-image', 'file-upload', 'tag-change'
  ],
  computed: {
    localFigure: {
      get() {
        return this.figure
      },
      set(value) {
        this.$emit('update:figure', value)
      }
    },
    localActiveTab: {
      get() {
        return this.activeTab
      },
      set(value) {
        this.$emit('update:activeTab', value)
      }
    }
  },
  methods: {
    handleSubmit() {
      this.$emit('submit')
    }
  }
}
</script>

<style scoped>
/* 表单样式 */
.form-overlay {
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
  overflow-y: auto;
}

.form-container {
  background: white;
  padding: 0;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  overflow: hidden;
  margin: 20px;
}

.form-container h3 {
  margin-bottom: 0;
  padding: 20px 24px;
  color: #333;
  text-align: left;
  font-size: 20px;
  font-weight: 600;
  border-bottom: 1px solid #e0e0e0;
}

.form-layout {
  margin-bottom: 20px;
}

.form-actions {
  margin-top: 0;
  padding: 16px 24px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  border-top: 1px solid #e0e0e0;
  background-color: #fafafa;
}

.btn-cancel {
  background-color: transparent;
  color: #005ed3;
  border: 1px solid #005ed3;
  border-radius: 4px;
  padding: 8px 16px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-cancel:hover {
  background-color: rgba(0, 94, 211, 0.08);
  color: #004bb5;
  border-color: #004bb5;
}

.btn-submit {
  background-color: #005ed3;
  color: white;
  border-radius: 4px;
  padding: 8px 16px;
  font-weight: 500;
  border: none;
  transition: all 0.2s;
}

.btn-submit:hover {
  background-color: #004bb5;
  color: white;
}

/* 标签页样式 - Komga风格 */
.tab-label {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 12px;
  width: 100%;
  padding: 8px 0;
  font-size: 15px;
}

.tab-label i {
  font-size: 18px;
  width: 24px;
  text-align: center;
}

/* 调整表单容器宽度 */
.form-container {
  max-width: 900px;
  padding: 0;
}

/* Komga风格的侧边栏 - 使用:deep()深度选择器覆盖Element Plus默认样式 */
:deep(.form-container .el-tabs__header) {
  background-color: #f5f5f5;
  border-right: 1px solid #e0e0e0;
}

:deep(.form-container .el-tabs__item) {
  height: 62px !important;
  padding: 0 24px !important;
  text-align: left;
  justify-content: flex-start;
  border-left: 3px solid transparent;
  transition: background-color 0.15s ease, color 0.15s ease;
  background-color: white !important;
  will-change: background-color, color;
}

:deep(.form-container .el-tabs__item:hover) {
  background-color: rgba(0, 0, 0, 0.04) !important;
  color: #333 !important;
}

:deep(.form-container .el-tabs__item.is-active) {
  background-color: white;
  border-left-color: #2196F3;
  color: #2196F3;
  font-weight: 500;
  position: relative;
}

/* 添加左侧滑动指示器 - 模拟v-tabs-slider-wrapper效果 */
:deep(.form-container .el-tabs__item.is-active)::after {
  content: '';
  position: absolute;
  left: 0;
  top: 19px;
  width: 3px;
  height: 24px;
  background-color: #2196F3;
  border-radius: 0 2px 2px 0;
}

/* 标签内容区域样式 */
:deep(.form-container .el-tabs__content) {
  padding: 24px;
  background-color: white;
}

/* 移除默认边框 */
:deep(.form-container .el-tabs--border-card) {
  border: none !important;
  box-shadow: none !important;
}

/* 移除标签页容器的上下边框 */
:deep(.form-container .el-tabs--border-card > .el-tabs__header) {
  border-top: none !important;
  border-bottom: none !important;
  background-color: #f5f5f5;
}

/* 移除导航包裹的边框 */
:deep(.form-container .el-tabs__nav-wrap) {
  margin-bottom: 0;
  border-top: none !important;
  border-bottom: none !important;
}

:deep(.form-container .el-tabs__nav-scroll) {
  background-color: #f5f5f5;
  border-top: none !important;
  border-bottom: none !important;
}

/* 确保标签项没有额外的边框 */
:deep(.form-container .el-tabs--border-card > .el-tabs__header .el-tabs__item) {
  border-top: none !important;
  border-bottom: none !important;
}

/* 错误输入样式 */
:deep(.error-input .el-input__wrapper) {
  box-shadow: 0 0 0 1px #f56c6c inset !important;
}

:deep(.error-input .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #f56c6c inset !important;
}

:deep(.error-input .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #f56c6c inset !important;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .form-container {
    max-height: 90vh;
    margin: 10px;
    padding: 20px;
  }
}
</style>
