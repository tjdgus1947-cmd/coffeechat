<template>
  <div class="mentor-map-container">
    <div id="kakao-map" class="kakao-map"></div>
    
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
      <p>지도 로딩 중...</p>
    </div>
    
    <div v-if="error" class="error-banner">
      ⚠️ {{ error }}
    </div>
    
    <button v-if="!loading && menteeLocation" @click="moveToMyLocation" class="my-location-btn" title="내 위치로 이동">
      📍
    </button>
    
    <div class="map-legend">
      <div class="legend-item">
        <span class="legend-icon mentee">🔵</span>
        <span>나의 위치</span>
      </div>
      <div class="legend-item">
        <span class="legend-icon mentor">🟢</span>
        <span>멘토 ({{ mentorCount }}명)</span>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'MentorMap',
  data() {
    return {
      map: null,
      markers: [],
      polylines: [],
      loading: true,
      error: null,
      userId: null,
      mentorCount: 0,
      menteeLocation: null
    };
  },
  
  mounted() {
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    this.userId = userData.id;
    
    if (!this.userId) {
      this.error = '로그인이 필요합니다.';
      this.loading = false;
      return;
    }
    
    this.loadKakaoMapScript();
  },
  
  methods: {
    loadKakaoMapScript() {
      if (window.kakao && window.kakao.maps) {
        this.$nextTick(() => this.initializeMap());
        return;
      }
      
      const script = document.createElement('script');
      script.src = '//dapi.kakao.com/v2/maps/sdk.js?appkey=a37ab17958bf71b653513edd08f31fac&autoload=false';
      script.onload = () => {
        window.kakao.maps.load(() => {
          this.$nextTick(() => this.initializeMap());
        });
      };
      script.onerror = () => {
        this.error = '카카오맵 API 로드 실패. 네트워크를 확인해주세요.';
        this.loading = false;
      };
      document.head.appendChild(script);
    },
    
    async initializeMap() {
      try {
        const container = document.getElementById('kakao-map');
        if (!container) {
          this.error = "지도 DOM 요소를 찾는 데 실패했습니다.";
          this.loading = false;
          return;
        }

        const response = await axios.get(
          `http://localhost:8000/api/locations/map-data/${this.userId}`
        );
        
        this.loading = false; 
        
        const { mentee_location, mentor_locations } = response.data;
        
        this.menteeLocation = mentee_location;
        this.mentorCount = mentor_locations?.length || 0;
        
        const centerLat = mentee_location?.lat || 37.5665;
        const centerLon = mentee_location?.lon || 126.9780;
        
        const options = {
          center: new window.kakao.maps.LatLng(centerLat, centerLon),
          level: 8
        };
        
        this.map = new window.kakao.maps.Map(container, options);
        
        const zoomControl = new window.kakao.maps.ZoomControl();
        this.map.addControl(zoomControl, window.kakao.maps.ControlPosition.RIGHT);
        
        const mapTypeControl = new window.kakao.maps.MapTypeControl();
        this.map.addControl(mapTypeControl, window.kakao.maps.ControlPosition.TOPRIGHT);

        window.kakao.maps.event.addListener(this.map, 'click', () => {
          this.markers.forEach(({ infowindow }) => infowindow.close());
        });
        
        if (mentee_location) {
          this.addMarker(
            mentee_location.lat,
            mentee_location.lon,
            mentee_location.name,
            'mentee'
          );
        }
        
        if (mentor_locations && mentor_locations.length > 0) {
          mentor_locations.forEach(mentor => {
            this.addMarker(mentor.lat, mentor.lon, mentor.name, 'mentor');
          });
        }
        
        this.drawMentorLines(mentee_location, mentor_locations);
        
      } catch (err) {
        console.error('지도 데이터 로드 실패:', err);
        this.loading = false; 
        if (err instanceof TypeError && err.message.includes('currentStyle')) {
            this.error = '지도 DOM 로딩 중 오류가 발생했습니다. 페이지를 새로고침 해주세요.';
        } else {
            this.error = err.response?.data?.detail || '위치 데이터를 불러올 수 없습니다.';
        }
      }
    },
    
    addMarker(lat, lon, name, role) {
      const position = new window.kakao.maps.LatLng(lat, lon);
      
      // 마커 생성
      const content = document.createElement('div');
      content.style.cssText = `
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background-color: ${role === 'mentee' ? '#4A90E2' : '#27AE60'};
        border: 3px solid white;
        box-shadow: 0 3px 10px rgba(0,0,0,0.3);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        transition: transform 0.2s;
      `;
      content.innerHTML = role === 'mentee' ? '📍' : '☕';
      
      const overlay = new window.kakao.maps.CustomOverlay({
        position: position,
        content: content,
        yAnchor: 1
      });
      
      overlay.setMap(this.map);
      
      // 이름 라벨 (항상 표시)
      const labelContent = document.createElement('div');
      labelContent.style.cssText = `
        padding: 6px 12px;
        background: white;
        border: 2px solid ${role === 'mentee' ? '#4A90E2' : '#27AE60'};
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        color: #333;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        white-space: nowrap;
        text-align: center;
      `;
      labelContent.textContent = name;
      
      const labelOverlay = new window.kakao.maps.CustomOverlay({
        position: position,
        content: labelContent,
        yAnchor: 2.3
      });
      
      labelOverlay.setMap(this.map);
      
      // 호버 시 상세 정보 창
      const roleText = role === 'mentee' ? '나의 위치' : '멘토';
      const infowindow = new window.kakao.maps.InfoWindow({
        position: position, 
        content: `<div style="padding:12px 16px; font-size:14px; background:white; border-radius:12px; min-width: 120px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
                    <div style="display: flex; align-items: center; margin-bottom: 6px;">
                      <span style="font-size: 20px; margin-right: 8px;">${role === 'mentee' ? '📍' : '☕'}</span>
                      <strong style="color: ${role === 'mentee' ? '#4A90E2' : '#27AE60'}; font-size: 15px;">
                        ${roleText}
                      </strong>
                    </div>
                    <div style="color: #333; font-weight: 600; font-size: 14px;">${name}</div>
                    ${role === 'mentor' ? '<div style="color: #888; font-size: 12px; margin-top: 4px;">클릭하여 연결</div>' : ''}
                  </div>`,
        removable: false
      });
      
      const openInfoWindow = () => {
        this.markers.forEach(({ infowindow: iw }) => iw.close());
        infowindow.open(this.map);
        content.style.transform = 'scale(1.2)';
      };

      const closeInfoWindow = () => {
        infowindow.close();
        content.style.transform = 'scale(1)';
      };

      content.addEventListener('mouseenter', openInfoWindow);
      content.addEventListener('mouseleave', closeInfoWindow);
      content.addEventListener('click', () => {
        this.map.setLevel(4);
        this.map.panTo(position);
      });
      
      this.markers.push({ overlay, labelOverlay, infowindow });
    },

    drawMentorLines(mentee, mentors) {
      if (!mentee || !mentors || mentors.length === 0 || !this.map) {
        return;
      }

      const menteePosition = new window.kakao.maps.LatLng(mentee.lat, mentee.lon);

      mentors.forEach(mentor => {
        const mentorPosition = new window.kakao.maps.LatLng(mentor.lat, mentor.lon);
        const linePath = [menteePosition, mentorPosition];
        const polyline = new window.kakao.maps.Polyline({
          path: linePath,
          strokeWeight: 2,
          strokeColor: '#6c5ce7',
          strokeOpacity: 0.6,
          strokeStyle: 'dash'
        });
        polyline.setMap(this.map);
        this.polylines.push(polyline);
      });
    },
    
    moveToMyLocation() {
      if (!this.menteeLocation || !this.map) return;
      
      const moveLatLon = new window.kakao.maps.LatLng(
        this.menteeLocation.lat,
        this.menteeLocation.lon
      );
      
      this.map.panTo(moveLatLon);
      
      setTimeout(() => {
        this.map.setLevel(5);
      }, 300);
    }
  },
  
  beforeUnmount() {
    this.markers.forEach(({ overlay, labelOverlay }) => {
      overlay.setMap(null);
      if (labelOverlay) labelOverlay.setMap(null);
    });
    this.markers = [];
    this.polylines.forEach(line => line.setMap(null));
    this.polylines = [];
    
    if (this.map) {
      this.map = null; 
    }
  }
};
</script>

<style scoped>
.mentor-map-container {
  position: relative;
  width: 100%;
  height: calc(100vh - 60px);
  overflow: hidden;
  background: #f5f5f5;
}
.kakao-map { width: 100%; height: 100%; }
.loading-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(255, 255, 255, 0.95); display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 1000; }
.spinner { border: 4px solid #f3f3f3; border-top: 4px solid #6c5ce7; border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.loading-overlay p { margin-top: 20px; font-size: 15px; color: #666; font-weight: 500; }
.error-banner { position: absolute; top: 20px; left: 50%; transform: translateX(-50%); background: #ff6b6b; color: white; padding: 14px 28px; border-radius: 10px; box-shadow: 0 4px 16px rgba(255, 107, 107, 0.3); z-index: 1000; font-size: 14px; font-weight: 500; max-width: 90%; }
.my-location-btn { position: absolute; bottom: 120px; right: 20px; width: 50px; height: 50px; background: white; border: 2px solid #4A90E2; border-radius: 50%; font-size: 24px; cursor: pointer; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); z-index: 500; transition: all 0.3s; display: flex; align-items: center; justify-content: center; }
.my-location-btn:hover { transform: scale(1.1); box-shadow: 0 6px 16px rgba(74, 144, 226, 0.3); background: #4A90E2; }
.map-legend { position: absolute; bottom: 30px; left: 20px; background: white; padding: 16px; border-radius: 12px; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15); z-index: 500; font-size: 14px; }
.legend-item { display: flex; align-items: center; margin-bottom: 8px; }
.legend-item:last-child { margin-bottom: 0; }
.legend-icon { font-size: 20px; margin-right: 10px; width: 24px; text-align: center; }
@media (max-width: 768px) {
  .map-legend { bottom: 20px; left: 10px; padding: 12px; font-size: 12px; }
  .legend-icon { font-size: 18px; margin-right: 8px; }
  .my-location-btn { bottom: 100px; right: 15px; width: 45px; height: 45px; font-size: 20px; }
}
</style>