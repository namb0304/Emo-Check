<template>
  <div class="min-h-screen bg-dark-950">
    <!-- Background effects -->
    <div class="fixed inset-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-1/2 -left-1/4 w-[800px] h-[800px] bg-emo-pink/10 rounded-full blur-[120px]" />
      <div class="absolute -bottom-1/2 -right-1/4 w-[800px] h-[800px] bg-emo-purple/10 rounded-full blur-[120px]" />
    </div>

    <!-- Content -->
    <div class="relative z-10">
      <slot />
    </div>
  </div>
</template>
