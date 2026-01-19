<script setup lang="ts">
import { PhSparkle, PhCamera, PhMagicWand, PhShareNetwork, PhArrowRight, PhPlay } from '@phosphor-icons/vue'

// スクロールに応じたヘッダーの透明度制御
const isScrolled = ref(false)

onMounted(() => {
  const handleScroll = () => {
    isScrolled.value = window.scrollY > 50
  }
  window.addEventListener('scroll', handleScroll)
  onUnmounted(() => window.removeEventListener('scroll', handleScroll))
})

// 特徴リスト
const features = [
  {
    icon: PhCamera,
    title: 'AIエモ度判定',
    description: 'ResNet152とViT-B/16の2つのAIモデルがあなたの写真を分析。エモさを0〜100%でスコア化します。',
    gradient: 'from-emo-pink to-rose-500',
  },
  {
    icon: PhMagicWand,
    title: 'エモ加工フィルター',
    description: 'Pixel ArtやY2K Filmなど、エモさを引き立てるフィルターで写真をさらに魅力的に。',
    gradient: 'from-emo-purple to-violet-500',
  },
  {
    icon: PhShareNetwork,
    title: 'SNSシェア',
    description: '判定結果をおしゃれなカードにして、そのままSNSでシェア。友達と盛り上がろう。',
    gradient: 'from-emo-blue to-cyan-500',
  },
]

// 使い方ステップ
const steps = [
  { number: '01', title: '写真をアップロード', description: 'ドラッグ&ドロップまたはクリックで選択' },
  { number: '02', title: 'AIが分析', description: '数秒でエモ度とカラーパレットを解析' },
  { number: '03', title: '加工&シェア', description: 'フィルターで加工してSNSへ投稿' },
]
</script>

<template>
  <div class="min-h-screen bg-dark-950">
    <!-- Header -->
    <AppHeader :transparent="!isScrolled" />

    <!-- Hero Section -->
    <section class="relative min-h-screen flex items-center justify-center overflow-hidden">
      <!-- Animated background -->
      <div class="absolute inset-0">
        <div class="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-emo-pink/20 rounded-full blur-[100px] animate-pulse-slow" />
        <div class="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-emo-purple/20 rounded-full blur-[100px] animate-pulse-slow animation-delay-200" />
        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] bg-emo-blue/10 rounded-full blur-[80px] animate-float" />
      </div>

      <!-- Grid pattern overlay -->
      <div class="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:100px_100px]" />

      <!-- Content -->
      <div class="relative z-10 text-center px-4 max-w-4xl mx-auto pt-20">
        <!-- Badge -->
        <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-dark-800/50 border border-dark-700 mb-8 animate-fade-in">
          <span class="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          <span class="text-sm text-dark-300">AI Powered by ResNet152 & ViT-B/16</span>
        </div>

        <!-- Main heading -->
        <h1 class="text-5xl md:text-7xl font-display font-bold text-white mb-6 animate-slide-up">
          あなたの写真の<br />
          <span class="gradient-text bg-300% animate-gradient">「エモさ」</span>を<br />
          数値化する
        </h1>

        <!-- Subheading -->
        <p class="text-lg md:text-xl text-dark-400 max-w-2xl mx-auto mb-10 animate-slide-up animation-delay-100">
          AIがあなたの写真を分析して、エモ度をスコア化。<br class="hidden md:block" />
          さらにエモく加工してSNSでシェアしよう。
        </p>

        <!-- CTA Buttons -->
        <div class="flex flex-col sm:flex-row items-center justify-center gap-4 animate-slide-up animation-delay-200">
          <NuxtLink
            to="/app"
            class="group btn-primary text-lg py-4 px-8 flex items-center gap-3"
          >
            <PhSparkle :size="24" weight="fill" />
            <span>今すぐ試す</span>
            <PhArrowRight :size="20" weight="bold" class="group-hover:translate-x-1 transition-transform" />
          </NuxtLink>
          <a
            href="#how-to-use"
            class="btn-secondary text-lg py-4 px-8 flex items-center gap-3"
          >
            <PhPlay :size="20" weight="fill" />
            <span>使い方を見る</span>
          </a>
        </div>

        <!-- Demo preview -->
        <div class="mt-16 relative animate-slide-up animation-delay-300">
          <div class="relative mx-auto max-w-2xl">
            <!-- Glow effect -->
            <div class="absolute -inset-4 bg-gradient-to-r from-emo-pink via-emo-purple to-emo-blue rounded-3xl blur-2xl opacity-30" />

            <!-- Screenshot mockup -->
            <div class="relative bg-dark-900 rounded-2xl border border-dark-700 overflow-hidden shadow-2xl">
              <div class="flex items-center gap-2 px-4 py-3 bg-dark-800 border-b border-dark-700">
                <div class="w-3 h-3 rounded-full bg-red-500" />
                <div class="w-3 h-3 rounded-full bg-yellow-500" />
                <div class="w-3 h-3 rounded-full bg-green-500" />
              </div>
              <div class="p-8 text-center">
                <div class="text-6xl font-display font-bold gradient-text mb-2">87%</div>
                <div class="text-dark-400 text-sm uppercase tracking-wider">Emo Score</div>
                <div class="mt-4 flex justify-center gap-2">
                  <div class="w-8 h-8 rounded-lg bg-pink-400" />
                  <div class="w-8 h-8 rounded-lg bg-purple-400" />
                  <div class="w-8 h-8 rounded-lg bg-blue-400" />
                  <div class="w-8 h-8 rounded-lg bg-orange-400" />
                  <div class="w-8 h-8 rounded-lg bg-teal-400" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Scroll indicator -->
      <div class="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
        <div class="w-6 h-10 rounded-full border-2 border-dark-600 flex justify-center pt-2">
          <div class="w-1.5 h-3 rounded-full bg-dark-500" />
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="py-24 px-4">
      <div class="max-w-6xl mx-auto">
        <div class="text-center mb-16">
          <h2 class="text-3xl md:text-4xl font-display font-bold text-white mb-4">
            3つの特徴
          </h2>
          <p class="text-dark-400">エモさを科学する、新しい写真体験</p>
        </div>

        <div class="grid md:grid-cols-3 gap-8">
          <div
            v-for="(feature, index) in features"
            :key="feature.title"
            class="group relative p-8 rounded-2xl bg-dark-900/50 border border-dark-800 hover:border-dark-700 transition-all duration-300"
          >
            <!-- Icon -->
            <div
              :class="[
                'w-14 h-14 rounded-xl flex items-center justify-center mb-6 bg-gradient-to-br',
                feature.gradient,
              ]"
            >
              <component :is="feature.icon" :size="28" weight="duotone" class="text-white" />
            </div>

            <!-- Content -->
            <h3 class="text-xl font-bold text-white mb-3">{{ feature.title }}</h3>
            <p class="text-dark-400 leading-relaxed">{{ feature.description }}</p>

            <!-- Hover glow -->
            <div
              :class="[
                'absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 -z-10 blur-xl',
                `bg-gradient-to-br ${feature.gradient}`,
              ]"
              style="opacity: 0.1"
            />
          </div>
        </div>
      </div>
    </section>

    <!-- How to Use Section -->
    <section id="how-to-use" class="py-24 px-4 bg-dark-900/50">
      <div class="max-w-4xl mx-auto">
        <div class="text-center mb-16">
          <h2 class="text-3xl md:text-4xl font-display font-bold text-white mb-4">
            使い方
          </h2>
          <p class="text-dark-400">たった3ステップでエモ度を判定</p>
        </div>

        <div class="space-y-8">
          <div
            v-for="(step, index) in steps"
            :key="step.number"
            class="flex items-start gap-6 p-6 rounded-2xl bg-dark-800/30 border border-dark-800"
          >
            <!-- Number -->
            <div class="flex-shrink-0 w-16 h-16 rounded-xl bg-gradient-to-br from-emo-pink to-emo-purple flex items-center justify-center">
              <span class="text-2xl font-display font-bold text-white">{{ step.number }}</span>
            </div>

            <!-- Content -->
            <div class="pt-2">
              <h3 class="text-xl font-bold text-white mb-2">{{ step.title }}</h3>
              <p class="text-dark-400">{{ step.description }}</p>
            </div>
          </div>
        </div>

        <!-- CTA -->
        <div class="text-center mt-12">
          <NuxtLink
            to="/app"
            class="inline-flex items-center gap-3 btn-primary text-lg py-4 px-8"
          >
            <PhSparkle :size="24" weight="fill" />
            <span>さっそく試してみる</span>
          </NuxtLink>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="py-8 px-4 border-t border-dark-800">
      <div class="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        <div class="flex items-center gap-2">
          <PhSparkle :size="20" weight="fill" class="text-emo-pink" />
          <span class="font-display font-bold text-white">Emo-Check</span>
        </div>
        <p class="text-sm text-dark-500">
          Made with 💜 for Portfolio | Powered by ResNet152 & ViT-B/16
        </p>
      </div>
    </footer>
  </div>
</template>
