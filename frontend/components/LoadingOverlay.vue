<script setup lang="ts">
interface Props {
  message?: string
}

const props = withDefaults(defineProps<Props>(), {
  message: '分析中',
})

// 分析中のサブメッセージ（ランダムで切り替え）
const subMessages = [
  '色彩を分析中',
  '構図を確認中',
  '雰囲気を感知中',
  'エモさを計測中',
  'ノスタルジー度をチェック',
  '儚さを検出中',
  'メランコリー成分を解析',
]

const dots = ref('')
const currentSubMessage = ref(subMessages[0])
let subMessageIndex = 0

onMounted(() => {
  // ドットアニメーション
  const dotsInterval = setInterval(() => {
    dots.value = dots.value.length >= 3 ? '' : dots.value + '.'
  }, 400)

  // サブメッセージ切り替え（1.5秒ごと）
  const messageInterval = setInterval(() => {
    subMessageIndex = (subMessageIndex + 1) % subMessages.length
    currentSubMessage.value = subMessages[subMessageIndex]
  }, 1500)

  onUnmounted(() => {
    clearInterval(dotsInterval)
    clearInterval(messageInterval)
  })
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

      <!-- メインメッセージ -->
      <p class="text-xl font-medium text-white">
        {{ message }}<span class="inline-block w-8 text-left">{{ dots }}</span>
      </p>

      <!-- サブメッセージ（切り替わる） -->
      <p class="text-sm text-dark-400 mt-2 h-5 transition-opacity duration-300">
        {{ currentSubMessage }}
      </p>
    </div>
  </div>
</template>
