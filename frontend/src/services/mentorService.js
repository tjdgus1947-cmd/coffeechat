import api from './api';

const mentorService = {
  /**
   * 멘티 ID를 기반으로 네트워크 그래프 데이터를 가져옵니다. (wbs_detail.md 기반)
   * @param {string} menteeId - 현재 로그인한 멘티의 ID
   * @returns {Promise<object>} { nodes, edges, recommendedMentors }
   */
  getNetworkData(menteeId) {
    // wbs_detail.md 기반 엔드포인트
    return api.get(`/network/${menteeId}`);
  },

  /**
   * 특정 멘토의 상세 정보를 가져옵니다. (wbs_detail.md 기반)
   * @param {string} mentorId - 멘토 ID
   * @returns {Promise<object>} 멘토 상세 정보
   */
  getMentorById(mentorId) {
    // wbs_detail.md 기반 엔드포인트
    return api.get(`/mentors/${mentorId}`);
  },

  /**
   * 멘토의 가능한 예약 시간을 가져옵니다. (wbs_detail.md 기반 - 예약 시스템)
   * @param {string} mentorId - 멘토 ID
   * @returns {Promise<Array>} 가능한 시간 슬롯
   */
  getAvailableSlots(mentorId) {
    // (wbs_detail.md - Week 5-6: 예약 시스템)
    // 예시 엔드포인트:
    return api.get(`/booking/slots/${mentorId}`);
  },

  /**
   * 커피챗을 예약합니다.
   * @param {object} bookingInfo - { mentorId, dateTime }
   * @returns {Promise<object>} 예약 확인 정보
   */
  createBooking(bookingInfo) {
    // (wbs_detail.md - Week 5-6: 예약 시스템)
    // 예시 엔드포인트:
    return api.post('/booking/book', bookingInfo);
  }
};

export default mentorService;