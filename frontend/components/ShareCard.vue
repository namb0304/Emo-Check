<script setup lang="ts">
import { PhShareNetwork, PhDownloadSimple, PhX, PhSparkle } from '@phosphor-icons/vue'
import type { EmoComponent, ColorPalette } from '~/composables/useEmoCheck'

interface Props {
  score: number
  imageUrl: string
  components: EmoComponent[]
  colors: ColorPalette[]
}

interface Emits {
  (e: 'close'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const hiddenCardRef = ref<HTMLElement | null>(null)
const isGenerating = ref(false)

// 画像生成の共通処理
const generateCardImage = async (): Promise<HTMLCanvasElement | null> => {
  if (!hiddenCardRef.value) return null

  try {
    const html2canvas = (await import('html2canvas')).default

    const canvas = await html2canvas(hiddenCardRef.value, {
      backgroundColor: '#0a0a0a',
      scale: 2,
      useCORS: true,
      allowTaint: true,
      logging: false,
    })

    return canvas
  } catch (error) {
    console.error('Failed to generate card:', error)
    return null
  }
}

// シェアカードをダウンロード
const downloadCard = async () => {
  isGenerating.value = true

  try {
    const canvas = await generateCardImage()
    if (!canvas) return

    const link = document.createElement('a')
    link.download = `emo_check_${props.score}_${Date.now()}.png`
    link.href = canvas.toDataURL('image/png')
    link.click()
  } finally {
    isGenerating.value = false
  }
}

// Web Share APIでシェア
const shareCard = async () => {
  isGenerating.value = true

  try {
    const canvas = await generateCardImage()
    if (!canvas) return

    canvas.toBlob(async (blob) => {
      if (!blob) return

      const file = new File([blob], 'emo_check.png', { type: 'image/png' })

      if (navigator.share && navigator.canShare({ files: [file] })) {
        await navigator.share({
          title: 'Emo-Check 結果',
          text: `私の写真のエモ度は ${props.score}% でした！ #EmoCheck`,
          files: [file],
        })
      } else {
        // Web Share API非対応の場合はダウンロード
        const link = document.createElement('a')
        link.download = `emo_check_${props.score}_${Date.now()}.png`
        link.href = canvas.toDataURL('image/png')
        link.click()
      }
    }, 'image/png')
  } finally {
    isGenerating.value = false
  }
}

// スコアに応じたグラデーション
const scoreGradient = computed(() => {
  if (props.score >= 80) return 'from-emo-pink via-emo-purple to-emo-pink'
  if (props.score >= 60) return 'from-emo-purple via-emo-blue to-emo-purple'
  if (props.score >= 40) return 'from-emo-blue via-emo-cyan to-emo-blue'
  return 'from-dark-400 via-dark-300 to-dark-400'
})
</script>

<template>
  <!-- 画面外に配置する画像生成用のカード（非表示） -->
  <div class="fixed" style="left: -9999px; top: 0;">
    <div
      ref="hiddenCardRef"
      class="w-[400px] overflow-hidden rounded-2xl bg-dark-950 p-6"
    >
      <!-- 背景グラデーション -->
      <div class="absolute inset-0 opacity-30">
        <div class="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-emo-pink/30 via-transparent to-emo-purple/30" />
      </div>

      <!-- コンテンツ -->
      <div class="relative z-10">
        <!-- ヘッダー -->
        <div class="flex items-center justify-center gap-2 mb-6">
          <PhSparkle :size="24" weight="fill" class="text-emo-pink" />
          <span class="text-xl font-display font-bold text-white">Emo-Check</span>
        </div>

        <!-- 画像 -->
        <div class="relative w-32 h-32 mx-auto mb-6 rounded-xl overflow-hidden border-2 border-dark-700">
          <img
            :src="imageUrl"
            alt="Analyzed image"
            class="w-full h-full object-cover"
            crossorigin="anonymous"
          />
        </div>

        <!-- スコア -->
        <div class="text-center mb-6">
          <div
            :class="[
              'text-6xl font-display font-bold bg-clip-text text-transparent bg-gradient-to-r bg-300%',
              scoreGradient,
            ]"
          >
            {{ score }}%
          </div>
          <div class="text-dark-400 text-sm uppercase tracking-wider mt-1">
            Emo Score
          </div>
        </div>

        <!-- 成分（上位2つ） -->
        <div class="flex justify-center gap-4 mb-6">
          <div
            v-for="comp in components.slice(0, 2)"
            :key="comp.name"
            class="px-3 py-1 rounded-full bg-dark-800 text-sm"
          >
            <span class="text-white">{{ comp.name }}</span>
            <span class="text-dark-400 ml-1">{{ comp.percentage }}%</span>
          </div>
        </div>

        <!-- カラーパレット -->
        <div class="flex justify-center gap-2 mb-4">
          <div
            v-for="color in colors.slice(0, 5)"
            :key="color.hex"
            class="w-8 h-8 rounded-lg"
            :style="{ backgroundColor: color.hex }"
          />
        </div>

        <!-- フッター -->
        <div class="text-center text-xs text-dark-500">
          emo-check.app
        </div>
      </div>
    </div>
  </div>

  <!-- 表示用のモーダル -->
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-dark-950/90 backdrop-blur-sm">
    <!-- 閉じるボタン -->
    <button
      @click="emit('close')"
      class="absolute top-4 right-4 p-2 rounded-full bg-dark-800 hover:bg-dark-700 transition-colors"
    >
      <PhX :size="24" weight="bold" />
    </button>

    <div class="w-full max-w-md">
      <!-- プレビューカード -->
      <div class="relative overflow-hidden rounded-2xl bg-dark-950 p-6 border border-dark-800">
        <!-- 背景グラデーション -->
        <div class="absolute inset-0 opacity-30">
          <div class="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-emo-pink/30 via-transparent to-emo-purple/30" />
        </div>

        <!-- コンテンツ -->
        <div class="relative z-10">
          <!-- ヘッダー -->
          <div class="flex items-center justify-center gap-2 mb-6">
            <PhSparkle :size="24" weight="fill" class="text-emo-pink" />
            <span class="text-xl font-display font-bold text-white">Emo-Check</span>
          </div>

          <!-- 画像 -->
          <div class="relative w-32 h-32 mx-auto mb-6 rounded-xl overflow-hidden border-2 border-dark-700">
            <img
              :src="imageUrl"
              alt="Analyzed image"
              class="w-full h-full object-cover"
            />
          </div>

          <!-- スコア -->
          <div class="text-center mb-6">
            <div
              :class="[
                'text-6xl font-display font-bold bg-clip-text text-transparent bg-gradient-to-r bg-300%',
                scoreGradient,
              ]"
            >
              {{ score }}%
            </div>
            <div class="text-dark-400 text-sm uppercase tracking-wider mt-1">
              Emo Score
            </div>
          </div>

          <!-- 成分（上位2つ） -->
          <div class="flex justify-center gap-4 mb-6">
            <div
              v-for="comp in components.slice(0, 2)"
              :key="comp.name"
              class="px-3 py-1 rounded-full bg-dark-800 text-sm"
            >
              <span class="text-white">{{ comp.name }}</span>
              <span class="text-dark-400 ml-1">{{ comp.percentage }}%</span>
            </div>
          </div>

          <!-- カラーパレット -->
          <div class="flex justify-center gap-2 mb-4">
            <div
              v-for="color in colors.slice(0, 5)"
              :key="color.hex"
              class="w-8 h-8 rounded-lg"
              :style="{ backgroundColor: color.hex }"
            />
          </div>

          <!-- フッター -->
          <div class="text-center text-xs text-dark-500">
            emo-check.app
          </div>
        </div>
      </div>

      <!-- アクションボタン -->
      <div class="flex gap-3 mt-4">
        <button
          @click="downloadCard"
          :disabled="isGenerating"
          class="flex-1 btn-secondary flex items-center justify-center gap-2"
        >
          <PhDownloadSimple :size="20" weight="bold" />
          <span>{{ isGenerating ? '生成中...' : 'ダウンロード' }}</span>
        </button>
        <button
          @click="shareCard"
          :disabled="isGenerating"
          class="flex-1 btn-primary flex items-center justify-center gap-2"
        >
          <PhShareNetwork :size="20" weight="bold" />
          <span>{{ isGenerating ? '生成中...' : 'シェア' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>
