<template>
  <div class="location-card card">
    <h2>나의 위치 정보 설정  </h2>
    <p class="info-text">
      지리적 매칭도(거리 30%)를 계산하기 위해 위치 정보가 필요합니다.
    </p>

    <!-- 우편번호 검색 -->
    <div class="search-section">
      <h3 class="section-title">📮 우편번호로 주소 찾기</h3>
      <div class="form-group">
        <button @click="openDaumPostcode" class="search-button daum-button">
          우편번호 찾기
        </button>
      </div>
    </div>

    <!-- 주소 직접 검색 -->
    <div class="search-section">
      <h3 class="section-title">🔍 주소로 직접 검색 </h3>
      <div class="form-group">
        <label>우편번호 검색 후, 동/호수 등 상세 주소를 입력하세요.</label>
        <div class="search-container">
          <input
            type="text"
            v-model="searchAddress"
            @keyup.enter="searchLocation"
            placeholder="예: 서울특별시 강남구 테헤란로 123"
            class="address-input"
          />
          <button @click="searchLocation" class="search-button" :disabled="isSearching">
            {{ isSearching ? '검색 중...' : '주소 검색' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 검색 결과 -->
    <div v-if="searchResults.length > 0" class="search-results">
      <h3>📍 주소 검색 결과 (좌표 선택)</h3>
      <p class="info-text small">검색된 주소를 클릭하여 좌표를 확정하세요.</p>

      <div
        v-for="(result, index) in searchResults"
        :key="index"
        class="result-item"
        @click="selectAddress(result)"
      >
        <div class="result-address">{{ result.address_name }}</div>
        <div class="result-road" v-if="result.road_address">
          🛣️ {{ result.road_address.address_name }}
        </div>
        <div class="result-zip" v-if="result.road_address && result.road_address.zone_no">
          📮 우편번호: {{ result.road_address.zone_no }}
        </div>
      </div>
    </div>

    <!-- 위도/경도 입력 -->
    <div class="coordinate-form">
      <div class="form-row">
        <div class="form-group">
          <label>위도 (Latitude)</label>
          <input
            type="number"
            step="0.0001"
            v-model.number="latitude"
            placeholder="37.4979"
            :disabled="isUpdating"
          />
        </div>
        <div class="form-group">
          <label>경도 (Longitude)</label>
          <input
            type="number"
            step="0.0001"
            v-model.number="longitude"
            placeholder="127.0276"
            :disabled="isUpdating"
          />
        </div>
      </div>

      <button
        @click="updateLocation"
        class="update-button"
        :disabled="isUpdating || !latitude || !longitude"
      >
        {{ isUpdating ? '업데이트 중...' : '위치 정보 업데이트' }}
      </button>
    </div>

    <!-- 안내/메시지 -->
    <div v-if="latitude && longitude" class="test-info">
      테스트 값 추천: {{ testLocationName }} (위도: {{ latitude }}, 경도: {{ longitude }})
    </div>

    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    <p v-if="successMessage" class="success-message">{{ successMessage }}</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '@/store/auth';
import axios from 'axios';

const authStore = useAuthStore();

const searchAddress = ref('');
const searchResults = ref([]);
const isSearching = ref(false);

const latitude = ref(null);
const longitude = ref(null);
const isUpdating = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

// ⭐️ 카카오맵 APP KEY (MentorMap.vue에서 가져옴)
const KAKAO_APP_KEY = 'a37ab17958bf71b653513edd08f31fac';

// ⭐️ 1. Kakao 맵 스크립트 로드 (Geocoder 라이브러리 포함)
const loadKakaoMapScript = () => {
  return new Promise((resolve, reject) => {
    if (window.kakao && window.kakao.maps) {
      resolve();
      return;
    }
    const script = document.createElement('script');
    // ⭐️ 주소 검색을 위해 &libraries=services 추가
    script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${KAKAO_APP_KEY}&libraries=services&autoload=false`;
    script.onload = () => {
      window.kakao.maps.load(() => resolve());
    };
    script.onerror = () => reject(new Error('카카오맵 스크립트 로드 실패'));
    document.head.appendChild(script);
  });
};

// Daum 우편번호 스크립트 로드
const loadDaumPostcodeScript = () => {
  return new Promise((resolve) => {
    if (window.daum && window.daum.Postcode) {
      resolve();
      return;
    }
    const script = document.createElement('script');
    script.src = '//t1.daumcdn.net/mapjsapi/bundle/postcode/prod/postcode.v2.js';
    script.onload = () => resolve();
    document.head.appendChild(script);
  });
};

onMounted(async () => {
  try {
    // ⭐️ 두 스크립트를 모두 로드
    await loadDaumPostcodeScript();
    await loadKakaoMapScript();
  } catch (error) {
    errorMessage.value = "지도 서비스 로드에 실패했습니다.";
  }
});

// 우편번호 팝업 (기존 코드와 동일)
const openDaumPostcode = () => {
  if (!window.daum || !window.daum.Postcode) {
    errorMessage.value = '우편번호 검색 서비스를 로드 중입니다. 잠시 후 다시 시도해주세요.';
    loadDaumPostcodeScript();
    return;
  }

  new window.daum.Postcode({
    oncomplete: (data) => {
      let addr = '';
      if (data.userSelectedType === 'R') {
        addr = data.roadAddress;
      } else {
        addr = data.jibunAddress;
      }
      searchAddress.value = addr;
      searchLocation(); // 자동 검색
    },
  }).open();
};

const testLocationName = computed(() => {
  if (latitude.value && longitude.value) {
    return `위도 ${latitude.value}, 경도 ${longitude.value}`;
  }
  return '';
});

// ⭐️ 2. 주소 → 좌표 검색 (백엔드 대신 카카오 Geocoder 사용)
const searchLocation = async () => {
  if (!searchAddress.value.trim()) {
    errorMessage.value = '주소를 입력해주세요.';
    return;
  }
  if (!window.kakao || !window.kakao.maps || !window.kakao.maps.services) {
    errorMessage.value = '카카오맵 서비스가 로드되지 않았습니다. 페이지를 새로고침해주세요.';
    return;
  }

  isSearching.value = true;
  errorMessage.value = '';
  searchResults.value = [];

  try {
    // ⭐️ 카카오 Geocoder 생성
    const geocoder = new window.kakao.maps.services.Geocoder();

    // ⭐️ Geocoder는 콜백 기반이므로 Promise로 변환
    const searchPromise = () => new Promise((resolve, reject) => {
      geocoder.addressSearch(searchAddress.value, (result, status) => {
        if (status === window.kakao.maps.services.Status.OK) {
          resolve(result); // result는 주소 객체 배열
        } else if (status === window.kakao.maps.services.Status.ZERO_RESULT) {
           resolve([]); // 검색 결과가 없는 경우 빈 배열 반환
        } else {
          reject(new Error('주소 검색 실패'));
        }
      });
    });

    const docs = await searchPromise(); // ⭐️ axios.get 대신 Kakao API 호출

    if (docs.length === 0) {
      errorMessage.value = '검색 결과가 없습니다. 주소를 다시 확인해주세요.';
    } else {
      searchResults.value = docs;
    }
  } catch (error) {
    console.error('주소 검색 실패:', error);
    errorMessage.value = '주소 검색에 실패했습니다. (카카오 API 오류)';
  } finally {
    isSearching.value = false;
  }
};

// 검색 결과 선택
const selectAddress = (result) => {
  // ⭐️ 카카오 Geocoder는 x, y를 문자열로 줍니다. float으로 변환.
  latitude.value = parseFloat(result.y);
  longitude.value = parseFloat(result.x);

  successMessage.value = `좌표가 선택되었습니다: ${result.address_name}`;
  searchResults.value = [];

  setTimeout(() => {
    successMessage.value = '';
  }, 3000);
};

// 위치 업데이트 (기존 코드와 동일)
const updateLocation = async () => {
  if (!latitude.value || !longitude.value) {
    errorMessage.value = '위도와 경도를 입력해주세요.';
    return;
  }
  if (!authStore.userId || !authStore.userRole) {
    errorMessage.value = '사용자 정보를 찾을 수 없습니다. 다시 로그인해주세요.';
    return;
  }

  isUpdating.value = true;
  errorMessage.value = '';
  successMessage.value = '';

  try {
    // ⭐️ 이 API는 백엔드 API가 맞습니다! (location.py에 존재함)
    const response = await axios.post('http://localhost:8000/api/location/update', {
      user_id: authStore.userId,
      role: authStore.userRole,
      lat: latitude.value,
      lon: longitude.value,
    });

    console.log('✅ 위치 업데이트 성공:', response.data);
    successMessage.value = '위치 정보가 성공적으로 업데이트되었습니다! ✅';

    setTimeout(() => {
      successMessage.value = '';
    }, 3000);
  } catch (error) {
    console.error('❌ 위치 업데이트 실패:', error);
    console.error('에러 상세:', error.response?.data);
    errorMessage.value = error.response?.data?.detail || '위치 업데이트에 실패했습니다.';
  } finally {
    isUpdating.value = false;
  }
};
</script>

<style scoped>
.location-card {
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.info-text {
  color: #666;
  font-size: 0.95rem;
  margin-bottom: 24px;
  line-height: 1.5;
}
.info-text.small {
  font-size: 0.9rem;
  margin-bottom: 10px;
  padding: 0 16px;
}

.search-section {
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}
.search-section:last-of-type {
  border-bottom: none;
}

.section-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 12px;
}

.form-group {
  margin-bottom: 16px;
}
.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 600;
  color: #333;
}

.search-container {
  display: flex;
  gap: 10px;
}

.address-input {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
}
.address-input:focus {
  outline: none;
  border-color: #6d28d9;
  box-shadow: 0 0 0 3px rgba(109, 40, 217, 0.1);
}

.search-button {
  padding: 10px 20px;
  background-color: #6d28d9;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  white-space: nowrap;
}
.search-button:hover:not(:disabled) {
  background-color: #5b21b6;
}
.search-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.daum-button {
  background-color: #6d28d9;
  width: 100%;
  font-size: 1.05rem;
}
.daum-button:hover:not(:disabled) {
  background-color: #6d28d9;
}

.search-results {
  margin: 20px 0;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  animation: slideDown 0.3s ease-out;
}
@keyframes slideDown {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
.search-results h3 {
  background-color: #f8f9fa;
  padding: 12px 16px;
  margin: 0;
  font-size: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.result-item {
  padding: 14px 16px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  transition: all 0.2s;
}
.result-item:last-child { border-bottom: none; }
.result-item:hover { background-color: #f8f9fa; transform: translateX(4px); }

.result-address {
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}
.result-road {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 4px;
}
.result-zip {
  font-size: 0.85rem;
  color: #6d28d9;
  font-weight: 600;
}

.coordinate-form { margin-top: 24px; }
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}
.form-group input[type="number"] {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
}
.form-group input[type="number"]:focus {
  outline: none;
  border-color: #6d28d9;
  box-shadow: 0 0 0 3px rgba(109, 40, 217, 0.1);
}

.update-button {
  width: 100%;
  padding: 12px;
  background-color: #6d28d9;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}
.update-button:hover:not(:disabled) { background-color: #5b21b6; }
.update-button:disabled { background-color: #ccc; cursor: not-allowed; }

.test-info {
  margin-top: 16px;
  padding: 12px;
  background-color: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 6px;
  color: #0369a1;
  font-size: 0.9rem;
}

.error-message {
  margin-top: 16px;
  padding: 12px;
  background-color: #fee;
  border: 1px solid #fcc;
  border-radius: 6px;
  color: #c00;
  font-size: 0.95rem;
}
.success-message {
  margin-top: 16px;
  padding: 12px;
  background-color: #d4edda;
  border: 1px solid #c3e6cb;
  border-radius: 6px;
  color: #155724;
  font-size: 0.95rem;
  font-weight: 600;
}

@media (max-width: 768px) {
  .form-row { grid-template-columns: 1fr; }
  .search-container { flex-direction: column; }
  .search-button { width: 100%; }
}
</style>
