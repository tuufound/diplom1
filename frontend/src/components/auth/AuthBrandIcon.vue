<template>
  <span class="auth-brand-icon" role="img" aria-hidden="true">
    <svg class="auth-brand-svg" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient :id="gradId" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#6b5fd4" />
          <stop offset="55%" stop-color="#8b6cf0" />
          <stop offset="100%" stop-color="#6d8ae8" />
        </linearGradient>
      </defs>
      <rect width="48" height="48" rx="14" :fill="`url(#${gradId})`" />
      <!-- белый ромб + «книга» -->
      <path
        d="M24 11 L35 22 L24 33 L13 22 Z"
        fill="#ffffff"
        stroke="rgba(255,255,255,0.35)"
        stroke-width="0.5"
      />
      <path
        d="M24 17 v10 M19.5 20.5 L24 24.5 L28.5 20.5 M19.5 26.5 L24 22.5 L28.5 26.5"
        stroke="#3d4a63"
        stroke-width="1.35"
        stroke-linecap="round"
        stroke-linejoin="round"
        fill="none"
      />
    </svg>
  </span>
</template>

<script>
export default {
  name: 'AuthBrandIcon',
  data() {
    return {
      gradId: `abg-${Math.random().toString(36).slice(2, 11)}`
    }
  }
}
</script>

<style scoped>
.auth-brand-icon {
  display: inline-flex;
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  filter: drop-shadow(0 10px 20px rgba(107, 95, 212, 0.35));
}

.auth-brand-svg {
  width: 100%;
  height: 100%;
  display: block;
}
</style>
