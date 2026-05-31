import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '../utils/request'
import { ElMessage } from 'element-plus'

export const useUserStore = defineStore('user', () => {
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const token = ref(localStorage.getItem('token') || '')

  async function login(username, password) {
    const res = await request.post('/user/login', { username, password })
    const data = res.data || res
    token.value = data.token
    localStorage.setItem('token', data.token)
    user.value = {
      id: data.user_id,
      username: data.username,
      nickname: data.nickname
    }
    localStorage.setItem('user', JSON.stringify(user.value))
    ElMessage.success('登录成功')
    return data
  }

  async function register(username, password, nickname) {
    const res = await request.post('/user/register', { username, password, nickname })
    ElMessage.success('注册成功，请登录')
    return res
  }

  function logout() {
    user.value = null
    token.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    ElMessage.success('已退出登录')
  }

  async function getUserInfo() {
    if (!user.value || !user.value.id) return
    try {
      const res = await request.get(`/user/info/${user.value.id}`)
      const data = res.data || res
      user.value = { ...user.value, ...data }
      localStorage.setItem('user', JSON.stringify(user.value))
    } catch {
      user.value = null
      localStorage.removeItem('user')
    }
  }

  return { user, token, login, register, logout, getUserInfo }
})
