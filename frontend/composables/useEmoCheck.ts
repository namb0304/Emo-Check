import axios from 'axios'

export interface ColorPalette {
  hex: string
  rgb: number[]
  percentage: number
}

export interface EmoComponent {
  name: string
  percentage: number
  description: string
}

export interface PredictResult {
  emo_score: number
  model_used: string
  color_palette: ColorPalette[]
  emo_components: EmoComponent[]
  emo_comment: string
}

export interface BoostResult {
  image_base64: string
  filter_applied: string
}

export type ModelType = 'resnet' | 'vit'
export type FilterType = 'pixel' | 'y2k'

export const useEmoCheck = () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase

  const isLoading = ref(false)
  const error = ref<string | null>(null)

  /**
   * 画像のエモ度を判定する
   */
  const predictEmoScore = async (
    file: File,
    modelType: ModelType = 'resnet'
  ): Promise<PredictResult | null> => {
    isLoading.value = true
    error.value = null

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('model_type', modelType)

      const response = await axios.post<PredictResult>(
        `${apiBase}/predict`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      )

      return response.data
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        error.value = err.response?.data?.detail || 'エモ度の判定に失敗しました'
      } else {
        error.value = '予期しないエラーが発生しました'
      }
      return null
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 画像にフィルターを適用する
   */
  const boostImage = async (
    file: File,
    filterType: FilterType
  ): Promise<BoostResult | null> => {
    isLoading.value = true
    error.value = null

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('filter_type', filterType)

      const response = await axios.post<BoostResult>(
        `${apiBase}/boost`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      )

      return response.data
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        error.value = err.response?.data?.detail || '画像の加工に失敗しました'
      } else {
        error.value = '予期しないエラーが発生しました'
      }
      return null
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Base64画像をダウンロード用のBlobに変換
   */
  const downloadImage = (base64: string, filename: string) => {
    const link = document.createElement('a')
    link.href = `data:image/png;base64,${base64}`
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return {
    isLoading: readonly(isLoading),
    error: readonly(error),
    predictEmoScore,
    boostImage,
    downloadImage,
  }
}
