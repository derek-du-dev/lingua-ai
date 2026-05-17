<script setup lang="ts">
import { confirmState, notify } from '../services/notify'
</script>

<template>
  <div v-if="confirmState.visible" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/35 px-4 backdrop-blur-sm">
    <div class="w-full max-w-md rounded-[2rem] border-4 border-white bg-white p-6 shadow-2xl shadow-slate-400/30">
      <h2 class="text-xl font-black text-slate-900">{{ confirmState.title }}</h2>
      <p class="mt-3 leading-7 text-slate-600">{{ confirmState.message }}</p>
      <div class="mt-6 flex justify-end gap-3">
        <button
          class="rounded-2xl border-2 border-slate-200 px-5 py-3 text-sm font-black text-slate-600 transition hover:bg-slate-50"
          type="button"
          @click="notify.confirmNo()"
        >
          {{ confirmState.cancelText }}
        </button>
        <button
          class="rounded-2xl px-5 py-3 text-sm font-black text-white shadow-lg transition hover:-translate-y-0.5"
          :class="confirmState.variant === 'danger' ? 'bg-rose-600 shadow-rose-200 hover:bg-rose-700' : 'bg-sky-600 shadow-sky-200 hover:bg-sky-700'"
          type="button"
          @click="notify.confirmYes()"
        >
          {{ confirmState.confirmText }}
        </button>
      </div>
    </div>
  </div>
</template>
