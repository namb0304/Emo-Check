<script setup lang="ts">
interface Props {
  message?: string
}

const props = withDefaults(defineProps<Props>(), {
  message: '分析中...',
})

const dots = ref('')

onMounted(() => {
  const interval = setInterval(() => {
    dots.value = dots.value.length >= 3 ? '' : dots.value + '.'
  }, 400)

  onUnmounted(() => clearInterval(interval))
})
</script>

<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-dark-950/90 backdrop-blur-sm"
  >
    <div class="text-center">
      <!-- アニメーションローダー -->
      <div class="relative w-24 h-24 mx-auto mb-8">
        <!-- 外側のリング -->
        <div
          class="absolute inset-0 rounded-full border-4 border-dark-700"
        />
        <!-- 回転するグラデーションリング -->
        <div
          class="absolute inset-0 rounded-full border-4 border-transparent animate-spin"
          style="
            border-top-color: #ff6b9d;
            border-right-color: #c084fc;
            animation-duration: 1.5s;
          "
        />
        <!-- 内側のパルス -->
        <div
          class="absolute inset-4 rounded-full bg-gradient-to-br from-emo-pink/20 to-emo-purple/20 animate-pulse"
        />
        <!-- 中央のドット -->
        <div
          class="absolute inset-0 flex items-center justify-center"
        >
          <div
            class="w-4 h-4 rounded-full bg-gradient-to-r from-emo-pink to-emo-purple animate-pulse"
          />
        </div>
      </div>

      <!-- テキスト -->
      <p class="text-xl font-medium text-white">
        {{ message }}<span class="inline-block w-8 text-left">{{ dots }}</span>
      </p>
      <p class="text-sm text-dark-400 mt-2">
        AIがあなたの写真を分析しています
      </p>
    </div>
  </div>
</template>
