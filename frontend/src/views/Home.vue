<template>
  <div class="home-page">
    <section class="hero-section">
      <div class="hero-overlay"></div>
      <div class="hero-content">
        <h1>探索中国，发现精彩</h1>
        <p>智能推荐，为您量身定制旅行方案</p>
        <div class="hero-search">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索景点、城市..."
            size="large"
            class="search-input"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button type="primary" size="large" class="search-btn" @click="handleSearch">
            搜索
          </el-button>
        </div>
      </div>
    </section>

    <div class="home-content">
      <section v-if="userStore.token" class="section">
        <div class="section-header">
          <h2>
            <el-icon><Star /></el-icon>
            为您推荐
          </h2>
          <p class="section-desc">基于您的偏好，智能推荐</p>
        </div>
        <el-row :gutter="20" v-loading="personalLoading">
          <el-col
            v-for="item in personalList"
            :key="item.id"
            :xs="24" :sm="12" :md="8" :lg="6"
          >
            <attraction-card :attraction="item" />
          </el-col>
          <el-col :span="24" v-if="!personalLoading && personalList.length === 0">
            <el-empty description="暂无个性化推荐，快去浏览景点吧" />
          </el-col>
        </el-row>
      </section>

      <section class="section">
        <div class="section-header">
          <h2>
            <el-icon><TrendCharts /></el-icon>
            热门景点
          </h2>
          <p class="section-desc">最受欢迎的旅行目的地</p>
        </div>
        <el-row :gutter="20" v-loading="popularLoading">
          <el-col
            v-for="item in popularList"
            :key="item.id"
            :xs="24" :sm="12" :md="8" :lg="6"
          >
            <attraction-card :attraction="item" />
          </el-col>
          <el-col :span="24" v-if="!popularLoading && popularList.length === 0">
            <el-empty description="暂无热门景点" />
          </el-col>
        </el-row>
      </section>

      <section class="section">
        <div class="section-header">
          <h2>
            <el-icon><Sunny /></el-icon>
            当季推荐 · {{ currentSeasonLabel }}
          </h2>
          <p class="section-desc">这个季节最值得去的地方</p>
        </div>
        <el-row :gutter="20" v-loading="seasonalLoading">
          <el-col
            v-for="item in seasonalList"
            :key="item.id"
            :xs="24" :sm="12" :md="8" :lg="6"
          >
            <attraction-card :attraction="item" />
          </el-col>
          <el-col :span="24" v-if="!seasonalLoading && seasonalList.length === 0">
            <el-empty description="暂无当季推荐" />
          </el-col>
        </el-row>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import request from '../utils/request'
import AttractionCard from '../components/AttractionCard.vue'

const router = useRouter()
const userStore = useUserStore()

const searchKeyword = ref('')
const personalList = ref([])
const popularList = ref([])
const seasonalList = ref([])
const personalLoading = ref(false)
const popularLoading = ref(false)
const seasonalLoading = ref(false)

const seasonMap = { spring: '春季', summer: '夏季', autumn: '秋季', winter: '冬季' }

function getCurrentSeason() {
  const month = new Date().getMonth() + 1
  if (month >= 3 && month <= 5) return 'spring'
  if (month >= 6 && month <= 8) return 'summer'
  if (month >= 9 && month <= 11) return 'autumn'
  return 'winter'
}

const currentSeason = getCurrentSeason()
const currentSeasonLabel = computed(() => seasonMap[currentSeason])

function handleSearch() {
  if (searchKeyword.value.trim()) {
    router.push({ path: '/attractions', query: { search: searchKeyword.value.trim() } })
  }
}

async function fetchPersonal() {
  if (!userStore.token || !userStore.user) return
  personalLoading.value = true
  try {
    const res = await request.get(`/recommend/personal/${userStore.user.id}`)
    const data = res.data || res
    personalList.value = Array.isArray(data) ? data.map(d => d.attraction || d) : []
  } catch {
    personalList.value = []
  } finally {
    personalLoading.value = false
  }
}

async function fetchPopular() {
  popularLoading.value = true
  try {
    const res = await request.get('/recommend/popular')
    const data = res.data || res
    popularList.value = Array.isArray(data) ? data.map(d => d.attraction || d) : []
  } catch {
    popularList.value = []
  } finally {
    popularLoading.value = false
  }
}

async function fetchSeasonal() {
  seasonalLoading.value = true
  try {
    const res = await request.get('/recommend/seasonal', { params: { season: currentSeasonLabel.value } })
    const data = res.data || res
    seasonalList.value = Array.isArray(data) ? data.map(d => d.attraction || d) : []
  } catch {
    seasonalList.value = []
  } finally {
    seasonalLoading.value = false
  }
}

onMounted(() => {
  fetchPersonal()
  fetchPopular()
  fetchSeasonal()
})
</script>

<style scoped>
.hero-section {
  position: relative;
  height: 480px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: url('https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=1920') center/cover no-repeat;
  overflow: hidden;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.85), rgba(236, 72, 153, 0.7));
}

.hero-content {
  position: relative;
  z-index: 1;
  text-align: center;
  color: #fff;
  padding: 0 24px;
}

.hero-content h1 {
  font-size: 48px;
  font-weight: 800;
  margin-bottom: 16px;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.hero-content p {
  font-size: 18px;
  opacity: 0.9;
  margin-bottom: 36px;
}

.hero-search {
  display: flex;
  max-width: 560px;
  margin: 0 auto;
  gap: 12px;
}

.search-input {
  flex: 1;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 4px 16px;
}

.search-btn {
  border-radius: 12px;
  padding: 0 32px;
  font-size: 16px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border: none;
}

.home-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 24px;
}

.section {
  margin-bottom: 48px;
}

.section-header {
  margin-bottom: 24px;
}

.section-header h2 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 24px;
  color: #1e293b;
  margin: 0 0 4px;
}

.section-header h2 .el-icon {
  color: #6366f1;
}

.section-desc {
  color: #94a3b8;
  font-size: 14px;
  margin: 0;
}
</style>
