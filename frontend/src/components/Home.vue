<template>
  <div class="home-container">
    <header class="bg-blue-600 text-white p-4">
      <div class="container mx-auto">
        <h1 class="text-2xl font-bold">Air Pollution Monitoring System</h1>
        <p class="text-sm opacity-80">Real-time air quality monitoring and analysis</p>
      </div>
    </header>
    
    <main class="container mx-auto p-4">
      <!-- Dashboard summary cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div v-for="(metric, index) in summaryMetrics" :key="index" class="bg-white p-4 rounded-lg shadow">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-gray-500 text-sm">{{ metric.title }}</h3>
              <p class="text-2xl font-bold" :class="metric.color">{{ metric.value }}</p>
            </div>
            <div :class="`bg-${metric.bg} p-3 rounded-full`">
              <span :class="`text-${metric.color}`">
                <component :is="metric.icon" class="h-6 w-6" />
              </span>
            </div>
          </div>
          <p class="text-xs text-gray-500 mt-2">{{ metric.description }}</p>
        </div>
      </div>
      
      <!-- Main content area -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Map component -->
        <div class="lg:col-span-2 bg-white rounded-lg shadow">
          <div class="p-4 border-b">
            <h2 class="text-lg font-semibold">Pollution Heatmap</h2>
          </div>
          <div class="p-4">
            <Map />
          </div>
        </div>
        
        <!-- Anomaly panel -->
        <div class="bg-white rounded-lg shadow">
          <AnomalyPanel />
        </div>
      </div>
      
      <!-- Charts section -->
      <div class="mt-6 bg-white rounded-lg shadow">
        <div class="p-4 border-b">
          <h2 class="text-lg font-semibold">Pollution Trends</h2>
          <p class="text-sm text-gray-500">Last 24 hours monitoring data</p>
        </div>
        <div class="p-4">
          <Charts />
        </div>
      </div>
    </main>
    
    <footer class="bg-gray-100 border-t mt-8 py-4">
      <div class="container mx-auto text-center text-gray-500 text-sm">
        <p>Air Pollution Monitoring System - &copy; 2025</p>
      </div>
    </footer>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import Map from '../components/Map.vue';
import Charts from '../components/Charts.vue';
import AnomalyPanel from '../components/AnomalyPanel.vue';
import axios from 'axios';  

// Import icons (assuming you're using a library like Heroicons or Lucide)
// If you're not using an icon library, you can remove these imports and the icon references
import { CloudSun, AlertTriangle, Wind, BarChart2 } from 'lucide-vue-next';

export default {
  name: 'Home',
  components: {
    Map,
    Charts,
    AnomalyPanel,
    CloudSun,
    AlertTriangle,
    Wind,
    BarChart2
  },
  
  setup() {
    const summaryMetrics = ref([
      {
        title: 'Air Quality Index',
        value: 'Loading...',
        description: 'Current average AQI',
        color: 'text-green-600',
        bg: 'green-100',
        icon: 'CloudSun'
      },
      {
        title: 'Active Anomalies',
        value: 'Loading...',
        description: 'Detected in last 24h',
        color: 'text-red-600',
        bg: 'red-100',
        icon: 'AlertTriangle'
      },
      {
        title: 'PM2.5 Average',
        value: 'Loading...',
        description: 'Particulate matter (μg/m³)',
        color: 'text-blue-600',
        bg: 'blue-100',
        icon: 'Wind'
      },
      {
        title: 'Monitoring Stations',
        value: 'Loading...',
        description: 'Active data sources',
        color: 'text-purple-600',
        bg: 'purple-100',
        icon: 'BarChart2'
      }
    ]);

    const fetchSummaryData = async () => {
      try {
        const response = await axios.get('5002/api/v1/statistics/recent');
        const data = response.data;
        
        // Update summary metrics with real data
        summaryMetrics.value[0].value = data.current_aqi || 'N/A';
        summaryMetrics.value[0].color = getAqiColor(data.current_aqi);
        
        summaryMetrics.value[1].value = data.anomaly_count || '0';
        
        summaryMetrics.value[2].value = data.pm25_avg ? `${data.pm25_avg} μg/m³` : 'N/A';
        
        summaryMetrics.value[3].value = data.active_stations || '0';
      } catch (error) {
        console.error('Error fetching summary data:', error);
      }
    };
    
    const getAqiColor = (aqi) => {
      if (!aqi) return 'text-gray-600';
      if (aqi <= 50) return 'text-green-600';
      if (aqi <= 100) return 'text-yellow-600';
      if (aqi <= 150) return 'text-orange-600';
      if (aqi <= 200) return 'text-red-600';
      if (aqi <= 300) return 'text-purple-600';
      return 'text-rose-800';
    };
    
    onMounted(() => {
      fetchSummaryData();
      
      // Set up polling for fresh data every 5 minutes
      const intervalId = setInterval(fetchSummaryData, 5 * 60 * 1000);
      
      // Clean up interval on unmount
      return () => clearInterval(intervalId);
    });
    
    return {
      summaryMetrics
    };
  }
};
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

main {
  flex: 1;
}
</style>