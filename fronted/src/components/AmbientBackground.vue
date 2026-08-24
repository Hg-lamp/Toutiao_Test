<template>
  <div class="ambient-bg">
    <!-- 静态背景图 -->
    <div class="bg-image">
      <img src="/bg-image.jpg" alt="" />
    </div>

    <!-- 半透明遮罩（让内容可读） -->
    <div class="bg-overlay"></div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.ambient-bg {
  position: fixed;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100vw;
  max-width: 750px;
  height: 100vh;
  z-index: 0;
  overflow: hidden;
  background: #e8e8f0;
}

.bg-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.bg-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.bg-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.25);
  pointer-events: none;
}
</style>