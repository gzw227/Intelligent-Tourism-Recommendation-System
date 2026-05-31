<template>
  <div class="detail-page" v-loading="loading">
    <template v-if="attraction">
      <div class="detail-hero">
        <img :src="attraction.image_url || defaultImage" :alt="attraction.name" />
        <div class="hero-overlay"></div>
        <div class="hero-info">
          <h1>{{ attraction.name }}</h1>
          <p>
            <el-icon><Location /></el-icon>
            {{ attraction.city }}
          </p>
        </div>
        <el-button
          :type="isCollected ? 'danger' : 'default'"
          circle
          size="large"
          class="collect-btn"
          @click="toggleCollect"
        >
          <el-icon :size="20">
            <StarFilled v-if="isCollected" />
            <Star v-else />
          </el-icon>
        </el-button>
      </div>

      <div class="detail-content">
        <el-row :gutter="24">
          <el-col :xs="24" :lg="16">
            <el-card shadow="never" class="info-card">
              <div class="info-grid">
                <div class="info-item" v-if="attraction.rating">
                  <el-icon color="#fbbf24"><Star /></el-icon>
                  <div>
                    <span class="info-label">评分</span>
                    <el-rate
                      :model-value="attraction.rating"
                      disabled
                      show-score
                      text-color="#ff9900"
                    />
                  </div>
                </div>
                <div class="info-item" v-if="attraction.address">
                  <el-icon color="#6366f1"><Location /></el-icon>
                  <div>
                    <span class="info-label">地址</span>
                    <span class="info-value">{{ attraction.address }}</span>
                  </div>
                </div>
                <div class="info-item" v-if="attraction.open_time">
                  <el-icon color="#10b981"><Clock /></el-icon>
                  <div>
                    <span class="info-label">开放时间</span>
                    <span class="info-value">{{ attraction.open_time }}</span>
                  </div>
                </div>
                <div class="info-item" v-if="attraction.play_time">
                  <el-icon color="#f59e0b"><Timer /></el-icon>
                  <div>
                    <span class="info-label">建议游玩</span>
                    <span class="info-value">{{ attraction.play_time }}</span>
                  </div>
                </div>
                <div class="info-item" v-if="attraction.season">
                  <el-icon color="#ec4899"><Sunny /></el-icon>
                  <div>
                    <span class="info-label">适宜季节</span>
                    <span class="info-value">{{ attraction.season }}</span>
                  </div>
                </div>
                <div class="info-item" v-if="attraction.ticket">
                  <el-icon color="#8b5cf6"><Ticket /></el-icon>
                  <div>
                    <span class="info-label">门票信息</span>
                    <span class="info-value">{{ attraction.ticket }}</span>
                  </div>
                </div>
              </div>
            </el-card>

            <el-card shadow="never" class="desc-card">
              <template #header>
                <h3><el-icon><Document /></el-icon> 景点介绍</h3>
              </template>
              <p class="desc-text">{{ attraction.description || '暂无介绍' }}</p>
            </el-card>

            <el-card v-if="attraction.tips" shadow="never" class="tips-card">
              <template #header>
                <h3><el-icon><Warning /></el-icon> 游玩贴士</h3>
              </template>
              <p class="tips-text">{{ attraction.tips }}</p>
            </el-card>
          </el-col>

          <el-col :xs="24" :lg="8">
            <el-card shadow="never" class="similar-card">
              <template #header>
                <h3><el-icon><Connection /></el-icon> 相似景点推荐</h3>
              </template>
              <div v-loading="similarLoading">
                <div
                  v-for="item in similarList"
                  :key="item.id"
                  class="similar-item"
                  @click="goDetail(item.id)"
                >
                  <img :src="item.image_url || defaultImage" :alt="item.name" />
                  <div class="similar-info">
                    <h4>{{ item.name }}</h4>
                    <p>
                      <el-icon><Location /></el-icon>
                      {{ item.city }}
                    </p>
                    <el-rate
                      v-if="item.rating"
                      :model-value="item.rating"
                      disabled
                      size="small"
                    />
                  </div>
                </div>
                <el-empty
                  v-if="!similarLoading && similarList.length === 0"
                  description="暂无相似推荐"
                  :image-size="60"
                />
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </template>

    <el-empty v-else-if="!loading" description="景点信息不存在" />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'
import request from '../utils/request'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const similarLoading = ref(false)
const attraction = ref(null)
const similarList = ref([])
const isCollected = ref(false)
const defaultImage = 'https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=800&h=400&fit=crop'

async function fetchDetail(id) {
  loading.value = true
  try {
    const res = await request.get(`/attractions/detail/${id}`)
    attraction.value = res.data || res
    checkCollected(id)
  } catch {
    attraction.value = null
  } finally {
    loading.value = false
  }
}

async function fetchSimilar(id) {
  similarLoading.value = true
  try {
    const res = await request.get(`/recommend/similar/${id}`)
    const data = res.data || res
    similarList.value = Array.isArray(data) ? data.map(d => d.attraction || d) : []
  } catch {
    similarList.value = []
  } finally {
    similarLoading.value = false
  }
}

async function recordBrowse(id) {
  if (!userStore.token || !userStore.user) return
  try {
    await request.post('/behavior/browse', { user_id: userStore.user.id, attraction_id: id })
  } catch {
    // silent fail
  }
}

async function checkCollected(id) {
  if (!userStore.token || !userStore.user) return
  try {
    const res = await request.get('/behavior/is_collected', { params: { user_id: userStore.user.id, attraction_id: id } })
    const data = res.data || res
    isCollected.value = data.is_collected || false
  } catch {
    isCollected.value = false
  }
}

async function toggleCollect() {
  if (!userStore.token) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  try {
    if (isCollected.value) {
      await request.delete('/behavior/collect', { data: { user_id: userStore.user.id, attraction_id: attraction.value.id } })
      isCollected.value = false
      ElMessage.success('已取消收藏')
    } else {
      await request.post('/behavior/collect', { user_id: userStore.user.id, attraction_id: attraction.value.id })
      isCollected.value = true
      ElMessage.success('收藏成功')
    }
  } catch {
    // error handled by interceptor
  }
}

function goDetail(id) {
  router.push(`/attraction/${id}`)
}

function loadPage(id) {
  fetchDetail(id)
  fetchSimilar(id)
  recordBrowse(id)
}

onMounted(() => {
  loadPage(route.params.id)
})

watch(() => route.params.id, (newId) => {
  if (newId) loadPage(newId)
})
</script>

<style scoped>
.detail-hero {
  position: relative;
  height: 400px;
  overflow: hidden;
}

.detail-hero img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.7) 0%, transparent 60%);
}

.hero-info {
  position: absolute;
  bottom: 32px;
  left: 32px;
  color: #fff;
  z-index: 1;
}

.hero-info h1 {
  font-size: 36px;
  margin: 0 0 8px;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.hero-info p {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 16px;
  opacity: 0.9;
  margin: 0;
}

.collect-btn {
  position: absolute;
  top: 24px;
  right: 24px;
  z-index: 2;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.detail-content {
  max-width: 1200px;
  margin: -40px auto 0;
  padding: 0 24px 40px;
  position: relative;
  z-index: 1;
}

.info-card,
.desc-card,
.tips-card,
.similar-card {
  border-radius: 16px;
  border: none;
  margin-bottom: 20px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
}

.info-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.info-item > .el-icon {
  margin-top: 4px;
  font-size: 20px;
}

.info-label {
  display: block;
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 4px;
}

.info-value {
  font-size: 14px;
  color: #334155;
}

.desc-card h3,
.tips-card h3,
.similar-card h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  color: #1e293b;
  margin: 0;
}

.desc-text,
.tips-text {
  font-size: 15px;
  line-height: 1.8;
  color: #475569;
  white-space: pre-wrap;
}

.tips-card {
  border-left: 4px solid #f59e0b;
}

.similar-item {
  display: flex;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #f1f5f9;
  cursor: pointer;
  transition: background 0.2s;
}

.similar-item:hover {
  background: #f8fafc;
  border-radius: 8px;
  padding: 12px 8px;
}

.similar-item:last-child {
  border-bottom: none;
}

.similar-item img {
  width: 80px;
  height: 60px;
  border-radius: 8px;
  object-fit: cover;
  flex-shrink: 0;
}

.similar-info h4 {
  font-size: 14px;
  color: #1e293b;
  margin: 0 0 4px;
}

.similar-info p {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #94a3b8;
  margin: 0 0 4px;
}
</style>
