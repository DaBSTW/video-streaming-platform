import { defineStore } from 'pinia'
import { ref } from 'vue'
import { toast } from 'vue3-toastify'
import axios from 'axios'

export const useVideoStore = defineStore('video', () => {
  const videos = ref([])
  const userVideos = ref([])
  const isLoading = ref(false)
  const currentVideo = ref(null)

  const getAllVideos = async () => {
    isLoading.value = true
    try {
      const response = await axios.get('/videos')
      videos.value = response.data
    } catch (error) {
      toast.error('Error al cargar videos')
      console.error('Error:', error)
    } finally {
      isLoading.value = false
    }
  }

  const getUserVideos = async () => {
    isLoading.value = true
    try {
      const response = await axios.get('/user/videos')
      userVideos.value = response.data
    } catch (error) {
      toast.error('Error al cargar tus videos')
      console.error('Error:', error)
    } finally {
      isLoading.value = false
    }
  }

  const uploadVideo = async (formData) => {
    isLoading.value = true
    try {
      const response = await axios.post('/videos', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      
      toast.success('Video subido exitosamente')
      await getUserVideos() // Actualizar lista de videos del usuario
      return response.data
    } catch (error) {
      toast.error(error.response?.data?.error || 'Error al subir video')
      console.error('Error:', error)
      return null
    } finally {
      isLoading.value = false
    }
  }

  const getVideo = async (slug) => {
    isLoading.value = true
    try {
      const response = await axios.get(`/videos/${slug}`)
      currentVideo.value = response.data
      return response.data
    } catch (error) {
      toast.error('Error al cargar video')
      console.error('Error:', error)
      return null
    } finally {
      isLoading.value = false
    }
  }

  const createEmbedConfig = async (videoId, config) => {
    try {
      const response = await axios.post(`/videos/${videoId}/embed`, config)
      toast.success('Configuración de embed creada')
      return response.data
    } catch (error) {
      toast.error('Error al crear configuración de embed')
      console.error('Error:', error)
      return null
    }
  }

  const deleteVideo = async (videoId) => {
    try {
      await axios.delete(`/videos/${videoId}`)
      toast.success('Video eliminado')
      await getUserVideos() // Actualizar lista
      return true
    } catch (error) {
      toast.error('Error al eliminar video')
      console.error('Error:', error)
      return false
    }
  }

  return {
    videos,
    userVideos,
    isLoading,
    currentVideo,
    getAllVideos,
    getUserVideos,
    uploadVideo,
    getVideo,
    createEmbedConfig,
    deleteVideo
  }
})