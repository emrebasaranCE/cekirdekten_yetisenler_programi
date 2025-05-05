import { createRouter, createWebHistory } from 'vue-router'
import Home from '../components/Home.vue'
import Map from '../components/Map.vue'
import Charts from '../components/Charts.vue'
import AnomalyPanel from '../components/AnomalyPanel.vue'
import DetailedAnalysis from '../components/DetailedAnalysis.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/map', component: Map },
  { path: '/analytics', component: DetailedAnalysis },
  { path: '/charts', component: Charts },
  { path: '/alerts', component: AnomalyPanel }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
