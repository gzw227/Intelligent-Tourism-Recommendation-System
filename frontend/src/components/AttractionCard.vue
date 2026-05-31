<template>
  <el-card
    class="attraction-card"
    shadow="hover"
    @click="goDetail"
  >
    <div class="card-image">
      <img :src="attraction.image_url || defaultImage" :alt="attraction.name" />
      <div class="card-rating">
        <el-icon><Star /></el-icon>
        {{ attraction.rating?.toFixed(1) || '暂无' }}
      </div>
      <div v-if="attraction.season" class="card-season">{{ attraction.season }}</div>
    </div>
    <div class="card-info">
      <h3 class="card-name">{{ attraction.name }}</h3>
      <p class="card-city">
        <el-icon><Location /></el-icon>
        {{ attraction.city }}
      </p>
      <p class="card-desc">{{ truncateDesc(attraction.description) }}</p>
    </div>
  </el-card>
</template>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  attraction: { type: Object, required: true }
})

const router = useRouter()
const defaultImage = 'https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=400&h=300&fit=crop'

function goDetail() {
  router.push(`/attraction/${props.attraction.id}`)
}

function truncateDesc(desc) {
  if (!desc) return '暂无介绍'
  return desc.length > 60 ? desc.slice(0, 60) + '...' : desc
}
</script>

<style scoped>
.attraction-card {
  cursor: pointer;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
  margin-bottom: 20px;
  border: none;
}

.attraction-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 32px rgba(99, 102, 241, 0.15);
}

.attraction-card :deep(.el-card__body) {
  padding: 0;
}

.card-image {
  position: relative;
  height: 180px;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.attraction-card:hover .card-image img {
  transform: scale(1.08);
}

.card-rating {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(0, 0, 0, 0.6);
  color: #fbbf24;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
  backdrop-filter: blur(4px);
}

.card-season {
  position: absolute;
  top: 12px;
  left: 12px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.card-info {
  padding: 16px;
}

.card-name {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-city {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #6366f1;
  margin: 0 0 8px;
}

.card-desc {
  font-size: 13px;
  color: #94a3b8;
  margin: 0;
  line-height: 1.5;
}
</style>
