<template>
  <div class="map-container">
    <!-- 로딩 중 -->
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
      <p>지도를 불러오는 중...</p>
    </div>

    <!-- 에러 메시지 -->
    <div v-if="error" class="error-message">
      <p>⚠️ {{ error }}</p>
      <button @click="initializeMap" class="retry-button">다시 시도</button>
    </div>

    <!-- 카카오맵 컨테이너 -->
    <div id="kakao-map" class="kakao-map"></div>

    <!-- 지도 위 정보 패널 -->
    <div v-if="!loading && !error" class="info-panel">
      <div class="info-item">
        <span class="info-icon">📍</span>
        <span class="info-text">내 위치</span>
      </div>
      <div class="info-item">
        <span class="info-icon">☕</span>
        <span class="info-text">{{ userRole === 'mentee' ? '멘토' : '멘티' }}: {{ otherUserCount }}명</span>
      </div>
    </div>

    <!-- 내 위치로 이동 버튼 -->
    <button
      v-if="!loading && !error && currentUserLocation"
      @click="moveToMyLocation"
      class="my-location-button"
      title="내 위치로 이동"
    >
      🎯
    </button>
  </div>
</template>

<script>
import api from '@/services/api';
import { useAuthStore } from '@/store/auth';
import { mapState } from 'pinia';

export default {
  name: 'MentorMap',
  data() {
    return {
      map: null,
      markers: [],
      polylines: [],
      loading: true,
      error: null,
      otherUserCount: 0,
      currentUserLocation: null,
    };
  },

  computed: {
    ...mapState(useAuthStore, ['userId', 'userRole'])
  },

  mounted() {
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
      script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${import.meta.env.VITE_KAKAO_MAP_KEY}&autoload=false`;
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
          this.error = '지도 DOM 요소를 찾는 데 실패했습니다.';
          this.loading = false;
          return;
        }

        const res = await api.get(`/locations/map-data/${this.userId}`);
        
        const { mentee_location, mentor_locations } = res.data;

        this.currentUserLocation = mentee_location;
        this.otherUserCount = mentor_locations?.length || 0;

        const centerLat = mentee_location?.lat || 37.5665;
        const centerLon = mentee_location?.lon || 126.9780;

        // loading을 먼저 false로 변경하여 지도 컨테이너가 완전히 표시되도록 함
        this.loading = false;

        // DOM이 완전히 렌더링된 후 지도 초기화
        await this.$nextTick();
        await new Promise(resolve => setTimeout(resolve, 50));

        const options = {
          center: new window.kakao.maps.LatLng(centerLat, centerLon),
          level: 8,
        };

        this.map = new window.kakao.maps.Map(container, options);

        const zoomControl = new window.kakao.maps.ZoomControl();
        this.map.addControl(zoomControl, window.kakao.maps.ControlPosition.RIGHT);

        const mapTypeControl = new window.kakao.maps.MapTypeControl();
        this.map.addControl(mapTypeControl, window.kakao.maps.ControlPosition.TOPRIGHT);

        window.kakao.maps.event.addListener(this.map, 'click', () => {
          this.markers.forEach(({ infowindow }) => infowindow.close());
        });

        if (this.currentUserLocation) {
          this.addMarker(
            this.currentUserLocation.lat,
            this.currentUserLocation.lon,
            this.currentUserLocation.name,
            this.currentUserLocation.role
          );
        }

        if (mentor_locations && mentor_locations.length > 0) {
          mentor_locations.forEach((user) => {
            this.addMarker(user.lat, user.lon, user.name, user.role);
          });
        }

        this.drawMentorLines(this.currentUserLocation, mentor_locations);

        // 지도 타일 강제 새로고침
        setTimeout(() => {
          this.map.relayout();
          this.map.setCenter(new window.kakao.maps.LatLng(centerLat, centerLon));
        }, 100);

        setTimeout(() => {
          this.map.relayout();
        }, 500);

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

      const isMentee = role === 'mentee';
      const bgColor = isMentee ? '#4A90E2' : '#27AE60';
      const icon = isMentee ? '📍' : '☕';
      const isCurrentUser = this.userRole === role;

      const content = document.createElement('div');
      content.style.cssText = `
        width: ${isCurrentUser ? '40px' : '36px'};
        height: ${isCurrentUser ? '40px' : '36px'};
        border-radius: 50%;
        background-color: ${bgColor};
        border: ${isCurrentUser ? '4px solid #fff' : '3px solid white'};
        box-shadow: 0 3px 10px rgba(0,0,0,0.3);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: ${isCurrentUser ? '20px' : '18px'};
        transition: transform 0.2s;
        z-index: ${isCurrentUser ? 10 : 1};
      `;
      content.innerHTML = icon;

      const overlay = new window.kakao.maps.CustomOverlay({
        position,
        content,
        yAnchor: 1,
      });
      overlay.setMap(this.map);

      const labelContent = document.createElement('div');
      labelContent.style.cssText = `
        padding: 6px 12px;
        background: white;
        border: 2px solid ${bgColor};
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
        position,
        content: labelContent,
        yAnchor: isCurrentUser ? 2.5 : 2.3,
      });
      labelOverlay.setMap(this.map);

      const roleText = isCurrentUser ? '나의 위치' : isMentee ? '멘티' : '멘토';
      const infowindow = new window.kakao.maps.InfoWindow({
        position,
        content: `
          <div style="padding:12px 16px; font-size:14px; background:white; border-radius:12px; min-width:120px; box-shadow:0 4px 12px rgba(0,0,0,0.15);">
            <div style="display:flex; align-items:center; margin-bottom:6px;">
              <span style="font-size:20px; margin-right:8px;">${icon}</span>
              <strong style="color:${bgColor}; font-size:15px;">${roleText}</strong>
            </div>
            <div style="color:#333; font-weight:600; font-size:14px;">${name}</div>
            ${!isCurrentUser ? '<div style="color:#888; font-size:12px; margin-top:4px;">클릭하여 연결</div>' : ''}
          </div>
        `,
        removable: false,
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

    drawMentorLines(currentUser, otherUsers) {
      if (!currentUser || !otherUsers || otherUsers.length === 0 || !this.map) return;

      const currentUserPosition = new window.kakao.maps.LatLng(currentUser.lat, currentUser.lon);

      otherUsers.forEach((user) => {
        const userPosition = new window.kakao.maps.LatLng(user.lat, user.lon);
        const polyline = new window.kakao.maps.Polyline({
          path: [currentUserPosition, userPosition],
          strokeWeight: 2,
          strokeColor: '#6c5ce7',
          strokeOpacity: 0.6,
          strokeStyle: 'dash',
        });
        polyline.setMap(this.map);
        this.polylines.push(polyline);
      });
    },

    moveToMyLocation() {
      if (!this.currentUserLocation || !this.map) return;

      const moveLatLon = new window.kakao.maps.LatLng(
        this.currentUserLocation.lat,
        this.currentUserLocation.lon
      );

      this.map.panTo(moveLatLon);

      setTimeout(() => {
        this.map.setLevel(5);
      }, 300);
    },
  },

  beforeUnmount() {
    this.markers.forEach(({ overlay, labelOverlay }) => {
      overlay.setMap(null);
      if (labelOverlay) labelOverlay.setMap(null);
    });
    this.markers = [];
    this.polylines.forEach((line) => line.setMap(null));
    this.polylines = [];
    if (this.map) this.map = null;
  },
};
</script>

<style scoped>
.map-container {
  position: relative;
  width: 100%;
  height: 100%;
  background-color: #f0f0f0;
}

.kakao-map {
  width: 100%;
  height: 100%;
  min-height: 600px; /* ← 추가 */
}


/* 로딩 오버레이 */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #e0e0e0;
  border-top-color: #6d28d9;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-overlay p {
  margin-top: 16px;
  font-size: 16px;
  color: #666;
}

/* 에러 메시지 */
.error-message {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  text-align: center;
  z-index: 1000;
}

.error-message p {
  color: #e53e3e;
  font-size: 16px;
  margin-bottom: 16px;
}

.retry-button {
  background-color: #6d28d9;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

.retry-button:hover {
  background-color: #5b21b6;
}

/* 정보 패널 */
.info-panel {
  position: absolute;
  top: 20px;
  left: 20px;
  background: white;
  padding: 16px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  z-index: 100;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-icon {
  font-size: 20px;
  margin-right: 8px;
}

.info-text {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

/* 내 위치 버튼 */
.my-location-button {
  position: absolute;
  bottom: 80px;
  right: 20px;
  width: 50px;
  height: 50px;
  background: white;
  border: 2px solid #6d28d9;
  border-radius: 50%;
  font-size: 24px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  z-index: 100;
  transition: transform 0.2s, background-color 0.2s;
}

.my-location-button:hover {
  transform: scale(1.1);
  background-color: #f0ebff;
}

.my-location-button:active {
  transform: scale(0.95);
}
</style>