<template>
  <div class="app-shell-decor" aria-hidden="true">
    <!-- левый край -->
    <i class="fas fa-folder shell-decor sd-l1"></i>
    <i class="fas fa-clock shell-decor sd-l2"></i>
    <i class="fas fa-list-check shell-decor sd-l3"></i>
    <i class="fas fa-layer-group shell-decor sd-l4"></i>
    <i class="fas fa-diagram-project shell-decor sd-l5"></i>
    <i class="fas fa-bullseye shell-decor sd-l6"></i>
    <!-- правый край -->
    <i class="fas fa-folder-open shell-decor sd-r1"></i>
    <i class="fas fa-stopwatch shell-decor sd-r2"></i>
    <i class="fas fa-chart-pie shell-decor sd-r3"></i>
    <i class="fas fa-star shell-decor sd-r4"></i>
    <i class="fas fa-flag-checkered shell-decor sd-r5"></i>
    <i class="fas fa-bell shell-decor sd-r6"></i>
    <!-- боковые «полосы» у контента (середина по вертикали) -->
    <i class="fas fa-lightbulb shell-decor sd-lm1"></i>
    <i class="fas fa-book shell-decor sd-lm2"></i>
    <i class="fas fa-chart-line shell-decor sd-rm1"></i>
    <i class="fas fa-mobile-screen shell-decor sd-rm2"></i>
    <!-- низ -->
    <i class="fas fa-table-columns shell-decor sd-b1"></i>
    <i class="fas fa-calendar-check shell-decor sd-b2"></i>
    <i class="fas fa-clipboard-list shell-decor sd-b3"></i>
    <i class="fas fa-user-check shell-decor sd-b4"></i>
    <i class="fas fa-tasks shell-decor sd-b5"></i>
  </div>
</template>

<script>
export default {
  name: 'AppShellDecor'
}
</script>

<style scoped>
.app-shell-decor {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 0;
}

.shell-decor {
  position: absolute;
  font-size: clamp(1.6rem, 3.2vw, 2.6rem);
  color: var(--accent-primary);
  opacity: 0.11;
}

/* слева */
.sd-l1 {
  left: 2%;
  top: 14%;
  transform: rotate(-12deg);
}
.sd-l2 {
  left: 1%;
  top: 42%;
  transform: rotate(6deg);
  font-size: clamp(1.85rem, 3.6vw, 2.9rem);
}
.sd-l3 {
  left: 3%;
  top: 68%;
  transform: rotate(-5deg);
}
.sd-l4 {
  left: 2%;
  bottom: 22%;
  transform: rotate(8deg);
  opacity: 0.09;
}
.sd-l5 {
  left: 4%;
  top: 28%;
  transform: rotate(11deg);
  opacity: 0.1;
}
.sd-l6 {
  left: 1%;
  top: 54%;
  transform: rotate(-9deg);
  font-size: clamp(1.5rem, 3vw, 2.4rem);
}

/* справа */
.sd-r1 {
  right: 2%;
  top: 12%;
  transform: rotate(10deg);
}
.sd-r2 {
  right: 1%;
  top: 38%;
  transform: rotate(-8deg);
  font-size: clamp(1.9rem, 3.5vw, 3rem);
}
.sd-r3 {
  right: 3%;
  top: 62%;
  transform: rotate(5deg);
}
.sd-r4 {
  right: 2%;
  bottom: 26%;
  transform: rotate(-14deg);
  opacity: 0.1;
}
.sd-r5 {
  right: 4%;
  top: 26%;
  transform: rotate(-11deg);
  opacity: 0.09;
}
.sd-r6 {
  right: 1%;
  top: 50%;
  transform: rotate(13deg);
  font-size: clamp(1.55rem, 3.1vw, 2.5rem);
}

/* слева/справа у центральной колонки (зоны рядом с карточкой, не у края экрана) */
.sd-lm1 {
  left: clamp(8%, 12vw, 16%);
  top: 38%;
  transform: rotate(-10deg);
  opacity: 0.1;
}
.sd-lm2 {
  left: clamp(10%, 14vw, 18%);
  bottom: 38%;
  transform: rotate(7deg);
  font-size: clamp(1.45rem, 2.9vw, 2.35rem);
  opacity: 0.09;
}
.sd-rm1 {
  right: clamp(8%, 12vw, 16%);
  top: 40%;
  transform: rotate(12deg);
  opacity: 0.1;
}
.sd-rm2 {
  right: clamp(10%, 14vw, 18%);
  bottom: 36%;
  transform: rotate(-8deg);
  font-size: clamp(1.5rem, 3vw, 2.4rem);
  opacity: 0.09;
}

/* снизу (между боками, не перекрывая центр контента сильно — ближе к углам и краям) */
.sd-b1 {
  bottom: 5%;
  left: 10%;
  transform: rotate(-6deg);
}
.sd-b2 {
  bottom: 7%;
  left: 32%;
  transform: rotate(4deg);
  opacity: 0.09;
}
.sd-b3 {
  bottom: 6%;
  left: 50%;
  transform: translateX(-50%) rotate(-3deg);
}
.sd-b4 {
  bottom: 7%;
  right: 32%;
  transform: rotate(7deg);
}
.sd-b5 {
  bottom: 5%;
  right: 10%;
  transform: rotate(-9deg);
}

@media (max-width: 768px) {
  .shell-decor {
    opacity: 0.07;
    font-size: clamp(1.35rem, 4vw, 2rem);
  }

  .sd-b3 {
    display: none;
  }
}
</style>
