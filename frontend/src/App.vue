<template>
  <div class="app-container">
    <el-menu
      :default-active="activeIndex"
      mode="horizontal"
      :ellipsis="false"
      class="nav-bar"
      @select="handleSelect"
    >
      <div class="nav-logo" @click="router.push('/')">
        <el-icon :size="24"><Location /></el-icon>
        <span class="logo-text">智游中国</span>
      </div>

      <el-menu-item index="/">
        <el-icon><HomeFilled /></el-icon>
        <span>首页</span>
      </el-menu-item>
      <el-menu-item index="/attractions">
        <el-icon><Place /></el-icon>
        <span>景点浏览</span>
      </el-menu-item>
      <el-menu-item v-if="userStore.token" index="/profile">
        <el-icon><User /></el-icon>
        <span>个人中心</span>
      </el-menu-item>

      <div class="nav-right">
        <template v-if="userStore.token && userStore.user">
          <span class="nav-username">
            <el-icon><UserFilled /></el-icon>
            {{ userStore.user.nickname || userStore.user.username }}
          </span>
          <el-button type="danger" text @click="handleLogout">退出</el-button>
        </template>
        <template v-else>
          <el-button type="primary" @click="router.push('/login')">登录</el-button>
          <el-button @click="router.push('/register')">注册</el-button>
        </template>
      </div>
    </el-menu>

    <main class="main-content">
      <router-view />
    </main>

    <footer class="app-footer">
      <p>© 2026 智游中国 - 智能旅游推荐系统</p>
    </footer>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from './stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const activeIndex = computed(() => route.path)

function handleSelect(index) {
  router.push(index)
}

function handleLogout() {
  userStore.logout()
  router.push('/')
}
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.nav-bar {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  padding: 0 24px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  border-bottom: none;
}

.nav-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  margin-right: 40px;
  padding: 0 8px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, #6366f1, #ec4899);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-right {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 12px;
}

.nav-username {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: #6366f1;
  font-weight: 500;
}

.main-content {
  flex: 1;
}

.app-footer {
  text-align: center;
  padding: 24px;
  color: #94a3b8;
  font-size: 13px;
  background: #f8fafc;
}
</style>
