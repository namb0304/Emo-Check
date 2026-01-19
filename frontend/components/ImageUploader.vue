<script setup lang="ts">
import { PhUploadSimple, PhImage, PhX } from '@phosphor-icons/vue'

interface Props {
  modelValue: File | null
  previewUrl: string | null
}

interface Emits {
  (e: 'update:modelValue', value: File | null): void
  (e: 'update:previewUrl', value: string | null): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const isDragging = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

const handleDrop = (event: DragEvent) => {
  isDragging.value = false
  const files = event.dataTransfer?.files
  if (files && files.length > 0) {
    handleFile(files[0])
  }
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (files && files.length > 0) {
    handleFile(files[0])
  }
}

const handleFile = (file: File) => {
  // HEIC/HEIFファイルもサポート
  const isHeic = file.name.toLowerCase().endsWith('.heic') || file.name.toLowerCase().endsWith('.heif')
  if (!file.type.startsWith('image/') && !isHeic) {
    alert('画像ファイルを選択してください')
    return
  }

  emit('update:modelValue', file)

  // プレビュー用のURLを生成
  const reader = new FileReader()
  reader.onload = (e) => {
    emit('update:previewUrl', e.target?.result as string)
  }
  reader.readAsDataURL(file)
}

const clearFile = () => {
  emit('update:modelValue', null)
  emit('update:previewUrl', null)
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const openFileDialog = () => {
  fileInput.value?.click()
}
</script>

<template>
  <div class="w-full">
    <!-- プレビュー表示 -->
    <div v-if="previewUrl" class="relative group">
      <div class="relative overflow-hidden rounded-2xl gradient-border">
        <img
          :src="previewUrl"
          alt="Uploaded preview"
          class="w-full h-auto max-h-[400px] object-contain bg-dark-950"
        />
        <!-- オーバーレイ -->
        <div
          class="absolute inset-0 bg-dark-950/60 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center"
        >
          <button
            @click="clearFile"
            class="p-3 rounded-full bg-red-500/80 hover:bg-red-500 transition-colors"
          >
            <PhX :size="24" weight="bold" />
          </button>
        </div>
      </div>
      <p class="mt-3 text-sm text-dark-400 text-center">
        クリックで画像を削除
      </p>
    </div>

    <!-- アップロードエリア -->
    <div
      v-else
      @dragenter.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @dragover.prevent
      @drop.prevent="handleDrop"
      @click="openFileDialog"
      :class="[
        'relative cursor-pointer rounded-2xl border-2 border-dashed transition-all duration-300',
        'flex flex-col items-center justify-center py-16 px-8',
        isDragging
          ? 'border-emo-purple bg-emo-purple/10 scale-[1.02]'
          : 'border-dark-600 hover:border-emo-pink/50 bg-dark-800/30',
      ]"
    >
      <!-- アイコン -->
      <div
        :class="[
          'mb-6 p-5 rounded-full transition-all duration-300',
          isDragging ? 'bg-emo-purple/20' : 'bg-dark-700',
        ]"
      >
        <PhUploadSimple
          v-if="isDragging"
          :size="48"
          weight="duotone"
          class="text-emo-purple"
        />
        <PhImage v-else :size="48" weight="duotone" class="text-dark-400" />
      </div>

      <!-- テキスト -->
      <p class="text-lg font-medium text-white mb-2">
        <span v-if="isDragging" class="text-emo-purple">ドロップして判定</span>
        <span v-else>画像をドラッグ&ドロップ</span>
      </p>
      <p class="text-sm text-dark-400">または クリックして選択</p>

      <!-- サポートフォーマット -->
      <div class="mt-6 flex items-center gap-2 text-xs text-dark-500">
        <span class="px-2 py-1 rounded bg-dark-700">JPG</span>
        <span class="px-2 py-1 rounded bg-dark-700">PNG</span>
        <span class="px-2 py-1 rounded bg-dark-700">HEIC</span>
      </div>

      <!-- Hidden input -->
      <input
        ref="fileInput"
        type="file"
        accept="image/*,.heic,.heif"
        class="hidden"
        @change="handleFileSelect"
      />
    </div>
  </div>
</template>
