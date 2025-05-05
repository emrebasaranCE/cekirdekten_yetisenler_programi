<template>
  <div class="map-container">
    <div id="pollutionMap" class="map"></div>
    <div class="map-controls">
      <div class="map-legend">
        <h3>Air Quality Index</h3>
        <div class="legend-item">
          <div class="color-box bg-green-500"></div>
          <span>Good (0-50)</span>
        </div>
        <div class="legend-item">
          <div class="color-box bg-yellow-400"></div>
          <span>Moderate (51-100)</span>
        </div>
        <div class="legend-item">
          <div class="color-box bg-orange-500"></div>
          <span>Unhealthy for Sensitive Groups (101-150)</span>
        </div>
        <div class="legend-item">
          <div class="color-box bg-red-500"></div>
          <span>Unhealthy (151-200)</span>
        </div>
        <div class="legend-item">
          <div class="color-box bg-purple-700"></div>
          <span>Very Unhealthy (201-300)</span>
        </div>
        <div class="legend-item">
          <div class="color-box bg-red-900"></div>
          <span>Hazardous (301+)</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import axios from 'axios';

export default {
  name: 'PollutionMap',
  data() {
    return {
      map: null,
      heatmapLayer: null,
      markers: [],
      pollutionData: [],
      markerLayer: null
    };
  },
  mounted() {
    this.initMap();
    this.fetchHeatmapData();
    
    // Set up polling to refresh data every 2 minutes
    this.dataRefreshInterval = setInterval(() => {
      this.fetchHeatmapData();
    }, 120000);
  },
  beforeUnmount() {
    if (this.dataRefreshInterval) {
      clearInterval(this.dataRefreshInterval);
    }
    
    if (this.map) {
      this.map.remove();
    }
  },
  methods: {
    initMap() {
      // Create map instance centered on Turkey
      this.map = L.map('pollutionMap').setView([39.925533, 32.866287], 6);
      
      // Add the OpenStreetMap tile layer
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 18
      }).addTo(this.map);
      
      // Create a layer group for markers
      this.markerLayer = L.layerGroup().addTo(this.map);
    },
    
    fetchHeatmapData() {
        axios.get('http://localhost:5003/api/v1/heatmap')
        .then(response => {
          this.pollutionData = response.data.data;
          this.updateMap();
        })
        .catch(error => {
          console.error('Error fetching heatmap data:', error);
        });
    },
    
    updateMap() {
      // Clear existing markers
      this.markerLayer.clearLayers();
      
      // Add new markers based on pollution data
      this.pollutionData.forEach(point => {
        const { latitude, longitude, aqi, pm25, pm10, station_name } = point;
        
        // Determine marker color based on AQI
        const color = this.getColorByAQI(aqi);
        
        // Create circle marker
        const marker = L.circleMarker([latitude, longitude], {
          radius: 10,
          fillColor: color,
          color: '#000',
          weight: 1,
          opacity: 1,
          fillOpacity: 0.8
        });
        
        // Add popup with station information
        marker.bindPopup(`
          <strong>${station_name}</strong><br>
          AQI: ${aqi}<br>
          PM2.5: ${pm25} μg/m³<br>
          PM10: ${pm10} μg/m³
        `);
        
        marker.addTo(this.markerLayer);
      });
    },
    
    getColorByAQI(aqi) {
      // Return color based on AQI value
      if (aqi <= 50) return '#10B981'; // Green (Good)
      if (aqi <= 100) return '#FBBF24'; // Yellow (Moderate)
      if (aqi <= 150) return '#F97316'; // Orange (Unhealthy for sensitive groups)
      if (aqi <= 200) return '#EF4444'; // Red (Unhealthy)
      if (aqi <= 300) return '#7E22CE'; // Purple (Very unhealthy)
      return '#7F1D1D';                 // Dark red (Hazardous)
    }
  }
};
</script>

<style scoped>
.map-container {
  position: relative;
  width: 100%;
  height: 500px;
}

.map {
  width: 100%;
  height: 100%;
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.map-controls {
  position: absolute;
  bottom: 20px;
  right: 20px;
  background-color: white;
  padding: 10px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.map-legend h3 {
  margin-top: 0;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: bold;
}

.legend-item {
  display: flex;
  align-items: center;
  margin-bottom: 4px;
  font-size: 12px;
}

.color-box {
  width: 16px;
  height: 16px;
  margin-right: 6px;
  border: 1px solid #333;
}
</style>