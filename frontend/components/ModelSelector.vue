<script setup lang="ts">
import { PhGridNine, PhSquaresFour } from '@phosphor-icons/vue'
import type { ModelType } from '~/composables/useEmoCheck'

interface Props {
  modelValue: ModelType
}

interface Emits {
  (e: 'update:modelValue', value: ModelType): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const models = [
  {
    id: 'resnet' as ModelType,
    name: 'ResNet152',
    shortName: 'ResNet',
    icon: PhGridNine,
    tooltip: '細部の特徴を重視',
    description: '画像を細かく分析して、色や質感からエモさを判定',
    color: 'from-emo-pink to-emo-orange',
    iconBg: 'bg-emo-pink/20',
  },
  {
    id: 'vit' as ModelType,
    name: 'ViT-B/16',
    shortName: 'ViT',
    icon: PhSquaresFour,
    tooltip: '全体の雰囲気を重視',
    description: '写真全体の構図や雰囲気からエモさを判定',
    color: 'from-emo-purple to-emo-blue',
    iconBg: 'bg-emo-purple/20',
  },
]

const selectModel = (modelId: ModelType) => {
  emit('update:modelValue', modelId)
}

// 選択中のモデル情報を取得
const selectedModel = computed(() => models.find(m => m.id === props.modelValue))
</script>

<template>
  <div class="w-full max-w-md">
    <!-- ラベル -->
    <div class="flex items-center gap-2 mb-3">
      <span class="text-sm text-dark-400">AIモデルを選択</span>
      <span class="text-xs text-dark-500">（お好みで）</span>
    </div>

    <!-- モデル選択ボタン -->
    <div class="grid grid-cols-2 gap-3">
      <button
        v-for="model in models"
        :key="model.id"
        @click="selectModel(model.id)"
        :class="[
          'relative p-4 rounded-xl border-2 transition-all duration-300 text-left group',
          modelValue === model.id
            ? 'border-transparent'
            : 'border-dark-700 hover:border-dark-600 bg-dark-800/50',
        ]"
      >
        <!-- 選択時のグラデーション背景 -->
        <div
          v-if="modelValue === model.id"
          :class="[
            'absolute inset-0 rounded-xl bg-gradient-to-br opacity-20',
            model.color,
          ]"
        />
        <div
          v-if="modelValue === model.id"
          :class="[
            'absolute inset-0 rounded-xl border-2 border-transparent bg-gradient-to-br',
            model.color,
          ]"
          style="mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0); mask-composite: xor; -webkit-mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0); -webkit-mask-composite: xor;"
        />

        <div class="relative z-10">
          <!-- アイコンと名前 -->
          <div class="flex items-center gap-3 mb-2">
            <div
              :class="[
                'w-10 h-10 rounded-lg flex items-center justify-center transition-colors',
                modelValue === model.id ? model.iconBg : 'bg-dark-700',
              ]"
            >
              <component
                :is="model.icon"
                :size="24"
                weight="duotone"
                :class="modelValue === model.id ? 'text-white' : 'text-dark-400'"
              />
            </div>
            <div>
              <div class="font-medium text-white">{{ model.shortName }}</div>
              <div class="text-xs text-dark-500">{{ model.name }}</div>
            </div>
          </div>

          <!-- 説明（ツールチップ風） -->
          <div class="text-xs text-dark-400 leading-relaxed">
            {{ model.tooltip }}
          </div>
        </div>

        <!-- 選択インジケーター -->
        <div
          v-if="modelValue === model.id"
          class="absolute top-2 right-2 w-2 h-2 rounded-full bg-green-400"
        />
      </button>
    </div>

    <!-- 選択中のモデルの詳細説明 -->
    <div
      v-if="selectedModel"
      class="mt-3 p-3 rounded-lg bg-dark-800/50 border border-dark-700 text-xs text-dark-400"
    >
      <span class="text-dark-300">{{ selectedModel.shortName }}:</span>
      {{ selectedModel.description }}
    </div>
  </div>
</template>
