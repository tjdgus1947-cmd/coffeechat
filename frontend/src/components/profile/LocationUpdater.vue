<template>
  <div class="location-updater-container">
    <p class="info-text">
      나와 가까운 멘토(바리스타)를 찾기 위해<br>
      현재 계신 곳의 위치 정보가 필요합니다.
    </p>

    <div class="search-section">
      <h3 class="section-label">📮 우편번호로 찾기</h3>
      <button @click="openDaumPostcode" class="btn-brown full-width">
        우편번호 검색
      </button>
    </div>

    <div class="search-section">
      <h3 class="section-label">🔍 주소로 직접 검색</h3>
      <div class="input-group">
        <input
          type="text"
          v-model="searchAddress"
          @keyup.enter="searchLocation"
          placeholder="예: 서울특별시 강남구 테헤란로 123"
          class="cafe-input"
        />
        <button @click="searchLocation" class="btn-latte" :disabled="isSearching">
          {{ isSearching ? '...' : '검색' }}
        </button>
      </div>
    </div>

    <div v-if="searchResults.length > 0" class="results-box">
      <p class="box-title">📍 검색 결과 (클릭하여 선택)</p>
      <ul class="result-list">
        <li
          v-for="(result, index) in searchResults"
          :key="index"
          class="result-item"
          @click="selectAddress(result)"
        >
          <div class="addr-main">{{ result.address_name }}</div>
          <div class="addr-sub" v-if="result.road_address">
            {{ result.road_address.address_name }}
          </div>
        </li>
      </ul>
    </div>

    <div class="coordinate-section">
      <div class="coord-row">
        <div class="coord-item">
          <label>위도 (Lat)</label>
          <input type="number" v-model.number="latitude" class="cafe-input" :disabled="isUpdating" />
        </div>
        <div class="coord-item">
          <label>경도 (Lng)</label>
          <input type="number" v-model.number="longitude" class="cafe-input" :disabled="isUpdating" />
        </div>
      </div>

      <button
        @click="updateLocation"
        class="btn-espresso full-width"
        :disabled="isUpdating || !latitude || !longitude"
      >
        {{ isUpdating ? '저장 중...' : '📍 위치 정보 저장하기' }}
      </button>
    </div>

    <p v-if="errorMessage" class="msg error">{{ errorMessage }}</p>
    <p v-if="successMessage" class="msg success">{{ successMessage }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
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

const KAKAO_APP_KEY = 'a37ab17958bf71b653513edd08f31fac';

// 스크립트 로드
const loadKakaoMapScript = () => {
  return new Promise((resolve, reject) => {
    if (window.kakao && window.kakao.maps) { resolve(); return; }
    const script = document.createElement('script');
    script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${KAKAO_APP_KEY}&libraries=services&autoload=false`;
    script.onload = () => window.kakao.maps.load(() => resolve());
    script.onerror = () => reject(new Error('카카오맵 로드 실패'));
    document.head.appendChild(script);
  });
};

const loadDaumPostcodeScript = () => {
  return new Promise((resolve) => {
    if (window.daum && window.daum.Postcode) { resolve(); return; }
    const script = document.createElement('script');
    script.src = '//t1.daumcdn.net/mapjsapi/bundle/postcode/prod/postcode.v2.js';
    script.onload = () => resolve();
    document.head.appendChild(script);
  });
};

onMounted(async () => {
  try {
    await Promise.all([loadDaumPostcodeScript(), loadKakaoMapScript()]);
  } catch (e) { errorMessage.value = "지도 서비스 로드 실패"; }
});

// 우편번호 검색
const openDaumPostcode = () => {
  if (!window.daum || !window.daum.Postcode) return;
  new window.daum.Postcode({
    oncomplete: (data) => {
      searchAddress.value = data.userSelectedType === 'R' ? data.roadAddress : data.jibunAddress;
      searchLocation();
    },
  }).open();
};

// 주소 검색 (좌표 변환)
const searchLocation = async () => {
  if (!searchAddress.value.trim()) return;
  isSearching.value = true;
  searchResults.value = [];
  errorMessage.value = '';

  try {
    const geocoder = new window.kakao.maps.services.Geocoder();
    const searchPromise = () => new Promise((resolve) => {
      geocoder.addressSearch(searchAddress.value, (result, status) => {
        if (status === window.kakao.maps.services.Status.OK) resolve(result);
        else resolve([]);
      });
    });
    const docs = await searchPromise();
    if (docs.length === 0) errorMessage.value = '검색 결과가 없습니다.';
    else searchResults.value = docs;
  } catch (e) {
    errorMessage.value = '주소 검색 실패';
  } finally {
    isSearching.value = false;
  }
};

const selectAddress = (result) => {
  latitude.value = parseFloat(result.y);
  longitude.value = parseFloat(result.x);
  successMessage.value = `좌표 선택됨: ${result.address_name}`;
  searchResults.value = [];
  setTimeout(() => successMessage.value = '', 3000);
};

// 위치 업데이트
const updateLocation = async () => {
  if (!latitude.value || !longitude.value) return;
  isUpdating.value = true;
  try {
    await axios.post('http://localhost:8000/api/location/update', {
      user_id: authStore.userId,
      role: authStore.userRole,
      lat: latitude.value,
      lon: longitude.value,
    });
    successMessage.value = '위치 정보가 저장되었습니다! ☕';
    setTimeout(() => successMessage.value = '', 3000);
  } catch (e) {
    errorMessage.value = '위치 업데이트 실패';
  } finally {
    isUpdating.value = false;
  }
};
</script>

<style scoped>
/* 전체 컨테이너는 부모인 .card 내부로 들어갑니다 */
.location-updater-container {
  padding: 10px 0;
}

.info-text {
  font-size: 0.9rem;
  color: #8d6e63; /* 부드러운 갈색 */
  margin-bottom: 24px;
  line-height: 1.5;
}

.search-section {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px dashed #d7ccc8; /* 점선 구분선 */
}
.search-section:last-of-type { border-bottom: none; }

.section-label {
  font-size: 0.95rem;
  font-weight: 700;
  color: #5d4037;
  margin-bottom: 10px;
}

/* ☕ 입력 필드 스타일 (베이지 톤) */
.cafe-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d7ccc8;
  border-radius: 6px;
  font-size: 0.95rem;
  background-color: #fdfbf7; /* 아주 연한 크림색 */
  color: #4e342e;
  outline: none;
  transition: border-color 0.2s;
}
.cafe-input:focus {
  border-color: #8d6e63;
  background-color: #fff;
  box-shadow: 0 0 0 2px rgba(141, 110, 99, 0.1);
}

.input-group {
  display: flex;
  gap: 8px;
}

/* ☕ 버튼 스타일 모음 */
.btn-brown {
  background-color: #8d6e63; /* 밀크 초콜릿 */
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-brown:hover { background-color: #795548; }

.btn-latte {
  background-color: #bcaaa4; /* 라떼 색 */
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}
.btn-latte:hover { background-color: #a1887f; }

.btn-espresso {
  background-color: #3e2723; /* 에스프레소 (진한 갈색) */
  color: #fff;
  border: none;
  padding: 12px;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
}
.btn-espresso:hover:not(:disabled) { background-color: #281914; }
.btn-espresso:disabled { background-color: #d7ccc8; cursor: not-allowed; }

.full-width { width: 100%; }

/* 검색 결과 박스 */
.results-box {
  background-color: #fafafa;
  border: 1px solid #eee;
  border-radius: 6px;
  margin-bottom: 20px;
  overflow: hidden;
}
.box-title {
  font-size: 0.85rem;
  background: #f5f5f5;
  padding: 8px 12px;
  margin: 0;
  color: #666;
  border-bottom: 1px solid #eee;
}
.result-list {
  list-style: none;
  padding: 0;
  margin: 0;
  max-height: 150px;
  overflow-y: auto;
}
.result-item {
  padding: 10px 12px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
}
.result-item:hover { background-color: #fce4ec; } /* 살짝 핑크빛으로 포인트 */
.addr-main { font-size: 0.9rem; font-weight: bold; color: #333; }
.addr-sub { font-size: 0.8rem; color: #888; }

/* 좌표 입력 섹션 */
.coordinate-section {
  background-color: #fff8e1; /* 연한 노란빛 */
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #ffe0b2;
}
.coord-row {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}
.coord-item { flex: 1; }
.coord-item label {
  display: block; font-size: 0.8rem; font-weight: 700; color: #795548; margin-bottom: 4px;
}

/* 메시지 */
.msg { font-size: 0.9rem; margin-top: 10px; font-weight: 600; text-align: center; }
.msg.error { color: #d32f2f; }
.msg.success { color: #2e7d32; }
</style>