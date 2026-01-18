<script setup lang="ts">
import { PhPixelLogo, PhFilmStrip, PhSpinner, PhDownloadSimple, PhArrowLeft } from '@phosphor-icons/vue'
import type { FilterType } from '~/composables/useEmoCheck'

interface Props {
  originalFile: File
  isProcessing: boolean
  processedImageUrl: string | null
  appliedFilter: string | null
}

interface Emits {
  (e: 'apply-filter', filterType: FilterType): void
  (e: 'download'): void
  (e: 'reset'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const filters = [
  {
    id: 'pixel' as FilterType,
    name: 'Pixel Art',
    description: 'ドット絵風に変換',
    icon: PhPixelLogo,
    gradient: 'from-green-400 to-cyan-400',
    bgGlow: 'bg-green-400/20',
  },
  {
    id: 'y2k' as FilterType,
    name: 'Y2K Film',
    description: 'フィルム風加工',
    icon: PhFilmStrip,
    gradient: 'from-orange-400 to-yellow-400',
    bgGlow: 'bg-orange-400/20',
  },
]
</script>

<template>
  <div class="w-full animate-slide-up">
    <!-- ヘッダー -->
    <div class="flex items-center gap-3 mb-6">
      <div class="w-8 h-[2px] bg-gradient-to-r from-emo-orange to-emo-pink" />
      <h3 class="text-sm font-medium text-dark-400 tracking-wider uppercase">
        Emo Booster
      </h3>
      <div class="flex-1 h-[1px] bg-dark-700" />
    </div>

    <!-- 処理結果表示 -->
    <div v-if="processedImageUrl" class="space-y-4">
      <!-- 加工済み画像 -->
      <div class="relative rounded-2xl overflow-hidden gradient-border">
        <img
          :src="processedImageUrl"
          :alt="appliedFilter || 'Processed image'"
          class="w-full h-auto max-h-[400px] object-contain bg-dark-950"
        />
        <!-- フィルター名バッジ -->
        <div class="absolute top-4 left-4 px-3 py-1 rounded-full bg-dark-900/80 backdrop-blur-sm text-sm">
          {{ appliedFilter }}
        </div>
      </div>

      <!-- アクションボタン -->
      <div class="flex gap-3">
        <button
          @click="emit('reset')"
          class="flex-1 btn-secondary flex items-center justify-center gap-2"
        >
          <PhArrowLeft :size="20" weight="bold" />
          <span>別のフィルター</span>
        </button>
        <button
          @click="emit('download')"
          class="flex-1 btn-primary flex items-center justify-center gap-2"
        >
          <PhDownloadSimple :size="20" weight="bold" />
          <span>ダウンロード</span>
        </button>
      </div>
    </div>

    <!-- フィルター選択 -->
    <div v-else class="space-y-4">
      <p class="text-center text-dark-400 mb-6">
        もっとエモくする？フィルターを選んでね
      </p>

      <div class="grid grid-cols-2 gap-4">
        <button
          v-for="filter in filters"
          :key="filter.id"
          @click="emit('apply-filter', filter.id)"
          :disabled="isProcessing"
          :class="[
            'relative group p-6 rounded-2xl border transition-all duration-300',
            'hover:scale-105 hover:border-transparent',
            isProcessing
              ? 'opacity-50 cursor-not-allowed border-dark-700 bg-dark-800'
              : 'border-dark-700 bg-dark-800/50 hover:bg-dark-800',
          ]"
        >
          <!-- グロー効果 -->
          <div
            :class="[
              'absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 blur-xl -z-10',
              filter.bgGlow,
            ]"
          />

          <!-- コンテンツ -->
          <div class="flex flex-col items-center gap-4">
            <!-- アイコン -->
            <div
              :class="[
                'p-4 rounded-xl bg-gradient-to-br',
                filter.gradient,
              ]"
            >
              <PhSpinner
                v-if="isProcessing"
                :size="32"
                weight="bold"
                class="text-dark-900 animate-spin"
              />
              <component
                v-else
                :is="filter.icon"
                :size="32"
                weight="duotone"
                class="text-dark-900"
              />
            </div>

            <!-- テキスト -->
            <div class="text-center">
              <p class="font-medium text-white">{{ filter.name }}</p>
              <p class="text-xs text-dark-400 mt-1">{{ filter.description }}</p>
            </div>
          </div>
        </button>
      </div>
    </div>
  </div>
</template>
