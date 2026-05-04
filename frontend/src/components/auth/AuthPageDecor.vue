<template>
  <div class="auth-page-decor page-shell">
    <div class="auth-bg-icons" aria-hidden="true">
      <i class="fas fa-folder decor i0"></i>
      <i class="fas fa-folder-open decor i1"></i>
      <i class="fas fa-clock decor i2"></i>
      <i class="fas fa-stopwatch decor i3"></i>
      <i class="fas fa-list-check decor i4"></i>
      <i class="fas fa-table-columns decor i5"></i>
      <i class="fas fa-chart-pie decor i6"></i>
      <i class="fas fa-star decor i7"></i>
      <i class="fas fa-calendar-check decor i8"></i>
      <i class="fas fa-clipboard-list decor i9"></i>
      <i class="fas fa-user-check decor i10"></i>
      <i class="fas fa-layer-group decor i11"></i>
    </div>
    <div class="auth-center-wrap">
      <slot />
    </div>
  </div>
</template>

<script>
export default {
  name: 'AuthPageDecor'
}
</script>

<style scoped>
.auth-page-decor {
  position: relative;
  min-height: calc(100vh - 170px);
  overflow: hidden;
}

.auth-bg-icons {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 0;
}

.decor {
  position: absolute;
  font-size: clamp(1.65rem, 4.2vw, 2.85rem);
  color: var(--accent-primary);
  opacity: 0.13;
}

.auth-center-wrap {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: inherit;
  padding: 18px;
}

.i0 {
  top: 6%;
  left: 4%;
  transform: rotate(-14deg);
}
.i1 {
  top: 14%;
  right: 8%;
  transform: rotate(8deg);
}
.i2 {
  top: 42%;
  left: 2%;
  transform: rotate(6deg);
  font-size: clamp(2rem, 5vw, 3.2rem);
}
.i3 {
  bottom: 18%;
  left: 10%;
  transform: rotate(-6deg);
}
.i4 {
  top: 8%;
  left: 38%;
  transform: rotate(-4deg);
  opacity: 0.1;
}
.i5 {
  top: 28%;
  right: 4%;
  transform: rotate(12deg);
}
.i6 {
  bottom: 8%;
  right: 6%;
  transform: rotate(-10deg);
  font-size: clamp(2.1rem, 5vw, 3.4rem);
}
.i7 {
  top: 52%;
  right: 14%;
  transform: rotate(18deg);
  opacity: 0.11;
}
.i8 {
  bottom: 32%;
  left: 18%;
  transform: rotate(-3deg);
}
.i9 {
  top: 62%;
  left: 28%;
  transform: rotate(5deg);
  opacity: 0.09;
}
.i10 {
  bottom: 12%;
  left: 42%;
  transform: rotate(-11deg);
}
.i11 {
  top: 22%;
  left: 12%;
  transform: rotate(7deg);
  opacity: 0.08;
}

@media (max-width: 576px) {
  .auth-page-decor {
    min-height: auto;
  }

  .auth-center-wrap {
    padding: 12px;
  }

  .decor {
    opacity: 0.09;
  }
}
</style>
