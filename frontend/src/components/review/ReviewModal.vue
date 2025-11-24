<template>
  <div v-if="show" class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h3>{{ existingReview ? '📖 작성한 후기' : '✍️ 후기 작성' }}</h3>
        <button class="close-btn" @click="$emit('close')">×</button>
      </div>

      <!-- 기존 후기 보기 모드 -->
      <div v-if="existingReview" class="modal-body view-mode">
        <p class="mentor-info">
          <strong>{{ mentorName }}</strong> 멘토님과의 커피챗 후기
        </p>

        <div class="review-display">
          <div class="rating-display">
            <div class="stars">
              <span
                v-for="star in 5"
                :key="star"
                class="star"
                :class="{ filled: star <= existingReview.rating }"
              >
                ★
              </span>
            </div>
            <p class="rating-text">{{ getRatingText(existingReview.rating) }}</p>
          </div>

          <div class="review-content">
            <p>{{ existingReview.content }}</p>
          </div>

          <p class="review-date">
            작성일: {{ formatDate(existingReview.created_at) }}
          </p>
        </div>
      </div>

      <!-- 후기 작성 모드 -->
      <div v-else class="modal-body">
        <p class="mentor-info">
          <strong>{{ mentorName }}</strong> 멘토님과의 커피챗은 어떠셨나요?
        </p>

        <!-- 별점 선택 -->
        <div class="rating-section">
          <div class="stars">
            <span
              v-for="star in 5"
              :key="star"
              class="star"
              :class="{ filled: star <= rating }"
              @click="rating = star"
            >
              ★
            </span>
          </div>
          <p class="rating-text">{{ ratingText }}</p>
        </div>

        <!-- 후기 내용 입력 -->
        <div class="input-group">
          <textarea
            v-model="content"
            placeholder="다른 멘티들에게 도움이 되도록 솔직한 후기를 남겨주세요. (최소 10자 이상)"
            rows="5"
          ></textarea>
        </div>
      </div>

      <div class="modal-footer">
        <button class="cancel-btn" @click="$emit('close')">닫기</button>
        <button 
          v-if="!existingReview"
          class="submit-btn" 
          :disabled="isSubmitting || content.length < 10 || rating === 0"
          @click="handleSubmit"
        >
          {{ isSubmitting ? '등록 중...' : '후기 등록하기' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { supabase } from '@/supabaseClient';

const props = defineProps({
  show: Boolean,
  chat: Object, 
  menteeId: String 
});

const emit = defineEmits(['close', 'review-submitted']);

const rating = ref(5);
const content = ref('');
const isSubmitting = ref(false);
const existingReview = ref(null);

const mentorName = computed(() => props.chat?.mentor?.full_name || '멘토');

const ratingText = computed(() => {
  const texts = ['아쉬웠어요', '그저 그랬어요', '보통이에요', '좋았어요!', '최고였어요!'];
  return rating.value > 0 ? texts[rating.value - 1] : '별점을 선택해주세요';
});

function getRatingText(ratingValue) {
  const texts = ['아쉬웠어요', '그저 그랬어요', '보통이에요', '좋았어요!', '최고였어요!'];
  return texts[ratingValue - 1] || '';
}

function formatDate(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

// 모달 열릴 때 기존 후기 확인
watch(() => props.show, async (newVal) => {
  if (newVal && props.chat) {
    await checkExistingReview();
  }
});

async function checkExistingReview() {
  try {
    const { data, error } = await supabase
      .from('reviews')
      .select('*')
      .eq('coffee_chat_id', props.chat.id)
      .eq('mentee_id', props.menteeId)
      .single();

    if (data) {
      existingReview.value = data;
    } else {
      existingReview.value = null;
    }
  } catch (err) {
    // 데이터 없음 = 아직 후기 미작성
    existingReview.value = null;
  }
}

async function handleSubmit() {
  if (!props.chat || !props.menteeId) return;

  isSubmitting.value = true;

  try {
    // coffee_chats 테이블에서 mentor_id 직접 조회
    const { data: chatData, error: fetchError } = await supabase
      .from('coffee_chats')
      .select('mentor_id')
      .eq('id', props.chat.id)
      .single();

    if (fetchError) throw fetchError;

    const targetMentorId = chatData.mentor_id;

    if (!targetMentorId) {
      throw new Error('멘토 ID를 찾을 수 없습니다.');
    }

    const { data, error } = await supabase
      .from('reviews')
      .insert({
        coffee_chat_id: props.chat.id,   
        mentee_id: props.menteeId,       
        mentor_id: targetMentorId,
        rating: rating.value,
        content: content.value
      })
      .select()
      .single();

    if (error) throw error;

    alert('소중한 후기가 등록되었습니다! 🎉');
    
    // 작성한 후기를 바로 표시
    existingReview.value = data;
    
    emit('review-submitted'); 
    
    // 폼 초기화
    rating.value = 5;
    content.value = '';
    
  } catch (error) {
    console.error('후기 등록 실패 상세:', error);
    
    if (error.code === '23505') { 
      alert('이미 후기를 작성하신 커피챗입니다.');
      await checkExistingReview();
    } else {
      alert(`후기 등록 중 오류가 발생했습니다: ${error.message || error.code}`);
    }
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  width: 90%;
  max-width: 500px;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.modal-header h3 { margin: 0; font-size: 20px; color: #111827; }
.close-btn { background: none; border: none; font-size: 24px; cursor: pointer; color: #9ca3af; }

.modal-body { margin-bottom: 24px; text-align: center; }
.mentor-info { font-size: 16px; color: #4b5563; margin-bottom: 20px; }

.rating-section { margin-bottom: 20px; }
.stars { font-size: 32px; cursor: pointer; color: #e5e7eb; transition: color 0.2s; }
.star { margin: 0 2px; }
.star.filled { color: #fbbf24; }
.rating-text { margin-top: 8px; font-size: 14px; color: #6d28d9; font-weight: 600; }

.input-group textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  resize: none;
  font-size: 14px;
}
.input-group textarea:focus {
  outline: none;
  border-color: #6d28d9;
  box-shadow: 0 0 0 3px rgba(109, 40, 217, 0.1);
}

/* 후기 보기 모드 스타일 */
.view-mode {
  text-align: left;
}

.review-display {
  background: #f9fafb;
  border-radius: 12px;
  padding: 20px;
}

.rating-display {
  text-align: center;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.rating-display .stars {
  cursor: default;
}

.review-content {
  margin-bottom: 16px;
}

.review-content p {
  font-size: 15px;
  line-height: 1.6;
  color: #374151;
  white-space: pre-wrap;
  word-break: break-word;
}

.review-date {
  text-align: right;
  font-size: 13px;
  color: #9ca3af;
  margin: 0;
}

.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}
.cancel-btn {
  background: #f3f4f6; color: #4b5563; border: none;
  padding: 10px 20px; border-radius: 8px; font-weight: 600;
  cursor: pointer;
}
.submit-btn {
  background: #6d28d9; color: white; border: none;
  padding: 10px 20px; border-radius: 8px; font-weight: 600;
  cursor: pointer;
}
.submit-btn:disabled { background: #d1d5db; cursor: not-allowed; }
</style>