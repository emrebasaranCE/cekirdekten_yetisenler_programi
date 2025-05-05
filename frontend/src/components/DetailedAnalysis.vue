<template>
  <form @submit.prevent="search">
    <input v-model="lat" placeholder="Latitude" />
    <input v-model="lon" placeholder="Longitude" />
    <input v-model="radius" placeholder="Radius (km)" />
    <input type="date" v-model="start" /> to <input type="date" v-model="end" />
    <button>Search</button>
  </form>
  <div v-if="results.length">
    <Charts :rawData="results" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Charts from './Charts.vue'

const lat = ref(''), lon = ref(''), radius = ref(10)
const start = ref(''), end = ref('')
const results = ref([])

async function search() {
  const qs = new URLSearchParams({ lat: lat.value, lon: lon.value, radius: radius.value, start_date: start.value, end_date: end.value })
  const resp = await fetch('/api/v1/pollution/data?' + qs)
  const json = await resp.json()
  results.value = json.data
}
</script>
