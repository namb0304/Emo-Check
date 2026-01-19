<script setup lang="ts">
interface Props {
  score: number
  modelUsed: string
}

const props = defineProps<Props>()

const displayScore = ref(0)
const isAnimating = ref(true)

// スコアのアニメーション
onMounted(() => {
  const duration = 1500
  const startTime = Date.now()
  const targetScore = props.score

  const animate = () => {
    const elapsed = Date.now() - startTime
    const progress = Math.min(elapsed / duration, 1)

    // イージング関数 (easeOutExpo)
    const eased = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress)
    displayScore.value = Math.round(targetScore * eased)

    if (progress < 1) {
      requestAnimationFrame(animate)
    } else {
      isAnimating.value = false
    }
  }

  requestAnimationFrame(animate)
})

// スコアに応じた色とメッセージ
const scoreConfig = computed(() => {
  const score = props.score
  if (score >= 80) {
    return {
      gradient: 'from-emo-pink via-emo-purple to-emo-pink',
      message: 'めちゃくちゃエモい！',
      emoji: '✨',
      glow: 'shadow-emo-pink/50',
    }
  } else if (score >= 60) {
    return {
      gradient: 'from-emo-purple via-emo-blue to-emo-purple',
      message: 'かなりエモい！',
      emoji: '💫',
      glow: 'shadow-emo-purple/50',
    }
  } else if (score >= 40) {
    return {
      gradient: 'from-emo-blue via-emo-cyan to-emo-blue',
      message: 'まあまあエモい',
      emoji: '🌙',
      glow: 'shadow-emo-blue/50',
    }
  } else if (score >= 20) {
    return {
      gradient: 'from-emo-cyan via-teal-400 to-emo-cyan',
      message: 'ちょっとエモい',
      emoji: '🌿',
      glow: 'shadow-emo-cyan/50',
    }
  } else {
    return {
      gradient: 'from-dark-400 via-dark-300 to-dark-400',
      message: 'エモさ控えめ',
      emoji: '🌑',
      glow: 'shadow-dark-400/30',
    }
  }
})
</script>

<template>
  <div class="text-center animate-scale-in">
    <!-- スコア表示 -->
    <div class="relative inline-block">
      <!-- グロー効果 -->
      <div
        :class="[
          'absolute inset-0 blur-3xl opacity-50 bg-gradient-to-r',
          scoreConfig.gradient,
        ]"
      />

      <!-- スコア数値 -->
      <div class="relative">
        <div class="flex items-baseline justify-center gap-1">
          <span
            :class="[
              'text-8xl md:text-9xl font-display font-bold bg-clip-text text-transparent bg-gradient-to-r bg-300% animate-gradient',
              scoreConfig.gradient,
            ]"
          >
            {{ displayScore }}
          </span>
          <span class="text-4xl md:text-5xl text-dark-400 font-light">%</span>
        </div>

        <!-- Emo Score ラベル -->
        <p class="text-lg text-dark-400 tracking-widest uppercase mt-2">
          Emo Score
        </p>
      </div>
    </div>

    <!-- メッセージ -->
    <div
      class="mt-8 flex items-center justify-center gap-3 animate-slide-up animation-delay-300"
    >
      <span class="text-3xl">{{ scoreConfig.emoji }}</span>
      <p class="text-xl md:text-2xl font-medium text-white">
        {{ scoreConfig.message }}
      </p>
      <span class="text-3xl">{{ scoreConfig.emoji }}</span>
    </div>

    <!-- 使用モデル -->
    <p class="mt-4 text-sm text-dark-500 animate-fade-in animation-delay-500">
      Analyzed by {{ modelUsed }}
    </p>
  </div>
</template>
