<!--
  index.vue - FigureOutDrawer 组件模板入口

  功能说明：
  - 出柜登记抽屉的模板定义
  - 仅包含 template 部分，逻辑抽离到 index.js
  - 样式抽离到 index.scss

  依赖：
  - index.js: 组件逻辑
  - index.scss: 组件样式
  - FigureMini: 藏品信息子组件
-->
<template>
  <el-drawer
    v-model="drawerVisible"
    :size="drawerSize"
    :with-header="false"
    :modal="true"
    :modal-class="'figure-out-drawer-modal'"
    direction="rtl"
    destroy-on-close
    @close="handleClose"
  >
    <div class="figure-out-drawer" v-if="figureData">
      <!-- 头部 -->
      <div class="drawer-header">
        <div class="drawer-title">{{ drawerTitle }}</div>
        <button class="drawer-close" @click="handleClose">{{ closeButtonText }}</button>
      </div>

      <!-- 内容区 -->
      <div class="drawer-body">
        <!-- 藏品信息（使用子组件） -->
        <FigureMini
          :figure="figureData"
          :cabinet-icon="cabinetIcon"
          :cabinet-name="cabinetName"
        />

        <!-- 出柜说明 -->
        <div class="info-block">
          <div class="info-block-title">{{ infoBlockTitle }}</div>
          <div class="info-row">
            <span class="info-label">{{ infoLabels.operationType }}</span>
            <span class="info-value">{{ infoValues.operationType }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">{{ infoLabels.financialImpact }}</span>
            <span class="info-value success">{{ infoValues.financialImpact }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">{{ infoLabels.inventoryImpact }}</span>
            <span class="info-value">{{ infoValues.inventoryImpact }}</span>
          </div>
        </div>

        <!-- 选择去向 -->
        <div class="option-section">
          <div class="option-title">{{ optionSectionTitle }}</div>
          <div class="option-list">
            <div
              class="option-item"
              :class="{ selected: selectedOption === 'default' }"
              @click="handleSelectOption('default')"
            >
              <div class="option-radio">
                <div class="option-radio-inner"></div>
              </div>
              <div class="option-body">
                <div class="option-label">{{ outOptionLabel }}</div>
                <div class="option-desc">{{ outOptionDesc }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 警告提示 -->
        <div class="warn-box">
          <div class="warn-icon">⚠️</div>
          <div class="warn-text">
            <strong>{{ warningText.title }}</strong>{{ warningText.content }}<br>
            {{ warningText.note }}
          </div>
        </div>

        <!-- 陪伴天数提示 -->
        <div class="hint-text" v-if="holdingDaysHint">
          {{ holdingDaysHint }}
        </div>
      </div>

      <!-- 底部操作 -->
      <div class="drawer-footer">
        <button class="btn btn-default" @click="handleClose">{{ cancelButtonText }}</button>
        <button class="btn btn-primary" :disabled="submitting" @click="handleConfirm">
          {{ confirmButtonText }}
        </button>
      </div>
    </div>
  </el-drawer>
</template>

<script>
import { componentOptions } from './index'
import FigureMini from './components/FigureMini.vue'
import './index.scss'

export default {
  ...componentOptions,
  components: {
    FigureMini
  }
}
</script>
