<template>
  <div class="figures-container">
    <div class="header">
      <h2>手办管理</h2>
      <div class="header-actions">
        <div class="action-buttons">
          <button class="btn btn-add" @click="openAddForm">添加手办</button>
          <button class="btn btn-download" @click="downloadFigures">
            <i class="fa-solid fa-download"></i> 下载数据
          </button>
          <button class="btn btn-refresh" @click="fetchFigures">
            <i class="fa-solid fa-refresh"></i>
          </button>
        </div>
        <div class="user-info">
          <span v-if="userStore.isAuthenticated">当前用户：</span>
          <span v-if="userStore.isAuthenticated" class="username" @click="$router.push('/profile')" style="cursor: pointer; color: #2196F3; text-decoration: underline;">{{ userStore.currentUser?.username }}</span>
          <button v-if="userStore.isAuthenticated" class="btn btn-logout" @click="logout">退出</button>
        </div>
      </div>
    </div>
    <div class="search-section">
      <div class="search-form">
        <span style="margin-right: 5px; font-weight: 500;">名称:</span>
        <el-input v-model="searchName" placeholder="搜索名称" style="width: 200px; margin-right: 10px;"></el-input>
        <span style="margin-right: 5px; font-weight: 500;">入手形式:</span>
        <el-select v-model="searchPurchaseType" placeholder="选择入手形式" style="width: 200px; margin-right: 10px;">
          <el-option value="" label="全部" />
          <el-option value="OTHER" label="其他" />
          <el-option value="PREORDER" label="预定" />
          <el-option value="INSTOCK" label="现货" />
          <el-option value="SECONDHAND" label="二手" />
          <el-option value="LOOSE" label="散货" />
          <el-option value="DOMESTIC" label="国产" />
        </el-select>
        <span style="margin-right: 5px; font-weight: 500;">入手时间:</span>
        <el-date-picker v-model="searchPurchaseDateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" style="width: 500px; min-width: 500px; max-width: 500px; margin-right: 10px;"></el-date-picker>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="resetSearch">重置</el-button>
      </div>
      <!-- 标签筛选显示 -->
      <div v-if="searchTagIds.length > 0" class="tag-filter-info" style="margin-top: 10px; padding: 8px 12px; background-color: #f0f9ff; border-radius: 4px; display: inline-flex; align-items: center; flex-wrap: wrap; gap: 8px;">
        <span style="color: #606266; margin-right: 4px;">当前标签筛选:</span>
        <el-tag 
          v-for="tagId in searchTagIds" 
          :key="tagId"
          size="small" 
          type="primary" 
          closable 
          @close="filterByTag(tagId)"
          style="font-size: 14px;"
        >
          {{ getTagNameById(tagId) }}
        </el-tag>
      </div>
    </div>
    <div class="figures-list">
      <div v-if="figureStore.figures.length === 0" class="empty-state">
        <p>暂无数据</p>
      </div>
      <div v-else class="figure-item" v-for="figure in paginatedFigures" :key="figure.id">
        <div class="figure-image">
          <img 
            :src="figure.image || '/imgs/no_image.png'" 
            :alt="figure.name"
            loading="lazy"
            decoding="async"
          >
        </div>
        <h3><router-link :to="`/figures/${figure.id}`" class="figure-name-link">{{ figure.name }}</router-link></h3>
        <p>定价: {{ figure.price !== null && figure.price !== undefined ? figure.price : '未设置' }} {{ getCurrencySymbol(figure.currency) }}</p>
        <p v-if="figure.purchase_price !== null && figure.purchase_price !== undefined">入手价格: {{ figure.purchase_price }} {{ getCurrencySymbol(figure.purchase_currency) }}</p>
        <p v-else>入手价格: 未设置</p>
        <p v-if="figure.purchase_date">入手时间: {{ figure.purchase_date }}</p>
        <div v-if="figure.tags && figure.tags.length > 0" class="tags-container">
          <span class="tags-label">标签:</span>
          <el-tag
            v-for="tag in getSortedTags(figure.tags)"
            :key="tag.id"
            size="small"
            effect="light"
            class="clickable-tag"
            @click="filterByTag(tag.id)"
            style="margin-right: 4px; margin-bottom: 4px; cursor: pointer;"
            :type="searchTagIds.includes(tag.id) ? 'primary' : ''"
          >
            {{ tag.name }}
          </el-tag>
        </div>
        <div class="figure-actions">
          <button class="btn btn-edit" @click="editFigure(figure)">编辑</button>
          <button class="btn btn-delete" @click="deleteFigure(figure.id)">删除</button>
        </div>
      </div>
    </div>
    
    <!-- 添加手办表单 -->
    <div class="form-overlay" v-if="showAddForm">
      <div class="form-container">
        <h3>{{ isEditing ? '编辑手办' : '添加手办' }}</h3>
        <form @submit.prevent="addFigure">
          <div class="form-layout">
            <el-tabs type="border-card" :tab-position="'left'" lazy v-model="activeTab" ref="formTabs">
              <!-- 基础页面 -->
              <el-tab-pane label="基础" name="basic">
                <template #label>
                  <div class="tab-label">
                    <i class="fa-solid fa-home"></i>
                    <span>基础</span>
                  </div>
                </template>
                <div class="form-grid">
                  <div class="form-group">
                    <label>名称</label>
                    <el-input 
                      v-model="newFigure.name" 
                      placeholder="请输入名称" 
                      :class="{ 'error-input': nameError }"
                      @input="validateNameOnInput"
                      ref="nameInput"
                    ></el-input>
                    <div v-if="nameError" class="error-message">{{ nameError }}</div>
                  </div>
                  <div class="form-group">
                    <label>定价</label>
                    <div class="price-currency-container">
                      <el-input-number v-model="newFigure.price" placeholder="请输入定价" :min="0" :step="1" required style="width: 200px;"></el-input-number>
                      <el-select v-model="newFigure.currency" placeholder="选择币种" style="width: 120px;">
                        <el-option value="CNY" label="人民币" />
                        <el-option value="JPY" label="日元" />
                        <el-option value="USD" label="美元" />
                        <el-option value="EUR" label="欧元" />
                      </el-select>
                    </div>
                  </div>
                  <div class="form-group">
                    <label>日文名</label>
                    <el-input
                      v-model="newFigure.japanese_name"
                      placeholder="请输入日文名"
                      :class="{ 'error-input': japaneseNameError }"
                      @input="validateJapaneseNameOnInput"
                      maxlength="100"
                      show-word-limit
                    ></el-input>
                    <div v-if="japaneseNameError" class="error-message">{{ japaneseNameError }}</div>
                  </div>
                  <div class="form-group">
                    <label>入手价格</label>
                    <div class="price-currency-container">
                      <el-input-number v-model="newFigure.purchase_price" placeholder="请输入入手价格" :min="0" :step="1" style="width: 200px;"></el-input-number>
                      <el-select v-model="newFigure.purchase_currency" placeholder="选择币种" style="width: 120px;">
                        <el-option value="CNY" label="人民币" />
                        <el-option value="JPY" label="日元" />
                        <el-option value="USD" label="美元" />
                        <el-option value="EUR" label="欧元" />
                      </el-select>
                    </div>
                  </div>
                  <div class="form-group">
                    <label>出货日</label>
                    <el-date-picker v-model="newFigure.release_date" type="date" placeholder="选择出货日" style="width: 100%;"></el-date-picker>
                  </div>
                  <div class="form-group">
                    <label>入手时间</label>
                    <el-date-picker v-model="newFigure.purchase_date" type="date" placeholder="选择入手时间" style="width: 100%;"></el-date-picker>
                  </div>
                  <div class="form-group">
                    <label>入手途径</label>
                    <el-input 
                      v-model="newFigure.purchase_method" 
                      placeholder="请输入入手途径"
                      :class="{ 'error-input': purchaseMethodError }"
                      @input="validatePurchaseMethodOnInput"
                    ></el-input>
                    <div v-if="purchaseMethodError" class="error-message">{{ purchaseMethodError }}</div>
                  </div>
                  <div class="form-group">
                    <label>入手形式</label>
                    <el-select v-model="newFigure.purchase_type" placeholder="请选择入手形式" style="width: 100%;">
                      <el-option value="OTHER" label="其他" />
                      <el-option value="PREORDER" label="预定" />
                      <el-option value="INSTOCK" label="现货" />
                      <el-option value="SECONDHAND" label="二手" />
                      <el-option value="LOOSE" label="散货" />
                      <el-option value="DOMESTIC" label="国产" />
                    </el-select>
                  </div>
                  <div class="form-group">
                    <label>数量</label>
                    <el-input-number v-model="newFigure.quantity" placeholder="请输入数量" :min="1" :step="1" style="width: 200px;"></el-input-number>
                  </div>
                </div>
                
                <!-- 图片上传 -->
                <div class="form-group full-width">
                  <label>图片上传 (最多10张，每张不超过20MB)</label>
                  <div class="image-upload-container">
                    <div class="image-upload-list">
                      <div v-for="(image, index) in newFigure.images" :key="index" class="image-upload-item">
                        <img :src="image" :alt="`图片 ${index + 1}`">
                        <div class="image-actions">
                          <button type="button" class="icon-btn view-btn" @click="viewImage(image)">
                            <i class="fa-solid fa-eye"></i>
                          </button>
                          <button type="button" class="icon-btn delete-btn" @click="removeImage(index)">
                            <i class="fa-solid fa-trash"></i>
                          </button>
                        </div>
                      </div>
                      <div v-if="newFigure.images.length < 10" class="image-upload-placeholder" @click="triggerFileInput">
                        <span>+</span>
                        <p>添加图片</p>
                      </div>
                    </div>
                    <input type="file" ref="fileInput" multiple accept="image/*" style="display: none" @change="handleFileUpload">
                  </div>
                </div>
              </el-tab-pane>
              
              <!-- 作者页面 -->
              <el-tab-pane label="作者" name="author">
                <template #label>
                  <div class="tab-label">
                    <i class="fa-solid fa-user"></i>
                    <span>作者</span>
                  </div>
                </template>
                <div class="form-grid">
                  <div class="form-group">
                    <label>涂装</label>
                    <el-input 
                      v-model="newFigure.painting" 
                      placeholder="请输入涂装"
                      :class="{ 'error-input': paintingError }"
                      @input="validatePaintingOnInput"
                    ></el-input>
                    <div v-if="paintingError" class="error-message">{{ paintingError }}</div>
                  </div>
                  <div class="form-group">
                    <label>原画</label>
                    <el-input 
                      v-model="newFigure.original_art" 
                      placeholder="请输入原画"
                      :class="{ 'error-input': originalArtError }"
                      @input="validateOriginalArtOnInput"
                    ></el-input>
                    <div v-if="originalArtError" class="error-message">{{ originalArtError }}</div>
                  </div>
                  <div class="form-group">
                    <label>作品</label>
                    <el-input 
                      v-model="newFigure.work" 
                      placeholder="请输入作品"
                      :class="{ 'error-input': workError }"
                      @input="validateWorkOnInput"
                    ></el-input>
                    <div v-if="workError" class="error-message">{{ workError }}</div>
                  </div>
                </div>
              </el-tab-pane>
              
              <!-- 标签页面 -->
              <el-tab-pane label="标签" name="tags">
                <template #label>
                  <div class="tab-label">
                    <i class="fa-solid fa-tags"></i>
                    <span>标签</span>
                  </div>
                </template>
                <div class="form-grid">
                  <div class="form-group">
                    <label>标签</label>
                    <el-select
                      v-model="newFigure.tag_ids"
                      multiple
                      filterable
                      allow-create
                      default-first-option
                      placeholder="请选择或输入标签"
                      empty-text="暂无数据"
                      style="width: 100%"
                      @change="handleTagChange"
                    >
                      <el-option
                        v-for="item in tagStore.tags"
                        :key="item.id"
                        :label="item.name"
                        :value="item.id"
                      />
                    </el-select>
                  </div>
                </div>
              </el-tab-pane>
              
              <!-- 规格页面 -->
              <el-tab-pane label="规格" name="specs">
                <template #label>
                  <div class="tab-label">
                    <i class="fa-solid fa-ruler"></i>
                    <span>规格</span>
                  </div>
                </template>
                <div class="form-grid">
                  <div class="form-group">
                    <label>制造商</label>
                    <el-input 
                      v-model="newFigure.manufacturer" 
                      placeholder="请输入制造商"
                      :class="{ 'error-input': manufacturerError }"
                      @input="validateManufacturerOnInput"
                    ></el-input>
                    <div v-if="manufacturerError" class="error-message">{{ manufacturerError }}</div>
                  </div>   
                  <div class="form-group">
                    <label>比例</label>
                    <el-input 
                      v-model="newFigure.scale" 
                      placeholder="请输入比例"
                      :class="{ 'error-input': scaleError }"
                      @input="validateScaleOnInput"
                    ></el-input>
                    <div v-if="scaleError" class="error-message">{{ scaleError }}</div>
                  </div>
                  <div class="form-group">
                    <label>材质</label>
                    <el-input 
                      v-model="newFigure.material" 
                      placeholder="请输入材质"
                      :class="{ 'error-input': materialError }"
                      @input="validateMaterialOnInput"
                    ></el-input>
                    <div v-if="materialError" class="error-message">{{ materialError }}</div>
                  </div>
                  <div class="form-group">
                    <label>尺寸</label>
                    <el-input 
                      v-model="newFigure.size" 
                      placeholder="请输入尺寸"
                      :class="{ 'error-input': sizeError }"
                      @input="validateSizeOnInput"
                    ></el-input>
                    <div v-if="sizeError" class="error-message">{{ sizeError }}</div>
                  </div>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
          
          <div class="form-actions">
            <el-button class="btn-cancel" @click="showAddForm = false">取消</el-button>
            <el-button class="btn-submit" type="primary" native-type="submit">保存</el-button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- 分页组件 -->
    <div v-if="totalFigures > 0" class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="pageSizes"
        layout="total, sizes, prev, pager, next, jumper"
        :total="totalFigures"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
    
    <!-- 图片预览模态框 -->
    <div v-if="showImagePreview" class="image-preview-modal" @click="closeImagePreview">
      <div class="image-preview-content" @click.stop>
        <button class="btn btn-close-preview" @click="closeImagePreview">×</button>
        <img :src="previewImage" :alt="'预览图片'">
      </div>
    </div>
  </div>
</template>

<script>
import { useFigureStore, useUserStore, useTagStore } from '../store'
import axios from '../axios'

export default {
  name: 'Figures',
  data() {
    return {
      showAddForm: false,
      showImagePreview: false,
      previewImage: '',
      tagOptions: ['PVC', 'ABS', '树脂', '合金', '可动', '限定', '特典', '初版', '再版'],
      nameError: '',
      japaneseNameError: '',
      purchaseMethodError: '',
      paintingError: '',
      originalArtError: '',
      workError: '',
      manufacturerError: '',
      scaleError: '',
      materialError: '',
      sizeError: '',
      activeTab: 'basic',
      currentPage: 1,
      pageSize: 15,
      pageSizes: [15, 30, 45, 60],
      isEditing: false,
      currentEditFigureId: null,
      // 搜索相关
      searchName: '',
      searchPurchaseDateRange: [],
      searchPurchaseType: '',
      searchTagIds: [],  // 使用标签ID数组进行多标签筛选
      newFigure: {
        name: '',
        japanese_name: '',
        manufacturer: '',
        price: 0,
        currency: 'CNY',
        tag_ids: [],  // 使用标签ID列表
        release_date: '',
        purchase_price: 0,
        purchase_currency: 'CNY',
        purchase_date: '',
        purchase_method: '',
        purchase_type: '',
        scale: '',
        painting: '',
        original_art: '',
        work: '',
        material: '',
        size: '',
        images: []
      }
    }
  },
  computed: {
    figureStore() {
      return useFigureStore()
    },
    userStore() {
      return useUserStore()
    },
    tagStore() {
      return useTagStore()
    },

    // 分页处理 - 直接使用后端返回的数据（已排序和过滤）
    paginatedFigures() {
      // 后端已经按 id 降序排序并过滤，直接返回
      return this.figureStore.figures
    },

    // 总数据量 - 使用后端返回的总数
    totalFigures() {
      return this.figureStore.totalCount
    }
  },
  async mounted() {
    // 使用 fetchFiguresWithSearch 加载数据，确保分页参数正确传递
    await this.fetchFiguresWithSearch()
    // 如果有token但用户信息为空，获取用户信息
    if (localStorage.getItem('token') && !this.userStore.currentUser) {
      this.userStore.fetchUser()
    }
    // 加载所有标签
    await this.tagStore.fetchTags()
  },
  watch: {
    'figureStore.figures': {
      handler() {
        this.updateTagOptions()
      },
      deep: true
    }
  },
  methods: {
    updateTagOptions() {
      const defaultOptions = []
      const allTags = new Set(defaultOptions)
      
      // 从已存在的手办中提取所有标签值
      this.figureStore.figures.forEach(figure => {
        if (figure.tags && Array.isArray(figure.tags)) {
          // tags 是对象数组，提取标签名称
          figure.tags.forEach(tag => {
            if (tag && tag.name) {
              allTags.add(tag.name)
            }
          })
        }
      })
      
      // 更新tagOptions
      this.tagOptions = Array.from(allTags)
    },
    triggerFileInput() {
      this.$refs.fileInput.click()
    },
    handleFileUpload(event) {
      const files = event.target.files
      const maxFiles = 10 - this.newFigure.images.length
      const maxSize = 20 * 1024 * 1024 // 20MB
      
      for (let i = 0; i < Math.min(files.length, maxFiles); i++) {
        const file = files[i]
        
        if (file.size > maxSize) {
          alert(`图片 ${file.name} 超过20MB，无法上传`)
          continue
        }
        
        const reader = new FileReader()
        reader.onload = (e) => {
          this.newFigure.images.push(e.target.result)
        }
        reader.readAsDataURL(file)
      }
      
      // 清空input，以便可以重复选择相同的文件
      event.target.value = ''
    },
    removeImage(index) {
      if (confirm('确定要删除这张图片吗？')) {
        this.newFigure.images.splice(index, 1)
      }
    },
    viewImage(image) {
      this.previewImage = image
      this.showImagePreview = true
    },
    closeImagePreview() {
      this.showImagePreview = false
      this.previewImage = ''
    },
    // 验证字段
    validateField(value, fieldName, minLength, maxLength, allowSpecialChars = true) {
      if (!value || value.trim() === '') {
        return { valid: true, value: null } // 空值允许通过（可选字段）
      }
      
      // 过滤 emoji
      const emojiPattern = /[\uD83C-\uDBFF\uDC00-\uDFFF]/g
      let cleanedValue = value.replace(emojiPattern, '')
      
      // 去除首尾空格
      cleanedValue = cleanedValue.trim()
      
      // 检查过滤后是否为空（如果原始值不为空但过滤后为空，说明输入的全是emoji）
      if (cleanedValue.length === 0) {
        return { valid: false, error: `${fieldName}不能只包含特殊字符` }
      }
      
      // 长度验证
      if (cleanedValue.length < minLength) {
        return { valid: false, error: `${fieldName}长度不能少于${minLength}个字符` }
      }
      if (cleanedValue.length > maxLength) {
        return { valid: false, error: `${fieldName}长度不能超过${maxLength}个字符` }
      }
      
      // 字符类型验证
      let pattern
      if (allowSpecialChars) {
        // 允许中文、英文、日文、数字、空格，常见符号
        pattern = /^[\u4e00-\u9fa5\u3040-\u309f\u30a0-\u30ff\u3100-\u312fa-zA-Z0-9\s\/\×\(\)\&\-\.\,\:\;\!\?\#\@\$\%\*\+\=\[\]\{\}\|\<\>\~\`\"\'\\]*$/
      } else {
        // 只允许中文、英文、日文、数字、空格
        pattern = /^[\u4e00-\u9fa5\u3040-\u309f\u30a0-\u30ff\u3100-\u312fa-zA-Z0-9\s]*$/
      }
      
      if (!pattern.test(cleanedValue)) {
        return { valid: false, error: `${fieldName}包含不允许的字符` }
      }
      
      return { valid: true, value: cleanedValue }
    },
    
    // 验证名称字段（实时验证）
    validateNameOnInput() {
      const value = this.newFigure.name

      // 必填检查
      if (!value || value.trim() === '') {
        this.nameError = '名称不能为空'
        // 如果不在基础页，自动跳转并聚焦
        this.focusToNameField()
        return
      }

      // 调用通用验证方法
      const result = this.validateField(value, '名称', 1, 100, true)

      if (!result.valid) {
        this.nameError = result.error
        // 如果不在基础页，自动跳转并聚焦
        this.focusToNameField()
      } else {
        this.nameError = ''
        // 更新验证后的值
        this.newFigure.name = result.value || ''
      }
    },

    // 验证日文名字段（实时验证）
    validateJapaneseNameOnInput() {
      const value = this.newFigure.japanese_name

      // 空值允许通过（非必填字段）
      if (!value || value.trim() === '') {
        this.japaneseNameError = ''
        return
      }

      // 调用通用验证方法
      const result = this.validateField(value, '日文名', 1, 100, true)

      if (!result.valid) {
        this.japaneseNameError = result.error
      } else {
        this.japaneseNameError = ''
        // 更新验证后的值
        this.newFigure.japanese_name = result.value || ''
      }
    },
    
    // 跳转到名称字段并聚焦
    focusToNameField() {
      // 切换到基础标签页
      this.activeTab = 'basic'
      // 使用nextTick等待DOM更新后聚焦
      this.$nextTick(() => {
        if (this.$refs.nameInput) {
          this.$refs.nameInput.focus()
        }
      })
    },
    
    // 验证入手途径字段（实时验证）
    validatePurchaseMethodOnInput() {
      const value = this.newFigure.purchase_method
      
      // 空值允许通过（非必填字段）
      if (!value || value.trim() === '') {
        this.purchaseMethodError = ''
        return
      }
      
      // 调用通用验证方法
      const result = this.validateField(value, '入手途径', 1, 50, true)
      
      if (!result.valid) {
        this.purchaseMethodError = result.error
      } else {
        this.purchaseMethodError = ''
        // 更新验证后的值
        this.newFigure.purchase_method = result.value || ''
      }
    },
    
    // 验证涂装字段（实时验证）
    validatePaintingOnInput() {
      const value = this.newFigure.painting
      
      // 空值允许通过（非必填字段）
      if (!value || value.trim() === '') {
        this.paintingError = ''
        return
      }
      
      // 调用通用验证方法
      const result = this.validateField(value, '涂装', 1, 40, true)
      
      if (!result.valid) {
        this.paintingError = result.error
      } else {
        this.paintingError = ''
        // 更新验证后的值
        this.newFigure.painting = result.value || ''
      }
    },
    
    // 验证原画字段（实时验证）
    validateOriginalArtOnInput() {
      const value = this.newFigure.original_art
      
      // 空值允许通过（非必填字段）
      if (!value || value.trim() === '') {
        this.originalArtError = ''
        return
      }
      
      // 调用通用验证方法
      const result = this.validateField(value, '原画', 1, 40, true)
      
      if (!result.valid) {
        this.originalArtError = result.error
      } else {
        this.originalArtError = ''
        // 更新验证后的值
        this.newFigure.original_art = result.value || ''
      }
    },
    
    // 验证作品字段（实时验证）
    validateWorkOnInput() {
      const value = this.newFigure.work
      
      // 空值允许通过（非必填字段）
      if (!value || value.trim() === '') {
        this.workError = ''
        return
      }
      
      // 调用通用验证方法
      const result = this.validateField(value, '作品', 1, 80, true)
      
      if (!result.valid) {
        this.workError = result.error
      } else {
        this.workError = ''
        // 更新验证后的值
        this.newFigure.work = result.value || ''
      }
    },
    
    // 验证制造商字段（实时验证）
    validateManufacturerOnInput() {
      const value = this.newFigure.manufacturer
      
      // 空值允许通过（非必填字段）
      if (!value || value.trim() === '') {
        this.manufacturerError = ''
        return
      }
      
      // 调用通用验证方法
      const result = this.validateField(value, '制造商', 1, 60, true)
      
      if (!result.valid) {
        this.manufacturerError = result.error
      } else {
        this.manufacturerError = ''
        // 更新验证后的值
        this.newFigure.manufacturer = result.value || ''
      }
    },
    
    // 验证比例字段（实时验证）
    validateScaleOnInput() {
      const value = this.newFigure.scale
      
      // 空值允许通过（非必填字段）
      if (!value || value.trim() === '') {
        this.scaleError = ''
        return
      }
      
      // 调用通用验证方法
      const result = this.validateField(value, '比例', 1, 20, true)
      
      if (!result.valid) {
        this.scaleError = result.error
      } else {
        this.scaleError = ''
        // 更新验证后的值
        this.newFigure.scale = result.value || ''
      }
    },
    
    // 验证材质字段（实时验证）
    validateMaterialOnInput() {
      const value = this.newFigure.material
      
      // 空值允许通过（非必填字段）
      if (!value || value.trim() === '') {
        this.materialError = ''
        return
      }
      
      // 调用通用验证方法
      const result = this.validateField(value, '材质', 1, 50, true)
      
      if (!result.valid) {
        this.materialError = result.error
      } else {
        this.materialError = ''
        // 更新验证后的值
        this.newFigure.material = result.value || ''
      }
    },
    
    // 验证尺寸字段（实时验证）
    validateSizeOnInput() {
      const value = this.newFigure.size
      
      // 空值允许通过（非必填字段）
      if (!value || value.trim() === '') {
        this.sizeError = ''
        return
      }
      
      // 调用通用验证方法
      const result = this.validateField(value, '尺寸', 1, 50, true)
      
      if (!result.valid) {
        this.sizeError = result.error
      } else {
        this.sizeError = ''
        // 更新验证后的值
        this.newFigure.size = result.value || ''
      }
    },
    
    // 验证表单
    validateForm() {
      // 先验证名称字段
      this.validateNameOnInput()
      if (this.nameError) {
        return false
      }

      // 验证日文名字段
      this.validateJapaneseNameOnInput()
      if (this.japaneseNameError) {
        return false
      }

      // 验证入手途径字段
      this.validatePurchaseMethodOnInput()
      if (this.purchaseMethodError) {
        return false
      }
      
      // 验证涂装字段
      this.validatePaintingOnInput()
      if (this.paintingError) {
        return false
      }
      
      // 验证原画字段
      this.validateOriginalArtOnInput()
      if (this.originalArtError) {
        return false
      }
      
      // 验证作品字段
      this.validateWorkOnInput()
      if (this.workError) {
        return false
      }
      
      // 验证制造商字段
      this.validateManufacturerOnInput()
      if (this.manufacturerError) {
        return false
      }
      
      // 验证比例字段
      this.validateScaleOnInput()
      if (this.scaleError) {
        return false
      }
      
      // 验证材质字段
      this.validateMaterialOnInput()
      if (this.materialError) {
        return false
      }
      
      // 验证尺寸字段
      this.validateSizeOnInput()
      if (this.sizeError) {
        return false
      }
      
      const validations = []
      
      for (const item of validations) {
        const value = this.newFigure[item.field]
        
        // 必填字段检查
        if (item.required && (!value || value.trim() === '')) {
          alert(`${item.label}不能为空`)
          return false
        }
        
        // 字段验证
        const result = this.validateField(
          value, 
          item.label, 
          item.min, 
          item.max, 
          !item.simple
        )
        
        if (!result.valid) {
          alert(result.error)
          return false
        }
        
        // 更新验证后的值
        this.newFigure[item.field] = result.value || ''
      }
      
      return true
    },
    
    // 重置表单
    resetForm() {
      // 重置错误信息
      this.nameError = ''
      this.japaneseNameError = ''
      this.purchaseMethodError = ''
      this.paintingError = ''
      this.originalArtError = ''
      this.workError = ''
      this.manufacturerError = ''
      this.scaleError = ''
      this.materialError = ''
      this.sizeError = ''

      // 重置编辑状态
      this.isEditing = false
      this.currentEditFigureId = null

      // 重置表单数据
      this.newFigure = {
        name: '',
        japanese_name: '',
        manufacturer: '',
        price: 0,
        currency: 'CNY',
        tag_ids: [],  // 使用标签ID列表
        release_date: '',
        purchase_price: 0,
        purchase_currency: 'CNY',
        purchase_date: '',
        purchase_method: '',
        purchase_type: '',
        quantity: 1,  // 数量默认值为1
        scale: '',
        painting: '',
        original_art: '',
        work: '',
        material: '',
        size: '',
        images: []
      }
      
      // 重置标签页
      this.activeTab = 'basic'
    },
    
    // 打开添加手办表单
    openAddForm() {
      // 重置表单
      this.resetForm()
      // 显示表单
      this.showAddForm = true
    },
    
    async addFigure() {
      try {
        // 表单验证
        if (!this.validateForm()) {
          return
        }

        // 处理空的日期字段和价格字段
        // 确保日期格式正确，只保留日期部分，去除时间部分
        const formatDate = (date) => {
          if (!date) return null
          if (typeof date === 'string') return date
          // 转换为YYYY-MM-DD格式
          return date.toISOString().split('T')[0]
        }

        // 处理标签：分离已存在的标签ID和需要创建的新标签名称
        const existingTagIds = []
        const newTagNames = []

        for (const item of this.newFigure.tag_ids) {
          if (typeof item === 'number') {
            // 已存在的标签ID
            existingTagIds.push(item)
          } else if (typeof item === 'string') {
            // 新标签名称（用户输入的）
            newTagNames.push(item)
          }
        }

        // 创建新标签并获取ID
        for (const tagName of newTagNames) {
          try {
            const newTag = await this.tagStore.createTag({ name: tagName })
            existingTagIds.push(newTag.id)
          } catch (error) {
            // 如果标签已存在，查找并获取ID
            const existingTag = this.tagStore.tags.find(t => t.name === tagName)
            if (existingTag) {
              existingTagIds.push(existingTag.id)
            }
          }
        }

        const figureData = {
          ...this.newFigure,
          release_date: formatDate(this.newFigure.release_date),
          purchase_date: formatDate(this.newFigure.purchase_date),
          purchase_currency: this.newFigure.purchase_currency || 'CNY',
          tag_ids: existingTagIds
        }

        if (this.isEditing) {
          // 编辑模式
          await this.figureStore.updateFigure(this.currentEditFigureId, figureData)
        } else {
          // 添加模式
          await this.figureStore.createFigure(figureData)
        }

        this.showAddForm = false
        // 重置表单
        this.resetForm()

        // 重新加载列表数据，确保排序正确
        await this.fetchFiguresWithSearch()
      } catch (error) {
        console.error('Failed to add figure:', error)
      }
    },
    async deleteFigure(id) {
      if (confirm('确定要删除这个手办吗？')) {
        try {
          await this.figureStore.deleteFigure(id)
          alert('手办删除成功')
        } catch (error) {
          console.error('Failed to delete figure:', error)
          if (error.response && error.response.status === 400) {
            alert('无法删除有关联尾款的手办')
          } else {
            alert('删除失败，请稍后重试')
          }
        }
      }
    },
    logout() {
      this.userStore.logout()
      this.$router.push('/login')
    },
    async editFigure(figure) {
      // 打开编辑表单
      this.showAddForm = true
      this.isEditing = true
      this.currentEditFigureId = figure.id

      try {
        // 调用详情接口获取完整的手办信息（包含完整的images数组）
        const response = await axios.get(`/figures/${figure.id}`)
        const fullFigure = response

        // 填充表单数据，确保images字段存在且为数组，quantity字段有默认值
        this.newFigure = {
          ...fullFigure,
          tag_ids: fullFigure.tags ? fullFigure.tags.map(tag => tag.id) : [],  // 使用标签ID列表
          price: fullFigure.price || 0,
          purchase_price: fullFigure.purchase_price || 0,
          images: fullFigure.images || [],  // 确保images字段存在且为数组
          quantity: fullFigure.quantity || 1  // 确保quantity字段存在，默认值为1
        }
      } catch (error) {
        console.error('Failed to fetch figure details:', error)
        // 失败时使用列表数据作为回退
        this.newFigure = {
          ...figure,
          tag_ids: figure.tags ? figure.tags.map(tag => tag.id) : [],
          price: figure.price || 0,
          purchase_price: figure.purchase_price || 0,
          images: figure.image ? [figure.image] : []
        }
      }

      // 重置错误信息
      this.resetErrors()
    },
    resetErrors() {
      this.nameError = ''
      this.purchaseMethodError = ''
      this.paintingError = ''
      this.originalArtError = ''
      this.workError = ''
      this.manufacturerError = ''
      this.scaleError = ''
      this.materialError = ''
      this.sizeError = ''
    },
    getCurrencySymbol(currency) {
      switch(currency) {
        case 'CNY': return '元'
        case 'JPY': return '日元'
        case 'USD': return '美元'
        case 'EUR': return '欧元'
        default: return '元'
      }
    },
    // 解析标签字符串为数组，使用缓存优化性能
    parseTags(tagStr) {
      if (!tagStr) return []
      // 使用简单的缓存机制
      if (!this._tagCache) this._tagCache = {}
      if (this._tagCache[tagStr]) return this._tagCache[tagStr]
      const result = tagStr.split(',').filter(tag => tag.trim())
      this._tagCache[tagStr] = result
      return result
    },
    
    // 处理每页条数变化
    async handleSizeChange(val) {
      this.pageSize = val
      this.currentPage = 1 // 重置为第一页
      await this.fetchFiguresWithSearch()
    },
    
    // 处理页码变化
    async handleCurrentChange(val) {
      this.currentPage = val
      await this.fetchFiguresWithSearch()
    },
    
    // 刷新数据
    async fetchFigures() {
      await this.fetchFiguresWithSearch()
    },
    
    // 处理搜索 - 调用后端接口
    async handleSearch() {
      this.currentPage = 1 // 搜索时重置到第一页
      await this.fetchFiguresWithSearch()
    },
    
    // 重置搜索
    async resetSearch() {
      this.searchName = ''
      this.searchPurchaseDateRange = []
      this.searchPurchaseType = ''
      this.searchTagIds = []
      this.currentPage = 1 // 重置到第一页
      await this.fetchFiguresWithSearch()
    },

    // 根据标签ID筛选
    async filterByTag(tagId) {
      // 如果点击的是已选中的标签，则移除它
      if (this.searchTagIds.includes(tagId)) {
        this.searchTagIds = this.searchTagIds.filter(id => id !== tagId)
      } else {
        // 否则添加到筛选列表
        this.searchTagIds.push(tagId)
      }
      this.currentPage = 1 // 重置到第一页
      await this.fetchFiguresWithSearch()
    },

    // 根据标签ID获取标签名称
    getTagNameById(tagId) {
      const tag = this.tagStore.tags.find(t => t.id === tagId)
      return tag ? tag.name : ''
    },

    // 获取排序后的标签列表（按标签ID排序，确保顺序固定）
    getSortedTags(tags) {
      if (!tags || !Array.isArray(tags)) return []
      return [...tags].sort((a, b) => a.id - b.id)
    },

    // 根据搜索条件获取数据
    async fetchFiguresWithSearch() {
      const params = {
        skip: (this.currentPage - 1) * this.pageSize,
        limit: this.pageSize
      }

      // 添加搜索条件
      if (this.searchName) {
        params.name = this.searchName
      }
      if (this.searchPurchaseType) {
        params.purchase_type = this.searchPurchaseType
      }
      if (this.searchPurchaseDateRange && this.searchPurchaseDateRange.length === 2) {
        const formatDate = (date) => {
          if (!date) return null
          const d = new Date(date)
          const year = d.getFullYear()
          const month = String(d.getMonth() + 1).padStart(2, '0')
          const day = String(d.getDate()).padStart(2, '0')
          return `${year}-${month}-${day}`
        }
        params.purchase_date_start = formatDate(this.searchPurchaseDateRange[0])
        params.purchase_date_end = formatDate(this.searchPurchaseDateRange[1])
      }
      // 添加标签筛选条件（使用标签ID数组）
      if (this.searchTagIds && this.searchTagIds.length > 0) {
        params.tag_ids = this.searchTagIds
      }

      await this.figureStore.fetchFigures(params)
    },
    
    // 下载手办数据
    async downloadFigures() {
      try {
        // 使用原生 fetch API 获取响应，以便正确处理文件下载
        const token = localStorage.getItem('token')
        const response = await fetch('/api/figures/download', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        
        if (!response.ok) {
          throw new Error('下载失败')
        }
        
        // 获取响应文本（JSON 字符串）
        const jsonText = await response.text()
        
        // 创建下载链接
        const blob = new Blob([jsonText], { type: 'application/json' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `figures_${new Date().toISOString().split('T')[0]}.json`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
        
        this.$message.success('手办数据下载成功')
      } catch (error) {
        console.error('下载失败:', error)
        this.$message.error('下载失败，请重试')
      }
    }
  }
}
</script>

<style scoped>
.figures-container {
  margin-top: 20px;
  width: 100%;
  max-width: 1650px;
  margin-left: 50px;
  margin-right: 50px;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #e0e0e0;
}

.header h2 {
  margin: 0;
  color: #333;
  font-size: 24px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 10px;
}

.search-section {
  margin-bottom: 30px;
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.search-form {
  display: flex;
  align-items: center;
  gap: 15px;
  width: 100%;
  justify-content: flex-start;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 10px 15px;
  background-color: white;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.username {
  font-size: 14px;
  font-weight: 500;
  color: #555;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.btn-add {
  background-color: #4CAF50;
  color: white;
  padding: 12px 24px;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 44px;
  box-sizing: border-box;
}

.btn-add:hover {
  background-color: #45a049;
}

.btn-download {
  background-color: #ff9800;
  color: white;
  padding: 12px 24px;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 44px;
  box-sizing: border-box;
}

.btn-download:hover {
  background-color: #f57c00;
}

.btn-refresh {
  background-color: #2196F3;
  color: white;
  padding: 10px 12px;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
}

.btn-refresh:hover {
  background-color: #0b7dda;
}

.btn-logout {
  background-color: #f44336;
  color: white;
  padding: 8px 16px;
  font-size: 14px;
}

.btn-logout:hover {
  background-color: #da190b;
}

.figures-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 60px 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  color: #999;
  font-size: 16px;
}

.figure-item {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  contain: layout style paint;
  will-change: transform;
}

.figure-item h3 {
  margin-bottom: 10px;
  color: #333;
}

.figure-name-link {
  color: #2196F3;
  text-decoration: none;
  transition: color 0.3s ease;
}

.figure-name-link:hover {
  color: #0b7dda;
}

.figure-item p {
  margin-bottom: 5px;
  color: #666;
}

.tags-container {
  margin-bottom: 10px;
}

.tags-label {
  font-weight: 500;
  margin-right: 8px;
  color: #666;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  margin-right: 10px;
  margin-top: 10px;
}

.btn-edit {
  background-color: #2196F3;
  color: white;
}

.btn-edit:hover {
  background-color: #0b7dda;
}

.btn-delete {
  background-color: #f44336;
  color: white;
}

.btn-delete:hover {
  background-color: #da190b;
}

.figure-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.figure-actions .btn {
  margin: 0;
  flex: 1;
}

.btn-add {
  background-color: #4CAF50;
  color: white;
  padding: 10px 20px;
  font-size: 16px;
}

.btn-add:hover {
  background-color: #45a049;
}

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

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 0;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #333;
  font-weight: 500;
  font-size: 16px;
}

.form-group input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  transition: border-color 0.3s;
}

/* 日期输入框样式，确保字体一致 */
.form-group input[type="date"] {
  font-family: inherit;
  font-size: 16px;
}

.form-group input:focus {
  outline: none;
  border-color: #2196F3;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.1);
}

/* 价格和币种容器样式 */
.price-currency-container {
  display: flex;
  gap: 10px;
}

.price-currency-container input {
  flex: 1;
}

.currency-select {
  padding: 10px 14px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  background-color: white;
  cursor: pointer;
  transition: border-color 0.3s;
}

.currency-select:focus {
  outline: none;
  border-color: #2196F3;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.1);
}

/* 图片上传样式 */
.form-group.full-width {
  grid-column: 1 / -1;
  margin-top: 20px;
}

.image-upload-container {
  margin-top: 10px;
}

.image-upload-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.image-upload-item {
  position: relative;
  width: 100px;
  height: 100px;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
}

.image-upload-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: all 0.3s ease;
}

.image-actions {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  opacity: 0;
  transition: all 0.3s ease;
  z-index: 1;
}

.image-upload-item:hover .image-actions {
  opacity: 1;
}

.image-upload-item:hover img {
  transform: scale(1.05);
}

/* 通用图标按钮 */
.icon-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: none;
  font-size: 14px;
  transition: all 0.2s ease;
}

/* 查看（眼睛） */
.view-btn {
  background: #f5f5f5;
  color: #666;
}
.view-btn:hover {
  background: #e6f7ff;
  color: #1890ff;
}

/* 删除（垃圾桶） */
.delete-btn {
  background: #f5f5f5;
  color: #666;
}
.delete-btn:hover {
  background: #fff2f0;
  color: #ff4d4f;
}

.image-upload-placeholder {
  width: 100px;
  height: 100px;
  border: 2px dashed #ddd;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.image-upload-placeholder:hover {
  border-color: #2196F3;
  background-color: rgba(33, 150, 243, 0.05);
}

.image-upload-placeholder span {
  font-size: 32px;
  color: #999;
  margin-bottom: 8px;
}

.image-upload-placeholder p {
  font-size: 14px;
  color: #999;
  margin: 0;
}

/* 手办图片样式 */
.figure-image {
  width: 100%;
  height: 200px;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 15px;
  background-color: #f5f5f5;
}

.figure-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  content-visibility: auto;
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

/* 图片预览模态框样式 */
.image-preview-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.image-preview-content {
  position: relative;
  max-width: 90%;
  max-height: 90%;
}

.image-preview-content img {
  max-width: 100%;
  max-height: 80vh;
  object-fit: contain;
  border-radius: 8px;
}

.btn-close-preview {
  position: absolute;
  top: -40px;
  right: 0;
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-close-preview:hover {
  background-color: rgba(255, 255, 255, 0.3);
}

/* 表单选择框样式 */
.form-select {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  background-color: white;
  cursor: pointer;
  transition: border-color 0.3s;
}

.form-select:focus {
  outline: none;
  border-color: #2196F3;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .form-container {
    max-height: 90vh;
    margin: 10px;
    padding: 20px;
  }
  
  .figure-image {
    height: 150px;
  }
  
  .image-upload-item,
  .image-upload-placeholder {
    width: 80px;
    height: 80px;
  }
}

/* 表单布局样式 */
.form-layout {
  margin-bottom: 20px;
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

:deep(.form-container .el-tabs__content) {
  padding: 24px;
  background-color: white;
}

:deep(.form-container .el-tabs--border-card) {
  border: none;
  box-shadow: none;
}

:deep(.form-container .el-tabs--border-card > .el-tabs__header) {
  border: none;
  background-color: #fafafa;
}

:deep(.form-container .el-tabs--border-card > .el-tabs__header .el-tabs__item) {
  border: none;
}

:deep(.form-container .el-tabs--border-card > .el-tabs__header .el-tabs__item.is-active) {
  background-color: white;
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

.error-message {
  color: #f56c6c;
  font-size: 12px;
  line-height: 1;
  padding-top: 4px;
}
  /* 分页组件样式 */
  .pagination-container {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
    padding-right: 20px;
  }
</style>
