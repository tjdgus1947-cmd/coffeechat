<template>
  <svg 
    :width="size" 
    :height="size" 
    viewBox="0 0 100 100" 
    fill="none" 
    xmlns="http://www.w3.org/2000/svg"
    :class="className"
  >
    <!-- Steam lines (3 wavy lines) -->
    <path 
      d="M 30 15 Q 28 10 30 5" 
      :stroke="color" 
      stroke-width="3" 
      stroke-linecap="round"
      fill="none"
    />
    <path 
      d="M 45 15 Q 43 10 45 5" 
      :stroke="color" 
      stroke-width="3" 
      stroke-linecap="round"
      fill="none"
    />
    <path 
      d="M 60 15 Q 58 10 60 5" 
      :stroke="color" 
      stroke-width="3" 
      stroke-linecap="round"
      fill="none"
    />
    
    <!-- Coffee cup body -->
    <path 
      d="M 20 30 L 25 75 Q 25 80 30 80 L 60 80 Q 65 80 65 75 L 70 30 Z" 
      :stroke="color" 
      stroke-width="3.5" 
      stroke-linecap="round"
      stroke-linejoin="round"
      fill="none"
    />
    
    <!-- Cup details (inner lines) -->
    <ellipse cx="45" cy="32" rx="8" ry="3" :stroke="color" stroke-width="2" fill="none" />
    <path d="M 30 50 Q 35 52 40 50" :stroke="color" stroke-width="2" stroke-linecap="round" fill="none" />
    
    <!-- Coffee cup handle -->
    <path 
      d="M 70 35 Q 85 40 85 50 Q 85 60 70 65" 
      :stroke="color" 
      stroke-width="3.5" 
      stroke-linecap="round"
      fill="none"
    />
    
    <!-- Saucer (plate) -->
    <ellipse 
      cx="45" 
      cy="85" 
      rx="32" 
      ry="5" 
      :stroke="color" 
      stroke-width="3.5" 
      fill="none"
    />
  </svg>
</template>

<script setup>
defineProps({
  size: {
    type: [Number, String],
    default: 48
  },
  color: {
    type: String,
    default: 'currentColor'
  },
  className: {
    type: String,
    default: ''
  }
})
</script>
