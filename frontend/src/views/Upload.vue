<template>
  <div class="upload-page">
    <div class="container mx-auto px-4 py-8">
      <div class="max-w-4xl mx-auto">
        <div class="bg-white rounded-lg shadow-lg p-6">
          <h1 class="text-2xl font-bold text-gray-900 mb-6">Subir Video</h1>
          
          <form @submit.prevent="handleUpload" class="space-y-6">
            <!-- Información del Video -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Título del Video
                </label>
                <input
                  v-model="form.title"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ingresa el título del video"
                  required
                />
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Miniatura (Opcional)
                </label>
                <input
                  @change="handleThumbnailUpload"
                  type="file"
                  accept="image/*"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Descripción
              </label>
              <textarea
                v-model="form.description"
                rows="4"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Describe tu video"
              ></textarea>
            </div>

            <!-- Archivo de Video -->
            <div class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors">
              <div v-if="!selectedFile" class="space-y-4">
                <div class="text-gray-500">
                  <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </div>
                <div>
                  <label class="cursor-pointer text-blue-600 hover:text-blue-800 font-medium">
                    Seleccionar archivo
                    <input
                      @change="handleFileSelect"
                      type="file"
                      accept="video/*"
                      class="hidden"
                      required
                    />
                  </label>
                  <span class="text-gray-500 mx-2">o arrastra y suelta aquí</span>
                </div>
                <p class="text-sm text-gray-500">Formatos soportados: MP4, WebM, AVI</p>
              </div>

              <!-- Vista previa del archivo seleccionado -->
              <div v-else class="space-y-4">
                <div class="flex items-center justify-between bg-gray-50 p-4 rounded-lg">
                  <div class="flex items-center space-x-3">
                    <svg class="h-8 w-8 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    <div class="text-left">
                      <p class="font-medium text-gray-900">{{ selectedFile.name }}</p>
                      <p class="text-sm text-gray-500">{{ formatFileSize(selectedFile.size) }}</p>
                    </div>
                  </div>
                  <button
                    @click="selectedFile = null"
                    type="button"
                    class="text-red-500 hover:text-red-700"
                  >
                    <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                <!-- Miniatura del video -->
                <div v-if="thumbnailPreview" class="mt-4">
                  <img :src="thumbnailPreview" alt="Miniatura" class="max-w-xs mx-auto rounded-lg shadow-md" />
                </div>
              </div>
            </div>

            <!-- Progreso de Subida -->
            <div v-if="uploadProgress > 0" class="space-y-2">
              <div class="flex justify-between text-sm text-gray-600">
                <span>Subiendo video...</span>
                <span>{{ uploadProgress }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                  :style="{ width: uploadProgress + '%' }"
                ></div>
              </div>
            </div>

            <!-- Botones de Acción -->
            <div class="flex justify-between items-center">
              <router-link 
                to="/videos" 
                class="text-gray-600 hover:text-gray-900 transition-colors"
              >
                ← Volver a mis videos
              </router-link>
              
              <div class="flex space-x-3">
                <button
                  type="button"
                  @click="resetForm"
                  class="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
                >
                  Limpiar
                </button>
                <button
                  type="submit"
                  :disabled="isLoading || !selectedFile"
                  class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <span v-if="isLoading">
                    <svg class="animate-spin h-5 w-5 mr-2 inline-block" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Subiendo...
                  </span>
                  <span v-else>Subir Video</span>
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useVideoStore } from '../stores/video'
import { toast } from 'vue3-toastify'

const router = useRouter()
const videoStore = useVideoStore()

const selectedFile = ref(null)
const thumbnailFile = ref(null)
const thumbnailPreview = ref('')
const uploadProgress = ref(0)
const isLoading = ref(false)

const form = ref({
  title: '',
  description: ''
})

const handleFileSelect = (event) => {
  selectedFile.value = event.target.files[0]
  generateThumbnail()
}

const handleThumbnailUpload = (event) => {
  thumbnailFile.value = event.target.files[0]
  if (thumbnailFile.value) {
    thumbnailPreview.value = URL.createObjectURL(thumbnailFile.value)
  }
}

const generateThumbnail = () => {
  if (!selectedFile.value) return

  const video = document.createElement('video')
  video.src = URL.createObjectURL(selectedFile.value)
  video.load()

  video.addEventListener('loadeddata', () => {
    const canvas = document.createElement('canvas')
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    
    const ctx = canvas.getContext('2d')
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
    
    thumbnailPreview.value = canvas.toDataURL('image/jpeg')
  })
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const resetForm = () => {
  selectedFile.value = null
  thumbnailFile.value = null
  thumbnailPreview.value = ''
  uploadProgress.value = 0
  form.value = {
    title: '',
    description: ''
  }
}

const handleUpload = async () => {
  if (!selectedFile.value) {
    toast.error('Por favor selecciona un archivo de video')
    return
  }

  isLoading.value = true
  uploadProgress.value = 0

  try {
    const formData = new FormData()
    formData.append('video', selectedFile.value)
    formData.append('title', form.value.title || selectedFile.value.name)
    formData.append('description', form.value.description)

    if (thumbnailFile.value) {
      formData.append('thumbnail', thumbnailFile.value)
    }

    const result = await videoStore.uploadVideo(formData)
    
    if (result) {
      toast.success('Video subido exitosamente')
      router.push('/videos')
    }
  } catch (error) {
    console.error('Error al subir video:', error)
    toast.error('Error al subir el video')
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.upload-page {
  min-height: 100vh;
  background-color: #f3f4f6;
}

/* Animaciones para el área de arrastre */
.drag-over {
  border-color: #3b82f6 !important;
  background-color: #eff6ff !important;
}
</style>