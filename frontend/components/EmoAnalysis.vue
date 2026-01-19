<script setup lang="ts">
import { PhQuotes } from '@phosphor-icons/vue'

interface EmoComponent {
  name: string
  percentage: number
  description: string
}

interface Props {
  components: EmoComponent[]
  comment: string
}

const props = defineProps<Props>()

// 成分に応じた色を返す
const getComponentColor = (name: string): string => {
  const colorMap: Record<string, string> = {
    'ノスタルジー': 'from-amber-400 to-orange-500',
    '儚さ': 'from-pink-400 to-rose-500',
    '青春': 'from-cyan-400 to-blue-500',
    'メランコリー': 'from-purple-400 to-violet-500',
    '夕暮れ感': 'from-orange-400 to-red-500',
    '孤独': 'from-slate-400 to-gray-500',
    '希望': 'from-emerald-400 to-teal-500',
    '哀愁': 'from-indigo-400 to-blue-600',
  }
  return colorMap[name] || 'from-gray-400 to-gray-500'
}

const getBarColor = (name: string): string => {
  const colorMap: Record<string, string> = {
    'ノスタルジー': 'bg-gradient-to-r from-amber-400 to-orange-500',
    '儚さ': 'bg-gradient-to-r from-pink-400 to-rose-500',
    '青春': 'bg-gradient-to-r from-cyan-400 to-blue-500',
    'メランコリー': 'bg-gradient-to-r from-purple-400 to-violet-500',
    '夕暮れ感': 'bg-gradient-to-r from-orange-400 to-red-500',
    '孤独': 'bg-gradient-to-r from-slate-400 to-gray-500',
    '希望': 'bg-gradient-to-r from-emerald-400 to-teal-500',
    '哀愁': 'bg-gradient-to-r from-indigo-400 to-blue-600',
  }
  return colorMap[name] || 'bg-gradient-to-r from-gray-400 to-gray-500'
}
</script>

<template>
  <div class="w-full animate-slide-up">
    <!-- ヘッダー -->
    <div class="flex items-center gap-3 mb-6">
      <div class="w-8 h-[2px] bg-gradient-to-r from-emo-purple to-emo-blue" />
      <h3 class="text-sm font-medium text-dark-400 tracking-wider uppercase">
        Emo Analysis
      </h3>
      <div class="flex-1 h-[1px] bg-dark-700" />
    </div>

    <!-- AIコメント -->
    <div class="mb-6 p-4 rounded-xl bg-dark-800/50 border border-dark-700">
      <div class="flex gap-3">
        <PhQuotes :size="24" weight="fill" class="text-emo-purple flex-shrink-0 mt-1" />
        <p class="text-white leading-relaxed italic">
          {{ comment }}
        </p>
      </div>
    </div>

    <!-- 成分グラフ -->
    <div class="space-y-4">
      <div
        v-for="(component, index) in components"
        :key="component.name"
        class="group"
        :style="{ animationDelay: `${index * 100}ms` }"
      >
        <!-- ラベルとパーセンテージ -->
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center gap-2">
            <span class="text-white font-medium">{{ component.name }}</span>
            <span class="text-xs text-dark-500 hidden sm:inline">
              {{ component.description }}
            </span>
          </div>
          <span class="text-lg font-display font-bold text-white">
            {{ component.percentage }}%
          </span>
        </div>

        <!-- プログレスバー -->
        <div class="h-3 bg-dark-800 rounded-full overflow-hidden">
          <div
            :class="[
              'h-full rounded-full transition-all duration-1000 ease-out',
              getBarColor(component.name),
            ]"
            :style="{ width: `${component.percentage}%` }"
          />
        </div>
      </div>
    </div>

    <!-- 説明 -->
    <p class="mt-6 text-xs text-dark-500 text-center">
      AIが画像から検出したエモさの成分内訳
    </p>
  </div>
</template>
