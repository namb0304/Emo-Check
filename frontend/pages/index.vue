<script setup lang="ts">
import { PhGithubLogo, PhArrowClockwise, PhSparkle } from '@phosphor-icons/vue'
import type { ModelType, FilterType, PredictResult } from '~/composables/useEmoCheck'

// Composable
const { isLoading, error, predictEmoScore, boostImage, downloadImage } = useEmoCheck()

// State
const selectedFile = ref<File | null>(null)
const previewUrl = ref<string | null>(null)
const selectedModel = ref<ModelType>('resnet')
const result = ref<PredictResult | null>(null)
const processedImageUrl = ref<string | null>(null)
const appliedFilter = ref<string | null>(null)
const isBoostProcessing = ref(false)

// 分析実行
const analyzeImage = async () => {
  if (!selectedFile.value) return

  result.value = await predictEmoScore(selectedFile.value, selectedModel.value)
  processedImageUrl.value = null
  appliedFilter.value = null
}

// フィルター適用
const applyFilter = async (filterType: FilterType) => {
  if (!selectedFile.value) return

  isBoostProcessing.value = true
  const boostResult = await boostImage(selectedFile.value, filterType)
  isBoostProcessing.value = false

  if (boostResult) {
    processedImageUrl.value = `data:image/png;base64,${boostResult.image_base64}`
    appliedFilter.value = boostResult.filter_applied
  }
}

// ダウンロード
const handleDownload = () => {
  if (!processedImageUrl.value) return

  const base64 = processedImageUrl.value.split(',')[1]
  const filterName = appliedFilter.value?.toLowerCase().replace(/\s+/g, '_') || 'emo'
  downloadImage(base64, `emo_check_${filterName}_${Date.now()}.png`)
}

// Boosterリセット
const resetBooster = () => {
  processedImageUrl.value = null
  appliedFilter.value = null
}

// 全リセット
const resetAll = () => {
  selectedFile.value = null
  previewUrl.value = null
  result.value = null
  processedImageUrl.value = null
  appliedFilter.value = null
}

// ファイルが変更されたら結果をリセット
watch(selectedFile, () => {
  result.value = null
  processedImageUrl.value = null
  appliedFilter.value = null
})
</script>

<template>
  <div class="min-h-screen bg-dark-900 noise">
    <!-- ローディングオーバーレイ -->
    <LoadingOverlay v-if="isLoading" message="エモ度を分析中" />
    <LoadingOverlay v-if="isBoostProcessing" message="画像を加工中" />

    <!-- 背景のグラデーション効果 -->
    <div class="fixed inset-0 overflow-hidden pointer-events-none">
      <div
        class="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-to-br from-emo-pink/10 to-transparent rounded-full blur-3xl"
      />
      <div
        class="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-to-tl from-emo-purple/10 to-transparent rounded-full blur-3xl"
      />
    </div>

    <!-- メインコンテンツ -->
    <div class="relative z-10">
      <!-- ヘッダー -->
      <header class="py-6 px-4">
        <div class="max-w-4xl mx-auto flex items-center justify-between">
          <div class="flex items-center gap-3">
            <PhSparkle :size="28" weight="duotone" class="text-emo-pink" />
            <h1 class="text-2xl font-display font-bold gradient-text">
              Emo-Check
            </h1>
          </div>
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            class="p-2 rounded-lg hover:bg-dark-800 transition-colors text-dark-400 hover:text-white"
          >
            <PhGithubLogo :size="24" weight="fill" />
          </a>
        </div>
      </header>

      <!-- メインエリア -->
      <main class="px-4 pb-12">
        <div class="max-w-4xl mx-auto">
          <!-- タイトルセクション -->
          <section class="text-center py-12">
            <h2 class="text-4xl md:text-5xl font-display font-bold text-white mb-4">
              あなたの写真の<br />
              <span class="gradient-text">「エモさ」</span>を判定
            </h2>
            <p class="text-dark-400 max-w-md mx-auto">
              AIがあなたの写真を分析して、エモ度をスコア化。<br />
              さらにエモく加工してSNSでシェアしよう。
            </p>
          </section>

          <!-- メインカード -->
          <div class="card p-6 md:p-8">
            <!-- エラー表示 -->
            <div
              v-if="error"
              class="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400"
            >
              {{ error }}
            </div>

            <!-- 結果表示モード -->
            <div v-if="result" class="space-y-8">
              <!-- 画像プレビュー（小さく表示） -->
              <div class="flex justify-center">
                <div class="relative w-40 h-40 rounded-xl overflow-hidden">
                  <img
                    :src="previewUrl || ''"
                    alt="Analyzed image"
                    class="w-full h-full object-cover"
                  />
                </div>
              </div>

              <!-- スコア表示 -->
              <EmoScore :score="result.emo_score" :model-used="result.model_used" />

              <!-- カラーパレット -->
              <div class="pt-8 border-t border-dark-700">
                <ColorPalette :colors="result.color_palette" />
              </div>

              <!-- Emo Booster -->
              <div class="pt-8 border-t border-dark-700">
                <EmoBooster
                  :original-file="selectedFile!"
                  :is-processing="isBoostProcessing"
                  :processed-image-url="processedImageUrl"
                  :applied-filter="appliedFilter"
                  @apply-filter="applyFilter"
                  @download="handleDownload"
                  @reset="resetBooster"
                />
              </div>

              <!-- 別の画像を試すボタン -->
              <div class="pt-6 border-t border-dark-700">
                <button
                  @click="resetAll"
                  class="w-full btn-secondary flex items-center justify-center gap-2"
                >
                  <PhArrowClockwise :size="20" weight="bold" />
                  <span>別の画像を試す</span>
                </button>
              </div>
            </div>

            <!-- アップロードモード -->
            <div v-else class="space-y-6">
              <!-- モデル選択 -->
              <div class="flex justify-center">
                <ModelSelector v-model="selectedModel" />
              </div>

              <!-- 画像アップロード -->
              <ImageUploader v-model="selectedFile" v-model:preview-url="previewUrl" />

              <!-- 分析ボタン -->
              <button
                v-if="selectedFile"
                @click="analyzeImage"
                :disabled="isLoading"
                class="w-full btn-primary text-lg py-4 flex items-center justify-center gap-3"
              >
                <PhSparkle :size="24" weight="fill" />
                <span>エモ度を判定する</span>
              </button>
            </div>
          </div>

          <!-- フッター -->
          <footer class="mt-12 text-center text-sm text-dark-500">
            <p>
              Made with 💜 for Portfolio | Powered by ResNet152 & ViT-B/16
            </p>
          </footer>
        </div>
      </main>
    </div>
  </div>
</template>
