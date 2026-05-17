<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { readLearningArticleLearningArticlesArticleIdGet } from '../api/client/sdk.gen'
import type { LearningArticleDetailPublic } from '../api/client/types.gen'
import { getApiErrorMessage } from '../services/api'
import { notify } from '../services/notify'

const route = useRoute()
const router = useRouter()
const article = ref<LearningArticleDetailPublic | null>(null)
const loading = ref(false)
const audioRef = ref<HTMLAudioElement | null>(null)
const sentenceListRef = ref<HTMLElement | null>(null)
const currentIndex = ref<number | null>(null)
const isPlaying = ref(false)

const sentences = computed(() => article.value?.sentences ?? [])
const currentSentence = computed(() => {
  if (currentIndex.value === null) {
    return null
  }

  return sentences.value[currentIndex.value] ?? null
})
const hasPlayableSentence = computed(() => sentences.value.some((sentence) => sentence.audio_url))
const backPath = computed(() => (article.value?.id ? `/learn/articles/${article.value.id}` : '/learn'))

function getArticleId() {
  const articleId = route.params.articleId
  return Array.isArray(articleId) ? articleId[0] : articleId
}

function resetPlayback() {
  const audio = audioRef.value
  if (audio) {
    audio.pause()
    audio.removeAttribute('src')
    audio.load()
  }

  currentIndex.value = null
  isPlaying.value = false
}

function scrollCurrentSentenceIntoView() {
  if (currentIndex.value === null || !sentenceListRef.value) {
    return
  }

  const currentElement = sentenceListRef.value.querySelector<HTMLElement>(`[data-sentence-index="${currentIndex.value}"]`)
  currentElement?.scrollIntoView({ behavior: 'smooth', block: 'center' })
}

async function playCurrentAudio() {
  const audio = audioRef.value
  if (!audio) {
    return
  }

  try {
    await audio.play()
  } catch {
    notify.error('播放失败，请稍后重试。')
  }
}

async function playSentence(index: number) {
  const sentence = sentences.value[index]
  if (!sentence?.audio_url) {
    notify.warning('该句暂无音频。')
    return
  }

  currentIndex.value = index
  await nextTick()
  scrollCurrentSentenceIntoView()

  const audio = audioRef.value
  if (!audio) {
    return
  }

  audio.src = sentence.audio_url
  audio.currentTime = 0
  await playCurrentAudio()
}

async function replayCurrent() {
  if (currentIndex.value === null) {
    const firstPlayableIndex = sentences.value.findIndex((sentence) => sentence.audio_url)
    if (firstPlayableIndex >= 0) {
      await playSentence(firstPlayableIndex)
    }
    return
  }

  const audio = audioRef.value
  if (!audio) {
    return
  }

  audio.currentTime = 0
  await playCurrentAudio()
}

async function playNextSentence() {
  if (currentIndex.value === null) {
    return
  }

  const startIndex = currentIndex.value + 1
  const nextIndex = sentences.value.findIndex((sentence, index) => index >= startIndex && sentence.audio_url)
  if (nextIndex < 0) {
    isPlaying.value = false
    return
  }

  await playSentence(nextIndex)
}

async function loadArticle() {
  const articleId = getArticleId()
  if (!articleId) {
    return
  }

  loading.value = true
  article.value = null
  resetPlayback()
  const response = await readLearningArticleLearningArticlesArticleIdGet({ path: { article_id: articleId } })
  loading.value = false

  if (response.data) {
    article.value = response.data
    return
  }

  notify.error(getApiErrorMessage(response.error, '加载文章失败。'))
}

watch(() => route.params.articleId, loadArticle, { immediate: true })
</script>

<template>
  <section class="flex h-[calc(100vh-8.5rem)] flex-col gap-4 overflow-hidden">
    <button class="rounded-2xl bg-white px-4 py-2 text-sm font-black text-sky-700 shadow-lg shadow-sky-100 transition hover:-translate-y-0.5 hover:bg-sky-50" type="button" @click="router.push(backPath)">
      返回文章学习
    </button>

    <div v-if="loading" class="rounded-[2rem] border-4 border-white bg-white/80 px-6 py-16 text-center text-sm font-bold text-slate-500 shadow-xl shadow-sky-100/70 backdrop-blur">
      正在加载精听内容...
    </div>

    <template v-else-if="article">
      <article class="shrink-0 rounded-[2rem] border-4 border-white bg-white/80 p-4 shadow-xl shadow-sky-100/70 backdrop-blur sm:p-5">
        <p class="text-sm font-black uppercase tracking-[0.25em] text-sky-500">Intensive Listening</p>
        <h1 class="mt-2 text-3xl font-black text-slate-900">{{ article.title }}</h1>
        <p class="mt-3 text-sm font-bold leading-6 text-slate-500">点击句子从头播放单句音频，当前播放句会自动高亮并滚动到列表中间。</p>
      </article>

      <section class="flex min-h-0 flex-1 flex-col rounded-[2rem] border-4 border-white bg-white/80 p-4 shadow-xl shadow-sky-100/70 backdrop-blur sm:p-6">
        <div class="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p class="text-sm font-black uppercase tracking-[0.25em] text-emerald-500">Sentences</p>
            <h2 class="mt-1 text-2xl font-black text-slate-900">句子列表</h2>
          </div>
          <div class="rounded-2xl bg-sky-50 px-4 py-3 text-sm font-black text-sky-700">共 {{ sentences.length }} 句</div>
        </div>

        <div v-if="sentences.length === 0" class="mt-6 rounded-[1.5rem] bg-white px-5 py-12 text-center text-sm font-bold text-slate-400">
          暂无可用于精听练习的句子。
        </div>

        <div v-else ref="sentenceListRef" class="mt-6 min-h-0 flex-1 space-y-3 overflow-y-auto rounded-[1.5rem] border-2 border-slate-100 bg-white p-3">
          <button
            v-for="(sentence, index) in sentences"
            :key="index"
            class="w-full rounded-2xl px-4 py-4 text-left transition"
            :class="currentIndex === index ? 'bg-sky-100 text-sky-900 ring-2 ring-sky-300' : 'bg-slate-50 text-slate-700 hover:bg-sky-50'"
            :data-sentence-index="index"
            type="button"
            @click="playSentence(index)"
          >
            <span class="mr-3 align-top text-sm font-black text-sky-600">{{ index + 1 }}.</span>
            <span class="font-semibold leading-7">{{ sentence.content }}</span>
            <span v-if="!sentence.audio_url" class="ml-3 inline-flex rounded-full bg-slate-100 px-2 py-1 text-xs font-black text-slate-400">暂无音频</span>
          </button>
        </div>

        <div class="mt-4 shrink-0 rounded-[1.5rem] border-2 border-sky-100 bg-white p-4 shadow-lg shadow-sky-100">
          <div class="space-y-3">
            <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div class="min-w-0">
                <p class="text-xs font-black uppercase tracking-[0.2em] text-sky-500">播放器</p>
                <p class="mt-1 truncate text-sm font-black text-slate-900">
                  {{ currentIndex === null ? '请选择一句开始精听' : `第 ${currentIndex + 1} 句：${currentSentence?.content ?? ''}` }}
                </p>
              </div>
              <button
                class="rounded-2xl bg-slate-900 px-5 py-3 text-sm font-black text-white shadow-lg shadow-slate-200 transition hover:-translate-y-0.5 hover:bg-sky-600 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:shadow-none"
                :disabled="!hasPlayableSentence"
                type="button"
                @click="replayCurrent"
              >
                {{ currentIndex === null ? '播放第一句' : '重播当前句' }}
              </button>
            </div>
            <audio ref="audioRef" class="w-full" controls :src="currentSentence?.audio_url" @ended="playNextSentence" @pause="isPlaying = false" @play="isPlaying = true"></audio>
          </div>
        </div>
      </section>
    </template>
  </section>
</template>
