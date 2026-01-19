<script setup lang="ts">
interface Props {
  beforeUrl: string
  afterUrl: string
  beforeLabel?: string
  afterLabel?: string
}

const props = withDefaults(defineProps<Props>(), {
  beforeLabel: 'Before',
  afterLabel: 'After',
})

const containerRef = ref<HTMLElement | null>(null)
const sliderPosition = ref(50)
const isDragging = ref(false)

const updateSlider = (clientX: number) => {
  if (!containerRef.value) return

  const rect = containerRef.value.getBoundingClientRect()
  const x = clientX - rect.left
  const percentage = Math.max(0, Math.min(100, (x / rect.width) * 100))
  sliderPosition.value = percentage
}

const onMouseDown = (e: MouseEvent) => {
  isDragging.value = true
  updateSlider(e.clientX)
}

const onMouseMove = (e: MouseEvent) => {
  if (!isDragging.value) return
  updateSlider(e.clientX)
}

const onMouseUp = () => {
  isDragging.value = false
}

const onTouchStart = (e: TouchEvent) => {
  isDragging.value = true
  updateSlider(e.touches[0].clientX)
}

const onTouchMove = (e: TouchEvent) => {
  if (!isDragging.value) return
  updateSlider(e.touches[0].clientX)
}

const onTouchEnd = () => {
  isDragging.value = false
}

onMounted(() => {
  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
  document.addEventListener('touchmove', onTouchMove)
  document.addEventListener('touchend', onTouchEnd)
})

onUnmounted(() => {
  document.removeEventListener('mousemove', onMouseMove)
  document.removeEventListener('mouseup', onMouseUp)
  document.removeEventListener('touchmove', onTouchMove)
  document.removeEventListener('touchend', onTouchEnd)
})
</script>

<template>
  <div class="w-full">
    <!-- ヘッダー -->
    <div class="flex items-center gap-3 mb-4">
      <div class="w-8 h-[2px] bg-gradient-to-r from-emo-cyan to-emo-blue" />
      <h3 class="text-sm font-medium text-dark-400 tracking-wider uppercase">
        Before / After
      </h3>
      <div class="flex-1 h-[1px] bg-dark-700" />
    </div>

    <!-- スライダーコンテナ -->
    <div
      ref="containerRef"
      class="relative w-full aspect-video rounded-xl overflow-hidden cursor-ew-resize select-none"
      @mousedown="onMouseDown"
      @touchstart="onTouchStart"
    >
      <!-- After画像（背景） -->
      <img
        :src="afterUrl"
        :alt="afterLabel"
        class="absolute inset-0 w-full h-full object-cover"
      />

      <!-- Before画像（クリップ） -->
      <div
        class="absolute inset-0 overflow-hidden"
        :style="{ width: `${sliderPosition}%` }"
      >
        <img
          :src="beforeUrl"
          :alt="beforeLabel"
          class="absolute inset-0 w-full h-full object-cover"
          :style="{ width: `${100 / (sliderPosition / 100)}%`, maxWidth: 'none' }"
        />
      </div>

      <!-- スライダーライン -->
      <div
        class="absolute top-0 bottom-0 w-1 bg-white shadow-lg"
        :style="{ left: `${sliderPosition}%`, transform: 'translateX(-50%)' }"
      >
        <!-- ハンドル -->
        <div
          class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-white shadow-xl flex items-center justify-center"
        >
          <div class="flex items-center gap-0.5">
            <div class="w-0 h-0 border-t-[6px] border-t-transparent border-b-[6px] border-b-transparent border-r-[6px] border-r-dark-800" />
            <div class="w-0 h-0 border-t-[6px] border-t-transparent border-b-[6px] border-b-transparent border-l-[6px] border-l-dark-800" />
          </div>
        </div>
      </div>

      <!-- ラベル -->
      <div
        class="absolute top-4 left-4 px-2 py-1 rounded bg-dark-900/80 text-xs text-white"
        v-if="sliderPosition > 15"
      >
        {{ beforeLabel }}
      </div>
      <div
        class="absolute top-4 right-4 px-2 py-1 rounded bg-dark-900/80 text-xs text-white"
        v-if="sliderPosition < 85"
      >
        {{ afterLabel }}
      </div>
    </div>

    <!-- 説明 -->
    <p class="mt-3 text-xs text-dark-500 text-center">
      スライダーをドラッグして比較
    </p>
  </div>
</template>
