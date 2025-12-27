<template>
  <div class="video-player">
    <div ref="playerContainer" class="player-container"></div>
    
    <div v-if="video" class="video-info">
      <h2 class="video-title">{{ video.title }}</h2>
      <p class="video-description">{{ video.description }}</p>
      <div class="video-meta">
        <span class="views">{{ video.views }} vistas</span>
        <span class="date">{{ formatDate(video.created_at) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import Artplayer from 'artplayer'
import { useVideoStore } from '../stores/video'

const props = defineProps({
  slug: {
    type: String,
    required: true
  }
})

const playerContainer = ref(null)
const artPlayer = ref(null)
const videoStore = useVideoStore()
const video = ref(null)

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const initPlayer = async () => {
  if (!props.slug) return

  try {
    const videoData = await videoStore.getVideo(props.slug)
    if (!videoData) return

    video.value = videoData

    // Destruir jugador anterior si existe
    if (artPlayer.value) {
      artPlayer.value.destroy()
    }

    artPlayer.value = new Artplayer({
      container: playerContainer.value,
      url: videoData.video_url,
      poster: videoData.thumbnail_url,
      title: videoData.title,
      fullscreen: true,
      fullscreenWeb: true,
      setting: true,
      pip: true,
      screenshot: true,
      autoplay: false,
      volume: 0.7,
      mutex: true,
      backdrop: true,
      miniProgressBar: true,
      theme: '#3b82f6',
      
      // Configuración de calidad (si se tiene HLS/DASH)
      customType: {
        // Aquí se pueden agregar tipos de video personalizados
      },
      
      // Controles personalizados
      controls: [
        {
          name: 'download',
          position: 'right',
          html: 'Descargar',
          click: () => {
            const link = document.createElement('a')
            link.href = videoData.video_url
            link.download = videoData.title
            link.click()
          }
        }
      ],
      
      // Capas personalizadas
      layers: [
        {
          name: 'watermark',
          style: {
            position: 'absolute',
            right: '10px',
            bottom: '10px',
            color: 'rgba(255, 255, 255, 0.5)',
            fontSize: '12px',
            pointerEvents: 'none',
          },
          html: 'Video Platform',
        }
      ],
      
      // Configuración de subtítulos (si se tienen)
      subtitle: {
        url: '', // URL del archivo de subtítulos
        type: 'vtt',
        style: {
          color: '#ffffff',
          fontSize: '20px',
          textShadow: '0 0 2px #000',
        }
      }
    })

    // Eventos del reproductor
    artPlayer.value.on('ready', () => {
      console.log('Reproductor listo')
    })

    artPlayer.value.on('play', () => {
      console.log('Video en reproducción')
    })

    artPlayer.value.on('pause', () => {
      console.log('Video en pausa')
    })

    artPlayer.value.on('fullscreen', () => {
      console.log('Pantalla completa')
    })

    artPlayer.value.on('fullscreenWeb', () => {
      console.log('Pantalla completa web')
    })

  } catch (error) {
    console.error('Error al inicializar el reproductor:', error)
  }
}

// Observar cambios en el slug
watch(() => props.slug, initPlayer)

onMounted(() => {
  initPlayer()
})

onUnmounted(() => {
  if (artPlayer.value) {
    artPlayer.value.destroy()
  }
})
</script>

<style scoped>
.video-player {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.player-container {
  width: 100%;
  aspect-ratio: 16 / 9;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.video-info {
  margin-top: 20px;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.1);
}

.video-title {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 10px 0;
}

.video-description {
  font-size: 16px;
  color: #6b7280;
  line-height: 1.6;
  margin: 0 0 20px 0;
}

.video-meta {
  display: flex;
  gap: 20px;
  color: #9ca3af;
  font-size: 14px;
}

.views {
  font-weight: 500;
}

.date {
  font-weight: 500;
}

/* Responsive */
@media (max-width: 768px) {
  .video-player {
    padding: 10px;
  }
  
  .player-container {
    aspect-ratio: 16 / 9;
  }
  
  .video-title {
    font-size: 20px;
  }
  
  .video-description {
    font-size: 14px;
  }
  
  .video-meta {
    flex-direction: column;
    gap: 10px;
  }
}
</style>