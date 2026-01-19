<script setup lang="ts">
interface TrailPoint {
  id: number
  x: number
  y: number
  opacity: number
  scale: number
  hue: number
}

const points = ref<TrailPoint[]>([])
const isDesktop = ref(true)
let idCounter = 0
let lastX = 0
let lastY = 0
let animationId: number | null = null

// 色相の範囲（ピンク〜パープル〜ブルー）
const HUE_START = 320 // ピンク
const HUE_END = 220   // ブルー
let currentHue = HUE_START

const onMouseMove = (e: MouseEvent) => {
  const dx = e.clientX - lastX
  const dy = e.clientY - lastY
  const distance = Math.sqrt(dx * dx + dy * dy)

  // 滑らかに軌跡を出すため間隔を狭める
  if (distance < 10) return

  lastX = e.clientX
  lastY = e.clientY

  // 色相をゆっくり変化
  currentHue -= 1.5
  if (currentHue < HUE_END) currentHue = HUE_START

  const newPoint: TrailPoint = {
    id: idCounter++,
    x: e.clientX,
    y: e.clientY,
    opacity: 0.25,
    scale: 1,
    hue: currentHue,
  }

  points.value.push(newPoint)

  if (points.value.length > 20) {
    points.value.shift()
  }
}

const animate = () => {
  points.value = points.value
    .map(point => ({
      ...point,
      opacity: point.opacity - 0.004,
      scale: point.scale * 1.015, // ゆっくり広がりながら消える
    }))
    .filter(point => point.opacity > 0)

  animationId = requestAnimationFrame(animate)
}

onMounted(() => {
  isDesktop.value = window.matchMedia('(hover: hover)').matches

  if (isDesktop.value) {
    window.addEventListener('mousemove', onMouseMove)
    animationId = requestAnimationFrame(animate)
  }
})

onUnmounted(() => {
  window.removeEventListener('mousemove', onMouseMove)
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
})
</script>

<template>
  <div
    v-if="isDesktop"
    class="fixed inset-0 pointer-events-none z-[9999]"
    aria-hidden="true"
  >
    <!-- ふわふわした光の軌跡（背景に溶け込む） -->
    <div
      v-for="point in points"
      :key="point.id"
      class="absolute rounded-full"
      :style="{
        left: `${point.x}px`,
        top: `${point.y}px`,
        width: `${40 * point.scale}px`,
        height: `${40 * point.scale}px`,
        transform: 'translate(-50%, -50%)',
        background: `radial-gradient(circle, hsla(${point.hue}, 60%, 70%, ${point.opacity}) 0%, hsla(${point.hue}, 50%, 65%, ${point.opacity * 0.3}) 30%, transparent 60%)`,
        filter: `blur(${12 * point.scale}px)`,
      }"
    />
  </div>
</template>
