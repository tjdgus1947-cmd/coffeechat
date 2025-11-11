// File: tjdgus1947-cmd/coffeechat/coffeechat-db-ksh/frontend/src/services/userService.js

import api from './api';

const userService = {
  /**
   * 멘토 또는 멘티의 위치 정보를 백엔드에 업데이트합니다.
   * POST /api/location/update
   * (wbs.md 1.2 시스템 아키텍처 설계 및 5.2 지도 뷰)
   * @param {string} userId - public.users.id
   * @param {string} role - 'mentee' 또는 'mentor'
   * @param {number} lon - 경도 (Longitude)
   * @param {number} lat - 위도 (Latitude)
   * @returns {Promise<object>} 응답 메시지
   */
  updateLocation(userId, role, lon, lat) {
    // backend/app/api/location.py의 LocationUpdateRequest 스키마에 맞춥니다.
    return api.post('/location/update', {
      user_id: userId,
      role: role,
      lon: lon,
      lat: lat,
    });
  },
  
  // (향후 프로필 수정 등 다른 사용자 관련 API를 여기에 추가할 예정입니다.)
};

export default userService;