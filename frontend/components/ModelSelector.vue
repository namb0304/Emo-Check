<script setup lang="ts">
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
    description: 'CNNベース',
    color: 'from-emo-pink to-emo-orange',
  },
  {
    id: 'vit' as ModelType,
    name: 'ViT-B/16',
    description: 'Transformer',
    color: 'from-emo-purple to-emo-blue',
  },
]

const selectModel = (modelId: ModelType) => {
  emit('update:modelValue', modelId)
}
</script>

<template>
  <div class="flex items-center gap-3">
    <span class="text-sm text-dark-400 mr-1">Model:</span>
    <div class="flex gap-2">
      <button
        v-for="model in models"
        :key="model.id"
        @click="selectModel(model.id)"
        :class="[
          'relative px-4 py-2 rounded-xl text-sm font-medium transition-all duration-300',
          modelValue === model.id
            ? 'text-white'
            : 'text-dark-400 hover:text-white bg-dark-800 hover:bg-dark-700',
        ]"
      >
        <!-- Active gradient background -->
        <div
          v-if="modelValue === model.id"
          :class="[
            'absolute inset-0 rounded-xl bg-gradient-to-r opacity-100',
            model.color,
          ]"
        />
        <span class="relative z-10 flex items-center gap-2">
          <span>{{ model.name }}</span>
          <span
            v-if="modelValue === model.id"
            class="text-xs opacity-75"
          >
            ({{ model.description }})
          </span>
        </span>
      </button>
    </div>
  </div>
</template>
