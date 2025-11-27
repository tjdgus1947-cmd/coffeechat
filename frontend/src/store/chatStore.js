// src/store/chatStore.js
import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '@/services/api';
import { useAuthStore } from './auth';

export const useChatStore = defineStore('chat', () => {
  const unreadCount = ref(0);
  const isLoading = ref(false);

  const authStore = useAuthStore();

  // 안 읽은 메시지 개수 불러오기
  async function fetchUnreadCount() {
    if (!authStore.isAuthenticated) {
      unreadCount.value = 0;
      return;
    }

    try {
      isLoading.value = true;
      const res = await api.get('/chat/unread-count');
      unreadCount.value = res.data?.unread_count ?? 0;
    } catch (e) {
      console.error('unread-count 불러오기 실패:', e);
    } finally {
      isLoading.value = false;
    }
  }

  // 나중에 상세 채팅 들어갔을 때 수동으로 줄이고 싶으면 쓰는 용도 (선택)
  function setUnreadCount(value) {
    unreadCount.value = value;
  }

  return {
    unreadCount,
    isLoading,
    fetchUnreadCount,
    setUnreadCount,
  };
});
