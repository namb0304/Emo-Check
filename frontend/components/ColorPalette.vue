<script setup lang="ts">
import type { ColorPalette as ColorPaletteType } from '~/composables/useEmoCheck'
import { PhCopy, PhCheck } from '@phosphor-icons/vue'

interface Props {
  colors: ColorPaletteType[]
}

const props = defineProps<Props>()

const copiedIndex = ref<number | null>(null)

const copyColor = async (hex: string, index: number) => {
  try {
    await navigator.clipboard.writeText(hex)
    copiedIndex.value = index
    setTimeout(() => {
      copiedIndex.value = null
    }, 1500)
  } catch {
    console.error('Failed to copy color')
  }
}

// 色の明るさを計算（テキスト色の決定用）
const getTextColor = (rgb: number[]) => {
  const [r, g, b] = rgb
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
  return luminance > 0.5 ? '#1a1a1a' : '#ffffff'
}
</script>

<template>
  <div class="w-full animate-slide-up">
    <!-- ヘッダー -->
    <div class="flex items-center gap-3 mb-4">
      <div class="w-8 h-[2px] bg-gradient-to-r from-emo-pink to-emo-purple" />
      <h3 class="text-sm font-medium text-dark-400 tracking-wider uppercase">
        Color Analysis
      </h3>
      <div class="flex-1 h-[1px] bg-dark-700" />
    </div>

    <!-- カラーチップ -->
    <div class="grid grid-cols-5 gap-3">
      <div
        v-for="(color, index) in colors"
        :key="color.hex"
        class="group relative"
        :style="{ animationDelay: `${index * 100}ms` }"
      >
        <!-- カラーカード -->
        <button
          @click="copyColor(color.hex, index)"
          class="w-full aspect-square rounded-xl transition-all duration-300 hover:scale-110 hover:z-10 hover:shadow-xl relative overflow-hidden animate-color-flip"
          :style="{
            backgroundColor: color.hex,
            animationDelay: `${index * 100}ms`,
          }"
        >
          <!-- ホバー時のオーバーレイ -->
          <div
            class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200"
            :style="{ backgroundColor: `${color.hex}dd` }"
          >
            <PhCheck
              v-if="copiedIndex === index"
              :size="20"
              weight="bold"
              :style="{ color: getTextColor(color.rgb) }"
            />
            <PhCopy
              v-else
              :size="20"
              weight="bold"
              :style="{ color: getTextColor(color.rgb) }"
            />
          </div>
        </button>

        <!-- カラー情報 -->
        <div class="mt-2 text-center">
          <p class="text-xs font-mono text-dark-300 uppercase">
            {{ color.hex }}
          </p>
          <p class="text-[10px] text-dark-500">
            {{ color.percentage }}%
          </p>
        </div>
      </div>
    </div>

    <!-- 説明 -->
    <p class="mt-4 text-xs text-dark-500 text-center">
      クリックでカラーコードをコピー
    </p>
  </div>
</template>
