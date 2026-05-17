import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import { initializeApi } from './services/api'

initializeApi()

createApp(App).use(router).mount('#app')
