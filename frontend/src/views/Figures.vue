<template>
  <div class="figures-container">
    <div class="header">
      <h2>手办管理</h2>
      <div class="header-actions">
        <button class="btn btn-add" @click="showAddForm = true">添加手办</button>
        <div class="user-info">
          <span v-if="userStore.isAuthenticated">当前用户：</span>
          <span v-if="userStore.isAuthenticated" class="username" @click="$router.push('/profile')" style="cursor: pointer; color: #2196F3; text-decoration: underline;">{{ userStore.currentUser?.username }}</span>
          <button v-if="userStore.isAuthenticated" class="btn btn-logout" @click="logout">退出</button>
        </div>
      </div>
    </div>
    <div class="figures-list">
      <div v-if="figureStore.figures.length === 0" class="empty-state">
        <p>暂无数据</p>
      </div>
      <div v-else class="figure-item" v-for="figure in figureStore.figures" :key="figure.id">
        <div class="figure-image">
          <img :src="figure.images && figure.images.length > 0 ? figure.images[0] : '/imgs/no_image.png'" :alt="figure.name">
        </div>
        <h3>{{ figure.name }}</h3>
        <p>{{ figure.manufacturer }}</p>
        <p>定价: {{ figure.price }} {{ getCurrencySymbol(figure.currency) }}</p>
        <p v-if="figure.attribute">属性: {{ figure.attribute }}</p>
        <p v-if="figure.release_date">出货日: {{ figure.release_date }}</p>
        <p v-if="figure.scale">比例: {{ figure.scale }}</p>
        <p v-if="figure.prototype">原型: {{ figure.prototype }}</p>
        <p v-if="figure.painting">涂装: {{ figure.painting }}</p>
        <p v-if="figure.original_art">原画: {{ figure.original_art }}</p>
        <p v-if="figure.work">作品: {{ figure.work }}</p>
        <p v-if="figure.material">材质: {{ figure.material }}</p>
        <p v-if="figure.size">尺寸: {{ figure.size }}</p>
        <button class="btn btn-edit">编辑</button>
        <button class="btn btn-delete" @click="deleteFigure(figure.id)">删除</button>
      </div>
    </div>
    
    <!-- 添加手办表单 -->
    <div class="form-overlay" v-if="showAddForm">
      <div class="form-container">
        <h3>添加手办</h3>
        <form @submit.prevent="addFigure">
          <div class="form-grid">
            <div class="form-group">
              <label>名称</label>
              <input type="text" v-model="newFigure.name" required>
            </div>
            <div class="form-group">
              <label>属性</label>
              <input type="text" v-model="newFigure.attribute">
            </div>
            <div class="form-group">
              <label>定价</label>
              <div class="price-currency-container">
                <input type="number" v-model.number="newFigure.price" required min="0" step="1">
                <select v-model="newFigure.currency" class="currency-select">
                  <option value="CNY">人民币</option>
                  <option value="JPY">日元</option>
                  <option value="USD">美元</option>
                  <option value="EUR">欧元</option>
                </select>
              </div>
            </div>
            <div class="form-group">
              <label>出货日</label>
              <input type="date" v-model="newFigure.release_date">
            </div>
            <div class="form-group">
              <label>制造商</label>
              <input type="text" v-model="newFigure.manufacturer">
            </div>   
            <div class="form-group">
              <label>比例</label>
              <input type="text" v-model="newFigure.scale">
            </div>
            <div class="form-group">
              <label>原型</label>
              <input type="text" v-model="newFigure.prototype">
            </div>
            <div class="form-group">
              <label>涂装</label>
              <input type="text" v-model="newFigure.painting">
            </div>
            <div class="form-group">
              <label>原画</label>
              <input type="text" v-model="newFigure.original_art">
            </div>
            <div class="form-group">
              <label>作品</label>
              <input type="text" v-model="newFigure.work">
            </div>
            <div class="form-group">
              <label>材质</label>
              <input type="text" v-model="newFigure.material">
            </div>
            <div class="form-group">
              <label>尺寸</label>
              <input type="text" v-model="newFigure.size">
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
          
          <div class="form-actions">
            <button type="button" class="btn btn-cancel" @click="showAddForm = false">取消</button>
            <button type="submit" class="btn btn-submit">保存</button>
          </div>
        </form>
      </div>
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
import { useFigureStore, useUserStore } from '../store'

export default {
  name: 'Figures',
  data() {
    return {
      showAddForm: false,
      showImagePreview: false,
      previewImage: '',
      newFigure: {
        name: '',
        manufacturer: '',
        price: 0,
        currency: 'CNY',
        attribute: '',
        release_date: '',
        scale: '',
        prototype: '',
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
    }
  },
  mounted() {
    this.figureStore.fetchFigures()
    // 如果有token但用户信息为空，获取用户信息
    if (localStorage.getItem('token') && !this.userStore.currentUser) {
      this.userStore.fetchUser()
    }
  },
  methods: {
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
    async addFigure() {
      try {
        // 处理空的日期字段
        const figureData = {
          ...this.newFigure,
          release_date: this.newFigure.release_date || null
        }
        await this.figureStore.createFigure(figureData)
        this.showAddForm = false
        // 重置表单
        this.newFigure = {
          name: '',
          manufacturer: '',
          price: 0,
          attribute: '',
          release_date: '',
          scale: '',
          prototype: '',
          painting: '',
          original_art: '',
          work: '',
          material: '',
          size: '',
          images: []
        }
      } catch (error) {
        console.error('Failed to add figure:', error)
      }
    },
    async deleteFigure(id) {
      if (confirm('确定要删除这个手办吗？')) {
        try {
          await this.figureStore.deleteFigure(id)
        } catch (error) {
          console.error('Failed to delete figure:', error)
        }
      }
    },
    logout() {
      this.userStore.logout()
      this.$router.push('/login')
    },
    getCurrencySymbol(currency) {
      switch(currency) {
        case 'CNY': return '元'
        case 'JPY': return '日元'
        case 'USD': return '美元'
        case 'EUR': return '欧元'
        default: return '元'
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
  margin-bottom: 30px;
  padding-bottom: 20px;
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
}

.btn-add:hover {
  background-color: #45a049;
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
}

.figure-item h3 {
  margin-bottom: 10px;
  color: #333;
}

.figure-item p {
  margin-bottom: 5px;
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
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  margin: 20px;
}

.form-container h3 {
  margin-bottom: 20px;
  color: #333;
  text-align: center;
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
  margin-bottom: 5px;
  color: #333;
  font-weight: 500;
  font-size: 14px;
}

.form-group input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s;
}

/* 日期输入框样式，确保字体一致 */
.form-group input[type="date"] {
  font-family: inherit;
  font-size: 14px;
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
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
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
  font-size: 24px;
  color: #999;
  margin-bottom: 5px;
}

.image-upload-placeholder p {
  font-size: 12px;
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
}

.form-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.btn-cancel {
  background-color: #9e9e9e;
  color: white;
  margin-right: 10px;
}

.btn-cancel:hover {
  background-color: #757575;
}

.btn-submit {
  background-color: #4CAF50;
  color: white;
}

.btn-submit:hover {
  background-color: #45a049;
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
</style>