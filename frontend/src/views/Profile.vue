<template>
  <div class="profile-container">
    <h2>个人资料</h2>
    <div class="profile-info" v-if="userStore.currentUser">
      <div v-if="!isEditing">
        <p><strong>用户名:</strong> {{ userStore.currentUser.username }}</p>
        <p><strong>邮箱:</strong> {{ userStore.currentUser.email }}</p>
        <button class="btn btn-edit" @click="startEditing">编辑资料</button>
      </div>
      <div v-else class="edit-form">
        <div class="form-group">
          <label>用户名</label>
          <input type="text" v-model="editUser.username">
        </div>
        <div class="form-group">
          <label>邮箱</label>
          <input type="email" v-model="editUser.email">
        </div>
        <div class="form-actions">
          <button class="btn btn-cancel" @click="cancelEditing">取消</button>
          <button class="btn btn-save" @click="saveChanges">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useUserStore } from '../store'

export default {
  name: 'Profile',
  data() {
    return {
      isEditing: false,
      editUser: {
        username: '',
        email: ''
      }
    }
  },
  computed: {
    userStore() {
      return useUserStore()
    }
  },
  mounted() {
    if (!this.userStore.currentUser) {
      this.userStore.fetchUser()
    }
  },
  methods: {
    startEditing() {
      this.editUser = {
        username: this.userStore.currentUser.username,
        email: this.userStore.currentUser.email
      }
      this.isEditing = true
    },
    cancelEditing() {
      this.isEditing = false
    },
    async saveChanges() {
      try {
        // 这里可以添加API调用，更新用户信息
        console.log('保存用户信息:', this.editUser)
        // 模拟保存成功
        this.userStore.user = this.editUser
        this.isEditing = false
      } catch (error) {
        console.error('保存失败:', error)
      }
    }
  }
}
</script>

<style scoped>
.profile-container {
  margin-top: 20px;
}

h2 {
  margin-bottom: 20px;
  color: #333;
}

.profile-info {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.profile-info p {
  margin-bottom: 10px;
  color: #333;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  margin-top: 10px;
}

.btn-edit {
  background-color: #2196F3;
  color: white;
}

.btn-edit:hover {
  background-color: #0b7dda;
}

.edit-form {
  margin-top: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: #333;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #2196F3;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.1);
}

.form-actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}

.btn-cancel {
  background-color: #9e9e9e;
  color: white;
}

.btn-cancel:hover {
  background-color: #757575;
}

.btn-save {
  background-color: #4CAF50;
  color: white;
}

.btn-save:hover {
  background-color: #45a049;
}
</style>