<template>
  <div class="mentor-map-container">
    <!-- 카카오맵 컨테이너 -->
    <div id="kakao-map" class="kakao-map"></div>
    
    <!-- 로딩 오버레이 -->
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
      <p>지도 로딩 중...</p>
    </div>
    
    <!-- 에러 메시지 -->
    <div v-if="error" class="error-banner">
      ⚠️ {{ error }}
    </div>
    
    <!-- 내 위치로 이동 버튼 -->
    <button v-if="!loading && menteeLocation" @click="moveToMyLocation" class="my-location-btn" title="내 위치로 이동">
      📍
    </button>
    
    <!-- 범례 (Legend) -->
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
      loading: true,
      error: null,
      userId: null,
      mentorCount: 0,
      menteeLocation: null // 멘티 위치 저장
    };
  },
  
  mounted() {
    // 로그인한 사용자 ID 가져오기
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    this.userId = userData.id;
    
    if (!this.userId) {
      this.error = '로그인이 필요합니다.';
      this.loading = false;
      return;
    }
    
    // 카카오맵 API 로드
    this.loadKakaoMapScript();
  },
  
  methods: {
    // 카카오맵 API 스크립트 동적 로드
    loadKakaoMapScript() {
      // 이미 로드되었는지 확인
      if (window.kakao && window.kakao.maps) {
        this.initializeMap();
        return;
      }
      
      // 카카오맵 API 스크립트 추가
      const script = document.createElement('script');
      script.src = '//dapi.kakao.com/v2/maps/sdk.js?appkey=a37ab17958bf71b653513edd08f31fac&autoload=false';
      script.onload = () => {
        window.kakao.maps.load(() => {
          this.initializeMap();
        });
      };
      script.onerror = () => {
        this.error = '카카오맵 API 로드 실패. 네트워크를 확인해주세요.';
        this.loading = false;
      };
      document.head.appendChild(script);
    },
    
    // 카카오맵 초기화
    async initializeMap() {
      try {
        // 백엔드에서 위치 데이터 가져오기
        const response = await axios.get(
          `http://localhost:8000/api/locations/map-data/${this.userId}`
        );
        
        const { mentee_location, mentor_locations } = response.data;
        
        // 멘티 위치 저장
        this.menteeLocation = mentee_location;
        
        // 멘토 수 업데이트
        this.mentorCount = mentor_locations?.length || 0;
        
        // 기본 중심 좌표 (멘티 위치 또는 서울 시청)
        const centerLat = mentee_location?.lat || 37.5665;
        const centerLon = mentee_location?.lon || 126.9780;
        
        // 카카오맵 생성
        const container = document.getElementById('kakao-map');
        const options = {
          center: new window.kakao.maps.LatLng(centerLat, centerLon),
          level: 8 // 확대 레벨 (1~14)
        };
        
        this.map = new window.kakao.maps.Map(container, options);
        
        // 지도 컨트롤 추가
        const zoomControl = new window.kakao.maps.ZoomControl();
        this.map.addControl(zoomControl, window.kakao.maps.ControlPosition.RIGHT);
        
        // 지도 타입 컨트롤 추가 (일반/스카이뷰)
        const mapTypeControl = new window.kakao.maps.MapTypeControl();
        this.map.addControl(mapTypeControl, window.kakao.maps.ControlPosition.TOPRIGHT);
        
        // 멘티 마커 추가 (파란색)
        if (mentee_location) {
          this.addMarker(
            mentee_location.lat,
            mentee_location.lon,
            mentee_location.name,
            'mentee'
          );
        }
        
        // 멘토 마커 추가 (초록색)
        if (mentor_locations && mentor_locations.length > 0) {
          mentor_locations.forEach(mentor => {
            this.addMarker(
              mentor.lat,
              mentor.lon,
              mentor.name,
              'mentor'
            );
          });
        }
        
        this.loading = false;
        
      } catch (err) {
        console.error('지도 데이터 로드 실패:', err);
        this.error = err.response?.data?.detail || '위치 데이터를 불러올 수 없습니다.';
        this.loading = false;
      }
    },
    
    // 마커 추가 함수 (이미지 대신 원형 마커 사용)
    addMarker(lat, lon, name, role) {
      const position = new window.kakao.maps.LatLng(lat, lon);
      
      // ⭐️ 이미지 마커 대신 원형 커스텀 오버레이 사용
      const content = document.createElement('div');
      content.style.cssText = `
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background-color: ${role === 'mentee' ? '#4A90E2' : '#27AE60'};
        border: 3px solid white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
      `;
      content.innerHTML = role === 'mentee' ? '📍' : '☕';
      
      // 커스텀 오버레이 생성
      const overlay = new window.kakao.maps.CustomOverlay({
        position: position,
        content: content,
        yAnchor: 1
      });
      
      overlay.setMap(this.map);
      
      // 인포윈도우 생성
      const roleText = role === 'mentee' ? '나의 위치' : '멘토';
      const infowindow = new window.kakao.maps.InfoWindow({
        content: `<div style="padding:8px 12px; font-size:13px; background:white; border-radius:8px;">
                    <strong style="color: ${role === 'mentee' ? '#4A90E2' : '#27AE60'};">
                      ${role === 'mentee' ? '📍' : '☕'} ${roleText}
                    </strong><br/>
                    <span style="color: #666;">${name}</span>
                  </div>`,
        removable: false
      });
      
      // 클릭 이벤트
      content.addEventListener('click', () => {
        // 다른 인포윈도우 닫기
        this.markers.forEach(({ infowindow: iw }) => iw.close());
        infowindow.open(this.map, overlay);
      });
      
      // 호버 이벤트
      content.addEventListener('mouseenter', () => {
        infowindow.open(this.map, overlay);
      });
      
      content.addEventListener('mouseleave', () => {
        infowindow.close();
      });
      
      this.markers.push({ overlay, infowindow });
    },
    
    // ⭐️ 내 위치로 이동
    moveToMyLocation() {
      if (!this.menteeLocation || !this.map) return;
      
      const moveLatLon = new window.kakao.maps.LatLng(
        this.menteeLocation.lat,
        this.menteeLocation.lon
      );
      
      // 부드럽게 이동
      this.map.panTo(moveLatLon);
      
      // 줌 레벨 조정 (더 가까이)
      setTimeout(() => {
        this.map.setLevel(5);
      }, 300);
    }
  },
  
  beforeUnmount() {
    // 마커 정리
    this.markers.forEach(({ overlay }) => {
      overlay.setMap(null);
    });
    this.markers = [];
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

.kakao-map {
  width: 100%;
  height: 100%;
}

/* 로딩 오버레이 */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.95);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #6c5ce7;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-overlay p {
  margin-top: 20px;
  font-size: 15px;
  color: #666;
  font-weight: 500;
}

/* 에러 배너 */
.error-banner {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: #ff6b6b;
  color: white;
  padding: 14px 28px;
  border-radius: 10px;
  box-shadow: 0 4px 16px rgba(255, 107, 107, 0.3);
  z-index: 1000;
  font-size: 14px;
  font-weight: 500;
  max-width: 90%;
}

/* ⭐️ 내 위치로 이동 버튼 */
.my-location-btn {
  position: absolute;
  bottom: 120px;
  right: 20px;
  width: 50px;
  height: 50px;
  background: white;
  border: 2px solid #4A90E2;
  border-radius: 50%;
  font-size: 24px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 500;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.my-location-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(74, 144, 226, 0.3);
  background: #4A90E2;
}

/* 범례 */
.map-legend {
  position: absolute;
  bottom: 30px;
  left: 20px;
  background: white;
  padding: 16px;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  z-index: 500;
  font-size: 14px;
}

.legend-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.legend-item:last-child {
  margin-bottom: 0;
}

.legend-icon {
  font-size: 20px;
  margin-right: 10px;
  width: 24px;
  text-align: center;
}

/* 반응형 */
@media (max-width: 768px) {
  .map-legend {
    bottom: 20px;
    left: 10px;
    padding: 12px;
    font-size: 12px;
  }
  
  .legend-icon {
    font-size: 18px;
    margin-right: 8px;
  }
  
  .my-location-btn {
    bottom: 100px;
    right: 15px;
    width: 45px;
    height: 45px;
    font-size: 20px;
  }
}
</style>