<template>
  <div class="profile-page">
    <div class="profile-container">
      <el-card shadow="never" class="user-card">
        <div class="user-info">
          <el-avatar :size="80" :icon="UserFilled" class="user-avatar" />
          <div class="user-meta">
            <h2>{{ userInfo.nickname || userInfo.username || '用户' }}</h2>
            <p class="user-username">@{{ userInfo.username }}</p>
          </div>
        </div>
      </el-card>

      <el-card shadow="never" class="tabs-card">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="我的收藏" name="collects">
            <div v-loading="collectLoading">
              <el-row :gutter="20" v-if="collectList.length > 0">
                <el-col
                  v-for="item in collectList"
                  :key="item.id"
                  :xs="24" :sm="12" :md="8" :lg="6"
                >
                  <attraction-card :attraction="item" />
                </el-col>
              </el-row>
              <el-empty v-else description="还没有收藏景点" />
              <div class="pagination-wrap" v-if="collectTotal > collectPageSize">
                <el-pagination
                  v-model:current-page="collectPage"
                  :page-size="collectPageSize"
                  :total="collectTotal"
                  layout="prev, pager, next"
                  background
                  @current-change="fetchCollects"
                />
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane label="浏览历史" name="history">
            <div v-loading="historyLoading">
              <div v-if="historyList.length > 0" class="history-list">
                <div
                  v-for="item in historyList"
                  :key="item.id"
                  class="history-item"
                  @click="goDetail(item.attraction_id || item.id)"
                >
                  <img :src="item.image_url || defaultImage" :alt="item.name" />
                  <div class="history-info">
                    <h4>{{ item.name }}</h4>
                    <p class="history-city">
                      <el-icon><Location /></el-icon>
                      {{ item.city }}
                    </p>
                  </div>
                  <div class="history-time">
                    <el-icon><Clock /></el-icon>
                    {{ formatTime(item.browse_time || item.created_at) }}
                  </div>
                </div>
              </div>
              <el-empty v-else description="还没有浏览记录" />
              <div class="pagination-wrap" v-if="historyTotal > historyPageSize">
                <el-pagination
                  v-model:current-page="historyPage"
                  :page-size="historyPageSize"
                  :total="historyTotal"
                  layout="prev, pager, next"
                  background
                  @current-change="fetchHistory"
                />
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import request from '../utils/request'
import AttractionCard from '../components/AttractionCard.vue'
import { UserFilled } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const defaultImage = 'https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=400&h=300&fit=crop'

const userInfo = computed(() => userStore.user || {})

const activeTab = ref('collects')
const collectList = ref([])
const collectLoading = ref(false)
const collectPage = ref(1)
const collectPageSize = ref(8)
const collectTotal = ref(0)

const historyList = ref([])
const historyLoading = ref(false)
const historyPage = ref(1)
const historyPageSize = ref(10)
const historyTotal = ref(0)

async function fetchCollects() {
  if (!userStore.user) return
  collectLoading.value = true
  try {
    const res = await request.get(`/behavior/collects/${userStore.user.id}`, {
      params: { page: collectPage.value, page_size: collectPageSize.value }
    })
    const data = res.data || res
    collectList.value = (data.items || []).map(i => i.attraction || i)
    collectTotal.value = data.total || 0
  } catch {
    collectList.value = []
    collectTotal.value = 0
  } finally {
    collectLoading.value = false
  }
}

async function fetchHistory() {
  if (!userStore.user) return
  historyLoading.value = true
  try {
    const res = await request.get(`/behavior/history/${userStore.user.id}`, {
      params: { page: historyPage.value, page_size: historyPageSize.value }
    })
    const data = res.data || res
    historyList.value = (data.items || []).map(i => ({ ...i.attraction, created_at: i.created_at }))
    historyTotal.value = data.total || 0
  } catch {
    historyList.value = []
    historyTotal.value = 0
  } finally {
    historyLoading.value = false
  }
}

function formatTime(time) {
  if (!time) return ''
  const d = new Date(time)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function goDetail(id) {
  router.push(`/attraction/${id}`)
}

onMounted(() => {
  fetchCollects()
  fetchHistory()
})
</script>

<style scoped>
.profile-page {
  background: #f8fafc;
  min-height: calc(100vh - 60px);
  padding: 32px 24px;
}

.profile-container {
  max-width: 1000px;
  margin: 0 auto;
}

.user-card {
  border-radius: 16px;
  border: none;
  margin-bottom: 24px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
}

.user-card :deep(.el-card__body) {
  padding: 32px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-avatar {
  background: rgba(255, 255, 255, 0.2);
  font-size: 36px;
  color: #fff;
  border: 3px solid rgba(255, 255, 255, 0.3);
}

.user-meta h2 {
  color: #fff;
  font-size: 24px;
  margin: 0 0 4px;
}

.user-username {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  margin: 0;
}

.tabs-card {
  border-radius: 16px;
  border: none;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #f1f5f9;
  cursor: pointer;
  transition: all 0.2s;
}

.history-item:hover {
  border-color: #6366f1;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1);
}

.history-item img {
  width: 80px;
  height: 60px;
  border-radius: 8px;
  object-fit: cover;
  flex-shrink: 0;
}

.history-info {
  flex: 1;
  min-width: 0;
}

.history-info h4 {
  font-size: 15px;
  color: #1e293b;
  margin: 0 0 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-city {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #94a3b8;
  margin: 0;
}

.history-time {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #cbd5e1;
  flex-shrink: 0;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}
</style>
