<script setup lang="ts">
import { PhSparkle } from '@phosphor-icons/vue'

interface Props {
  transparent?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  transparent: false,
})

const route = useRoute()
const isLanding = computed(() => route.path === '/')
</script>

<template>
  <header
    :class="[
      'fixed top-0 left-0 right-0 z-50 transition-all duration-300',
      transparent ? 'bg-transparent' : 'bg-dark-950/80 backdrop-blur-xl border-b border-dark-800/50',
    ]"
  >
    <div class="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
      <!-- Logo -->
      <NuxtLink to="/" class="flex items-center gap-2 group">
        <div class="p-1.5 rounded-lg bg-gradient-to-br from-emo-pink to-emo-purple group-hover:scale-110 transition-transform">
          <PhSparkle :size="20" weight="fill" class="text-white" />
        </div>
        <span class="text-xl font-display font-bold text-white">
          Emo-Check
        </span>
      </NuxtLink>

      <!-- Navigation -->
      <nav class="flex items-center gap-4">
        <NuxtLink
          v-if="isLanding"
          to="/app"
          class="btn-primary text-sm py-2 px-4"
        >
          今すぐ試す
        </NuxtLink>
        <template v-else>
          <NuxtLink
            to="/"
            class="text-sm text-dark-400 hover:text-white transition-colors"
          >
            ホーム
          </NuxtLink>
          <NuxtLink
            to="/app"
            class="btn-primary text-sm py-2 px-4"
          >
            新しい画像
          </NuxtLink>
        </template>
      </nav>
    </div>
  </header>
</template>
