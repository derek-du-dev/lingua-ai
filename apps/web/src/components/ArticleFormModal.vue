<script setup lang="ts">
import { computed, reactive, watch } from 'vue'
import type { ArticlePublic } from '../api/client/types.gen'

const props = defineProps<{
  open: boolean
  article: ArticlePublic | null
  saving: boolean
}>()

const emit = defineEmits<{
  close: []
  save: [payload: {
    title: string
    content: string
  }]
}>()

const form = reactive({
  title: '',
  content: '',
})

const isEdit = computed(() => Boolean(props.article))
const canSubmit = computed(() => !props.saving && form.title.trim().length > 0)

watch(
  () => [props.open, props.article] as const,
  () => {
    if (!props.open) {
      return
    }

    form.title = props.article?.title ?? ''
    form.content = props.article?.content ?? ''
  },
  { immediate: true },
)

function handleSubmit() {
  if (!canSubmit.value) {
    return
  }

  emit('save', {
    title: form.title.trim(),
    content: form.content.trim(),
  })
}
</script>

<template>
  <div v-if="open" class="fixed inset-0 z-40 flex items-center justify-center bg-slate-900/35 px-4 backdrop-blur-sm">
    <form class="max-h-[92vh] w-full max-w-3xl overflow-y-auto rounded-[2rem] border-4 border-white bg-white p-6 shadow-2xl shadow-slate-400/30" @submit.prevent="handleSubmit">
      <div class="flex items-start justify-between gap-4">
        <div>
          <p class="text-sm font-black uppercase tracking-[0.25em] text-sky-500">Article</p>
          <h2 class="mt-1 text-2xl font-black text-slate-900">{{ isEdit ? '编辑文章' : '新增文章' }}</h2>
        </div>
        <button class="text-2xl font-black text-slate-300 transition hover:text-slate-600" type="button" @click="emit('close')">×</button>
      </div>

      <div class="mt-6 grid gap-5">
        <label class="block">
          <span class="mb-2 block text-sm font-bold text-slate-700">文章标题</span>
          <input
            v-model="form.title"
            class="w-full rounded-2xl border-2 border-sky-100 bg-sky-50/70 px-4 py-3 font-semibold outline-none transition focus:border-sky-400 focus:bg-white focus:ring-4 focus:ring-sky-100"
            placeholder="请输入文章标题"
            type="text"
          >
        </label>

        <label class="block">
          <span class="mb-2 block text-sm font-bold text-slate-700">文章内容</span>
          <textarea
            v-model="form.content"
            class="min-h-32 w-full resize-y rounded-2xl border-2 border-sky-100 bg-sky-50/70 px-4 py-3 font-semibold outline-none transition focus:border-sky-400 focus:bg-white focus:ring-4 focus:ring-sky-100"
            placeholder="请输入文章内容"
          />
        </label>

      </div>

      <div class="mt-7 flex justify-end gap-3">
        <button class="rounded-2xl border-2 border-slate-200 px-5 py-3 text-sm font-black text-slate-600 transition hover:bg-slate-50" type="button" @click="emit('close')">
          取消
        </button>
        <button
          class="rounded-2xl bg-sky-600 px-5 py-3 text-sm font-black text-white shadow-lg shadow-sky-200 transition hover:-translate-y-0.5 hover:bg-sky-700 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:shadow-none"
          :disabled="!canSubmit"
          type="submit"
        >
          {{ saving ? '保存中...' : '保存' }}
        </button>
      </div>
    </form>
  </div>
</template>
