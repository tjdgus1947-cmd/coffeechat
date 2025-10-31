<template>
  <div class="file-uploader">
    <input 
      type="file" 
      @change="handleFileChange" 
      accept="image/*,.pdf" 
      ref="fileInput"
      style="display: none;"
    >
    <button type="button" @click="triggerFileInput">파일 선택</button>
    <span v-if="fileName">{{ fileName }}</span>
    <span v-else>선택된 파일 없음</span>
  </div>
</template>

<script setup>
import { ref, defineEmits } from 'vue';

const emit = defineEmits(['file-changed']);
const fileInput = ref(null);
const fileName = ref('');

const triggerFileInput = () => {
  fileInput.value.click();
};

const handleFileChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    fileName.value = file.name;
    emit('file-changed', file); // 부모(MenteeRegisterForm)에게 파일 객체 전달
  } else {
    fileName.value = '';
    emit('file-changed', null);
  }
};
</script>

<style scoped>
.file-uploader {
  border: 1px dashed #ccc;
  padding: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.file-uploader button {
  background: #f0f0f0;
  border: 1px solid #ccc;
  padding: 5px 10px;
  cursor: pointer;
}
</style>