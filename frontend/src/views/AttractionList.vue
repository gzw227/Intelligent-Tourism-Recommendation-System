<template>
  <div class="attraction-list-page">
    <div class="page-container">
      <aside class="filter-sidebar">
        <el-card shadow="never" class="filter-card">
          <h3 class="filter-title">
            <el-icon><Filter /></el-icon>
            筛选条件
          </h3>

          <div class="filter-group">
            <label>搜索</label>
            <el-input
              v-model="filters.search"
              placeholder="搜索景点名称"
              clearable
              :prefix-icon="Search"
              @clear="fetchList"
              @keyup.enter="fetchList"
            />
          </div>

          <div class="filter-group">
            <label>城市</label>
            <el-select
              v-model="filters.city"
              placeholder="选择城市"
              clearable
              @change="fetchList"
            >
              <el-option
                v-for="city in cityOptions"
                :key="city"
                :label="city"
                :value="city"
              />
            </el-select>
          </div>

          <div class="filter-group">
            <label>最低评分</label>
            <el-select
              v-model="filters.min_rating"
              placeholder="选择评分"
              clearable
              @change="fetchList"
            >
              <el-option label="4.5分以上" :value="4.5" />
              <el-option label="4.0分以上" :value="4.0" />
              <el-option label="3.5分以上" :value="3.5" />
              <el-option label="3.0分以上" :value="3.0" />
            </el-select>
          </div>

          <el-button type="primary" class="filter-btn" @click="fetchList">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button class="filter-btn" @click="resetFilters">重置</el-button>
        </el-card>
      </aside>

      <main class="list-main">
        <div class="list-header">
          <h2>景点浏览</h2>
          <span class="result-count">共 {{ total }} 个景点</span>
        </div>

        <el-row :gutter="20" v-loading="loading">
          <el-col
            v-for="item in attractionList"
            :key="item.id"
            :xs="24" :sm="12" :md="8"
          >
            <attraction-card :attraction="item" />
          </el-col>
          <el-col :span="24" v-if="!loading && attractionList.length === 0">
            <el-empty description="没有找到符合条件的景点" />
          </el-col>
        </el-row>

        <div class="pagination-wrap" v-if="total > 0">
          <el-pagination
            v-model:current-page="page"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[8, 12, 16, 24]"
            layout="total, sizes, prev, pager, next, jumper"
            background
            @size-change="fetchList"
            @current-change="fetchList"
          />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import request from '../utils/request'
import AttractionCard from '../components/AttractionCard.vue'
import { Search } from '@element-plus/icons-vue'

const route = useRoute()

const loading = ref(false)
const attractionList = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(12)

const cityOptions = ref([])

async function loadCities() {
  try {
    const res = await request.get('/attractions/cities')
    const data = res.data || res
    cityOptions.value = Array.isArray(data) ? data : []
  } catch {
    cityOptions.value = ['北京', '上海', '广州', '深圳', '成都', '杭州', '重庆', '西安', '苏州', '南京', '长沙', '厦门', '青岛', '大理', '丽江', '桂林']
  }
}

const filters = reactive({
  search: '',
  city: '',
  min_rating: null
})

async function fetchList() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value
    }
    if (filters.search) params.keyword = filters.search
    if (filters.city) params.city = filters.city
    if (filters.min_rating) params.min_rating = filters.min_rating

    const res = await request.get('/attractions/list', { params })
    const data = res.data || res
    attractionList.value = data.items || []
    total.value = data.total || 0
  } catch {
    attractionList.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  filters.search = ''
  filters.city = ''
  filters.min_rating = null
  page.value = 1
  fetchList()
}

onMounted(() => {
  loadCities()
  if (route.query.search) {
    filters.search = route.query.search
  }
  fetchList()
})
</script>

<style scoped>
.attraction-list-page {
  background: #f8fafc;
  min-height: calc(100vh - 60px);
}

.page-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
  display: flex;
  gap: 24px;
}

.filter-sidebar {
  width: 260px;
  flex-shrink: 0;
}

.filter-card {
  border-radius: 16px;
  border: none;
  position: sticky;
  top: 80px;
}

.filter-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  color: #1e293b;
  margin: 0 0 20px;
}

.filter-group {
  margin-bottom: 20px;
}

.filter-group label {
  display: block;
  font-size: 13px;
  color: #64748b;
  margin-bottom: 8px;
  font-weight: 500;
}

.filter-group .el-select,
.filter-group .el-input {
  width: 100%;
}

.filter-btn {
  width: 100%;
  margin-bottom: 8px;
  border-radius: 10px;
}

.list-main {
  flex: 1;
  min-width: 0;
}

.list-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 24px;
}

.list-header h2 {
  font-size: 24px;
  color: #1e293b;
  margin: 0;
}

.result-count {
  font-size: 14px;
  color: #94a3b8;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 32px;
  padding-bottom: 16px;
}

@media (max-width: 768px) {
  .page-container {
    flex-direction: column;
  }

  .filter-sidebar {
    width: 100%;
  }
}
</style>
