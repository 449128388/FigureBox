<!--
  TagCloud.vue - 收藏家模式标签云组件

  功能说明：
  - 展示系统标签（自动计算）和用户标签（手动添加）
  - 系统标签：海景房、破发区、待补款、已出坑（基于业务规则动态计算）
  - 用户标签：来自 figure_tag 中间表的自定义标签
  - 支持点击标签进行筛选，长按/右键管理用户标签

  组件依赖：
  - 接收 collectorData 作为 props，包含 tags/system_tags/user_tags
  - 标签数据结构：{ name, count, type: "system"|"user", description? }

  Events:
  - filter-by-tag: 点击标签筛选时触发，参数 tagName
-->
<template>
  <div class="tag-cloud">
    <div class="section-title">
      <el-icon><CollectionTag /></el-icon> 标签云
    </div>

    <!-- 系统标签 -->
    <div class="tag-section">
      <div class="tag-section-title">系统标签</div>
      <div class="tag-cloud-body">
        <span
          v-for="tag in systemTags"
          :key="'sys-' + tag.name"
          class="tag-chip"
          :class="[tagChipClass(tag.name), { 'tag-sys-zero': tag.count === 0 }]"
          @click="handleTagClick(tag.name)"
          :title="tag.description"
        >
          #{{ tag.name }}({{ tag.count }})
        </span>
      </div>
    </div>

    <!-- 用户标签 -->
    <div class="tag-section" v-if="userTags.length > 0">
      <div class="tag-section-title">
        自定义标签
        <span class="tag-section-count">{{ userTags.length }}</span>
      </div>
      <div class="tag-cloud-body">
        <span
          v-for="tag in userTags"
          :key="'user-' + tag.name"
          class="tag-chip tag-user"
          :class="{ 'tag-user-zero': tag.count === 0 }"
          @click="handleTagClick(tag.name)"
        >
          #{{ tag.name }}({{ tag.count }})
        </span>
      </div>
    </div>

    <!-- 无标签提示 -->
    <div v-if="systemTags.length === 0 && userTags.length === 0" class="tag-empty">
      暂无标签数据
    </div>
  </div>
</template>

<script>
import { CollectionTag } from '@element-plus/icons-vue'

export default {
  name: 'TagCloud',

  components: { CollectionTag },

  props: {
    collectorData: {
      type: Object,
      default: () => ({})
    }
  },

  emits: ['filter-by-tag'],

  computed: {
    /**
     * 系统标签列表（自动计算）
     */
    systemTags() {
      return this.collectorData?.system_tags || []
    },

    /**
     * 用户标签列表（手动添加）
     */
    userTags() {
      return this.collectorData?.user_tags || []
    }
  },

  methods: {
    /**
     * 获取系统标签的样式类
     * @param {string} name - 标签名称
     * @returns {string} CSS class
     */
    tagChipClass(name) {
      const classMap = {
        '海景房': 'tag-sys-star',
        '破发区': 'tag-sys-break',
        '待补款': 'tag-sys-due',
        '已出坑': 'tag-sys-sold'
      }
      return classMap[name] || 'tag-sys-default'
    },

    /**
     * 处理点击标签筛选
     * @param {string} tagName - 标签名称
     */
    handleTagClick(tagName) {
      this.$emit('filter-by-tag', tagName)
    }
  }
}
</script>

<style scoped>
.tag-cloud {
  margin-bottom: 30px;
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
}

/* Tag Sections */
.tag-section {
  margin-bottom: 16px;
}

.tag-section:last-child {
  margin-bottom: 0;
}

.tag-section-title {
  font-size: 12px;
  color: #999;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.tag-section-title::before {
  content: "";
  display: inline-block;
  width: 3px;
  height: 12px;
  background: #C49A6C;
  border-radius: 2px;
}

.tag-section-count {
  font-size: 11px;
  color: #ccc;
  margin-left: 2px;
}

.tag-cloud-body {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* Tag Chips */
.tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
  user-select: none;
}

.tag-chip:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
}

/* System Tag Colors */
.tag-sys-star {
  background: #FFF8E1;
  color: #E6A23C;
  border-color: #FFE082;
}

.tag-sys-star:hover {
  background: #FFE082;
}

.tag-sys-break {
  background: #FFEBEE;
  color: #D66A6A;
  border-color: #FFCDD2;
}

.tag-sys-break:hover {
  background: #FFCDD2;
}

.tag-sys-due {
  background: #F3E5F5;
  color: #9B7ED8;
  border-color: #E1BEE7;
}

.tag-sys-due:hover {
  background: #E1BEE7;
}

.tag-sys-sold {
  background: #F5F5F5;
  color: #999;
  border-color: #E0E0E0;
}

.tag-sys-sold:hover {
  background: #E0E0E0;
}

.tag-sys-default {
  background: #E8F5E9;
  color: #2E7D32;
  border-color: #C8E6C9;
}

.tag-sys-default:hover {
  background: #C8E6C9;
}

.tag-sys-zero {
  opacity: 0.5;
  cursor: default;
  pointer-events: none;
}

/* User Tags */
.tag-user {
  background: #FDF6EE;
  color: #C49A6C;
  border-color: #E8D5C0;
}

.tag-user:hover {
  background: #E8D5C0;
}

.tag-user-zero {
  opacity: 0.5;
  cursor: default;
  pointer-events: none;
}

/* Empty State */
.tag-empty {
  text-align: center;
  color: #999;
  font-size: 14px;
  padding: 30px 0;
}
</style>
