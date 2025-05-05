<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
} from 'chart.js'

// register Chart.js components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const chartData = ref({
  labels: [],        // pollutant names
  datasets: []       // avg & max series
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    title: {
      display: true,
      text: 'Last 24h Pollution Levels'
    },
    tooltip: { mode: 'index', intersect: false },
    legend: { position: 'top' }
  },
  scales: {
    y: {
      beginAtZero: true,
      title: { display: true, text: 'µg/m³' }
    }
  }
}

async function fetchStats() {
  try {
    const { data: res } = await axios.get('/api/v1/statistics/recent')
    if (res.status === 'success' && res.data) {
      const d = res.data
      // define mapping
      const pollutants = [
        { label: 'PM2.5', avgKey: 'avg_pm25', maxKey: 'max_pm25' },
        { label: 'PM10',  avgKey: 'avg_pm10', maxKey: 'max_pm10' },
        { label: 'NO2',   avgKey: 'avg_no2',  maxKey: 'max_no2'  },
        { label: 'SO2',   avgKey: 'avg_so2',  maxKey: 'max_so2'  },
        { label: 'O3',    avgKey: 'avg_o3',   maxKey: 'max_o3'   }
      ]
      chartData.value = {
        labels: pollutants.map(p => p.label),
        datasets: [
          {
            label: 'Average',
            backgroundColor: 'rgba(75, 192, 192, 0.5)',
            borderColor: 'rgba(75, 192, 192, 1)',
            data: pollutants.map(p => d[p.avgKey] ?? 0)
          },
          {
            label: 'Maximum',
            backgroundColor: 'rgba(255, 99, 132, 0.5)',
            borderColor: 'rgba(255, 99, 132, 1)',
            data: pollutants.map(p => d[p.maxKey] ?? 0)
          }
        ]
      }
    }
  } catch (err) {
    console.error('Failed to load stats:', err)
  }
}

onMounted(fetchStats)
</script>

<template>
  <div class="chart-container">
    <Bar :chart-data="chartData" :options="chartOptions" />
  </div>
</template>

<style scoped>
.chart-container {
  position: relative;
  width: 100%;
  height: 400px;
}
</style>
