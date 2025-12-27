import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import { createRouter, createWebHistory } from 'vue-router'
import axios from 'axios'

// Importar estilos
import './assets/css/main.css'
import 'vue3-toastify/dist/index.css'

// Importar componentes
import App from './App.vue'
import Home from './views/Home.vue'
import Login from './views/Login.vue'
import Register from './views/Register.vue'
import Dashboard from './views/Dashboard.vue'
import Upload from './views/Upload.vue'
import VideoList from './views/VideoList.vue'
import VideoPlayer from './views/VideoPlayer.vue'
import EmbedGenerator from './views/EmbedGenerator.vue'

// Importar mensajes de i18n
import messages from './locales'

// Configurar axios
axios.defaults.baseURL = '/api'
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Configurar i18n
const i18n = createI18n({
  locale: 'es',
  fallbackLocale: 'en',
  messages,
})

// Configurar rutas
const routes = [
  { path: '/', component: Home },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { 
    path: '/dashboard', 
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  { 
    path: '/upload', 
    component: Upload,
    meta: { requiresAuth: true }
  },
  { 
    path: '/videos', 
    component: VideoList,
    meta: { requiresAuth: true }
  },
  { path: '/video/:slug', component: VideoPlayer },
  { 
    path: '/embed/:id', 
    component: EmbedGenerator,
    meta: { requiresAuth: true }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Proteger rutas
router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const token = localStorage.getItem('token')
  
  if (requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

// Crear aplicación
const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(i18n)

app.mount('#app')