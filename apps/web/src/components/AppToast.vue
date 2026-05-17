<script setup lang="ts">
import { removeToast, toastState } from '../services/notify'

const styles = {
  info: 'border-sky-100 bg-sky-50 text-sky-700',
  success: 'border-emerald-100 bg-emerald-50 text-emerald-700',
  warning: 'border-amber-100 bg-amber-50 text-amber-700',
  error: 'border-rose-100 bg-rose-50 text-rose-700',
}
</script>

<template>
  <div class="fixed right-4 top-4 z-50 w-[min(24rem,calc(100vw-2rem))] space-y-3">
    <div
      v-for="toast in toastState.items"
      :key="toast.id"
      class="flex items-start justify-between gap-3 rounded-2xl border-2 px-4 py-3 text-sm font-bold shadow-xl backdrop-blur"
      :class="styles[toast.type]"
    >
      <span>{{ toast.message }}</span>
      <button class="text-lg leading-none opacity-60 transition hover:opacity-100" type="button" @click="removeToast(toast.id)">
        ×
      </button>
    </div>
  </div>
</template>
