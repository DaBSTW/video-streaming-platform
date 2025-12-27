import { defineStore } from 'pinia'
import { ref } from 'vue'
import { toast } from 'vue3-toastify'
import axios from 'axios'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = ref(false)
  const isLoading = ref(false)

  const login = async (credentials) => {
    isLoading.value = true
    try {
      const response = await axios.post('/auth/login', credentials)
      const { access_token, user: userData } = response.data
      
      localStorage.setItem('token', access_token)
      user.value = userData
      isAuthenticated.value = true
      
      toast.success('¡Bienvenido!')
      return true
    } catch (error) {
      toast.error(error.response?.data?.error || 'Error al iniciar sesión')
      return false
    } finally {
      isLoading.value = false
    }
  }

  const register = async (userData) => {
    isLoading.value = true
    try {
      const response = await axios.post('/auth/register', userData)
      toast.success('Usuario registrado exitosamente')
      return true
    } catch (error) {
      toast.error(error.response?.data?.error || 'Error al registrar usuario')
      return false
    } finally {
      isLoading.value = false
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    user.value = null
    isAuthenticated.value = false
    toast.success('Sesión cerrada')
  }

  const checkAuth = () => {
    const token = localStorage.getItem('token')
    if (token) {
      // Verificar si el token es válido (opcional: hacer una petición al backend)
      isAuthenticated.value = true
      // Podrías obtener los datos del usuario aquí
    }
  }

  const getUser = async () => {
    try {
      const response = await axios.get('/user')
      user.value = response.data
      return user.value
    } catch (error) {
      console.error('Error al obtener usuario:', error)
      return null
    }
  }

  return {
    user,
    isAuthenticated,
    isLoading,
    login,
    register,
    logout,
    checkAuth,
    getUser
  }
})