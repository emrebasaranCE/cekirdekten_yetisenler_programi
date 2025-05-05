<template>
  <div class="anomaly-panel">
    <div class="panel-header">
      <h2 class="text-xl font-bold mb-2">Anomaly Alerts</h2>
      <div class="flex">
        <button 
          class="bg-red-500 text-white px-4 py-1 rounded-md mr-2 text-sm" 
          @click="refreshAnomalies">
          Refresh
        </button>
        <select 
          v-model="alertType"
          class="bg-gray-100 border border-gray-300 rounded-md text-sm px-2">
          <option value="all">All Alerts</option>
          <option value="critical">Critical</option>
          <option value="warning">Warning</option>
        </select>
      </div>
    </div>

    <div class="anomaly-list mt-4">
      <div v-if="loading" class="text-center py-4">
        <div class="inline-block animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-red-500"></div>
        <p class="mt-2 text-gray-600">Loading anomalies...</p>
      </div>
      
      <div v-else-if="anomalies.length === 0" class="text-center py-8 bg-gray-50 rounded-md">
        <p class="text-gray-500">No anomalies detected</p>
      </div>
      
      <div v-else class="space-y-3">
        <div 
          v-for="(anomaly, index) in filteredAnomalies" 
          :key="index"
          class="anomaly-item p-3 rounded-md shadow-sm"
          :class="{'bg-red-50 border-l-4 border-red-500': anomaly.severity === 'critical',
                  'bg-yellow-50 border-l-4 border-yellow-500': anomaly.severity === 'warning'}">
          <div class="flex justify-between">
            <span class="font-medium">{{ anomaly.location }}</span>
            <span 
              class="text-sm px-2 py-0.5 rounded-full"
              :class="{'bg-red-100 text-red-800': anomaly.severity === 'critical',
                      'bg-yellow-100 text-yellow-800': anomaly.severity === 'warning'}">
              {{ anomaly.severity }}
            </span>
          </div>
          <div class="text-sm mt-1">{{ anomaly.pollutant }}: {{ anomaly.value }} {{ anomaly.unit }}</div>
          <div class="text-xs text-gray-500 mt-1">{{ formatTime(anomaly.timestamp) }}</div>
          <div class="mt-2 text-sm">
            <button 
              class="text-blue-600 hover:text-blue-800"
              @click="viewDetails(anomaly)">
              View details
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import io from 'socket.io-client';

export default {
  name: 'AnomalyPanel',
  
  setup() {
    const anomalies = ref([]);
    const loading = ref(true);
    const alertType = ref('all');
    const socket = ref(null);
    
    const filteredAnomalies = computed(() => {
      if (alertType.value === 'all') {
        return anomalies.value;
      } else {
        return anomalies.value.filter(anomaly => anomaly.severity === alertType.value);
      }
    });
    
    const fetchAnomalies = async () => {
      loading.value = true;
      try {
        const response = await axios.get('/api/v1/anomalies');
        anomalies.value = response.data;
      } catch (error) {
        console.error('Error fetching anomalies:', error);
      } finally {
        loading.value = false;
      }
    };
    
    const refreshAnomalies = () => {
      fetchAnomalies();
    };
    
    const formatTime = (timestamp) => {
      if (!timestamp) return '';
      const date = new Date(timestamp);
      return date.toLocaleString();
    };
    
    const viewDetails = (anomaly) => {
      // Emit event to parent component or use router to navigate to details
      // For example:
      // router.push({ name: 'DetailedAnalysis', params: { id: anomaly.id } });
      // Or emit to parent:
      // emit('view-anomaly', anomaly);
      console.log('View details for anomaly:', anomaly);
    };
    
    onMounted(() => {
      fetchAnomalies();
      
      // Connect to socket.io for real-time updates
      socket.value = io('/notifications');
      
      socket.value.on('connect', () => {
        console.log('Connected to notification service');
      });
      
      socket.value.on('new_anomaly', (data) => {
        console.log('New anomaly detected:', data);
        anomalies.value.unshift(data);
      });
      
      socket.value.on('disconnect', () => {
        console.log('Disconnected from notification service');
      });
    });
    
    return {
      anomalies,
      loading,
      alertType,
      filteredAnomalies,
      refreshAnomalies,
      formatTime,
      viewDetails
    };
  }
};
</script>

<style scoped>
.anomaly-panel {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 1rem;
  max-height: 500px;
  overflow-y: auto;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 0.75rem;
}
</style>