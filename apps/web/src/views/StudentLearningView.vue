<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  readLearningArticleLearningArticlesArticleIdGet,
  submitLearningArticleAnswersLearningArticlesArticleIdAnswersPost,
} from '../api/client/sdk.gen'
import type {
  LearningAnswerResultItem,
  LearningAnswerSubmissionResult,
  LearningArticleDetailPublic,
  LearningArticleQuestionPublic,
} from '../api/client/types.gen'
import { getApiErrorMessage } from '../services/api'
import { notify } from '../services/notify'
import { buildHighlightRanges, buildTextSegments, highlightClass, type TextSegment } from '../utils/articleHighlights'

type AnswerChoice = 'A' | 'B' | 'C' | 'D'

const optionKeys: AnswerChoice[] = ['A', 'B', 'C', 'D']
const route = useRoute()
const router = useRouter()
const article = ref<LearningArticleDetailPublic | null>(null)
const selectedAnswers = ref<Record<string, AnswerChoice>>({})
const result = ref<LearningAnswerSubmissionResult | null>(null)
const loading = ref(false)
const submitting = ref(false)
const hoveredKeyPointId = ref('')
const tooltipPosition = ref({ x: 0, y: 0 })
let tooltipHideTimer: ReturnType<typeof setTimeout> | null = null

const questions = computed(() => article.value?.questions ?? [])
const articleContent = computed(() => article.value?.content ?? '')
const articleTextSegments = computed(() => buildTextSegments(articleContent.value, buildHighlightRanges(articleContent.value, article.value?.key_points ?? [])))
const hoveredKeyPoint = computed(() => article.value?.key_points?.find((point) => point.id === hoveredKeyPointId.value && point.abbreviation) ?? null)
const canSubmit = computed(() => questions.value.length > 0 && questions.value.every((question) => selectedAnswers.value[question.id]))
const resultItemsByQuestionId = computed(() => {
  const items: Record<string, LearningAnswerResultItem> = {}
  for (const item of result.value?.items ?? []) {
    items[item.question_id] = item
  }
  return items
})

function getArticleId() {
  const articleId = route.params.articleId
  return Array.isArray(articleId) ? articleId[0] : articleId
}

function getOptionEntries(question: LearningArticleQuestionPublic) {
  return optionKeys.map((key) => [key, question.options[key] ?? ''] as const).filter(([, text]) => text)
}

function selectAnswer(questionId: string, answer: AnswerChoice) {
  if (result.value) {
    return
  }

  selectedAnswers.value[questionId] = answer
}

function clearTooltipTimer() {
  if (tooltipHideTimer) {
    clearTimeout(tooltipHideTimer)
    tooltipHideTimer = null
  }
}

function showTooltip(segment: TextSegment, event: MouseEvent) {
  if (!segment.keyPointId) {
    return
  }

  const point = article.value?.key_points?.find((item) => item.id === segment.keyPointId)
  if (!point?.abbreviation) {
    return
  }

  const target = event.currentTarget instanceof HTMLElement ? event.currentTarget : null
  const rect = target?.getBoundingClientRect()
  clearTooltipTimer()
  hoveredKeyPointId.value = segment.keyPointId
  tooltipPosition.value = rect
    ? { x: rect.left, y: rect.bottom }
    : { x: event.clientX, y: event.clientY }
}

function scheduleHideTooltip() {
  clearTooltipTimer()
  tooltipHideTimer = setTimeout(() => {
    hoveredKeyPointId.value = ''
  }, 180)
}

function openIntensiveListening() {
  if (!article.value?.id) {
    return
  }

  router.push(`/learn/articles/${article.value.id}/intensive-listening`)
}

async function loadArticle() {
  const articleId = getArticleId()
  if (!articleId) {
    return
  }

  loading.value = true
  article.value = null
  result.value = null
  selectedAnswers.value = {}
  hoveredKeyPointId.value = ''
  const response = await readLearningArticleLearningArticlesArticleIdGet({ path: { article_id: articleId } })
  loading.value = false

  if (response.data) {
    article.value = response.data
    return
  }

  notify.error(getApiErrorMessage(response.error, '加载文章失败。'))
}

async function submitAnswers() {
  const articleId = article.value?.id
  if (!articleId || submitting.value) {
    return
  }

  if (!canSubmit.value) {
    notify.warning('请完成所有题目后提交。')
    return
  }

  submitting.value = true
  const response = await submitLearningArticleAnswersLearningArticlesArticleIdAnswersPost({
    path: { article_id: articleId },
    body: { answers: selectedAnswers.value },
  })
  submitting.value = false

  if (response.data) {
    result.value = response.data
    notify.success(`已提交，答对 ${response.data.correct} / ${response.data.total} 题。`)
    return
  }

  notify.error(getApiErrorMessage(response.error, '提交答案失败。'))
}

watch(() => route.params.articleId, loadArticle, { immediate: true })
</script>

<template>
  <section class="space-y-6">
    <button class="rounded-2xl bg-white px-4 py-2 text-sm font-black text-sky-700 shadow-lg shadow-sky-100 transition hover:-translate-y-0.5 hover:bg-sky-50" type="button" @click="router.push('/learn')">
      返回学习空间
    </button>

    <div v-if="loading" class="rounded-[2rem] border-4 border-white bg-white/80 px-6 py-16 text-center text-sm font-bold text-slate-500 shadow-xl shadow-sky-100/70 backdrop-blur">
      正在加载文章...
    </div>

    <template v-else-if="article">
      <div class="grid gap-6 xl:grid-cols-[minmax(0,1.15fr)_minmax(22rem,0.85fr)] xl:items-start">
        <article class="min-w-0 rounded-[2rem] border-4 border-white bg-white/80 p-5 shadow-xl shadow-sky-100/70 backdrop-blur sm:p-7">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p class="text-sm font-black uppercase tracking-[0.25em] text-sky-500">Article</p>
            <h1 class="mt-2 text-3xl font-black text-slate-900">{{ article.title }}</h1>
          </div>
          <button class="rounded-2xl bg-sky-600 px-5 py-3 text-sm font-black text-white shadow-lg shadow-sky-200 transition hover:-translate-y-0.5 hover:bg-sky-700" type="button" @click="openIntensiveListening">
            精听练习
          </button>
        </div>

        <div v-if="article.audio_url" class="mt-6 rounded-[1.5rem] border-2 border-sky-100 bg-sky-50 p-4">
          <p class="mb-3 text-sm font-black text-sky-700">文章音频</p>
          <audio class="w-full" controls :src="article.audio_url"></audio>
        </div>

        <div class="mt-6 rounded-[1.5rem] border-2 border-slate-100 bg-white p-5 text-base font-semibold leading-8 text-slate-700 whitespace-pre-wrap">
          <template v-if="articleContent">
            <span
              v-for="(segment, index) in articleTextSegments"
              :key="index"
              :class="segment.highlight ? `cursor-help rounded px-1 py-0.5 ${highlightClass(segment.type)}` : ''"
              @mouseenter="segment.highlight && showTooltip(segment, $event)"
              @mouseleave="segment.highlight && scheduleHideTooltip()"
            >{{ segment.text }}</span>
          </template>
          <template v-else>暂无文章内容。</template>
        </div>

        <div v-if="article.key_points?.length" class="mt-6 rounded-[1.5rem] border-2 border-violet-100 bg-violet-50 p-5">
          <p class="text-sm font-black uppercase tracking-[0.2em] text-violet-500">重点词</p>
          <div class="mt-4 flex flex-wrap gap-3">
            <span v-for="keyPoint in article.key_points" :key="keyPoint.id" class="rounded-2xl bg-white px-4 py-3 text-sm font-black text-violet-700 shadow-sm">
              {{ keyPoint.text }}<span v-if="keyPoint.abbreviation" class="ml-2 text-violet-400">{{ keyPoint.abbreviation }}</span>
            </span>
          </div>
        </div>
      </article>

        <section class="min-w-0 rounded-[2rem] border-4 border-white bg-white/80 p-5 shadow-xl shadow-sky-100/70 backdrop-blur sm:p-7">
        <div class="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p class="text-sm font-black uppercase tracking-[0.25em] text-emerald-500">Exercises</p>
            <h2 class="mt-1 text-2xl font-black text-slate-900">练习题</h2>
          </div>
          <div v-if="result" class="rounded-2xl bg-emerald-50 px-4 py-3 text-sm font-black text-emerald-700">答对 {{ result.correct }} / {{ result.total }} 题</div>
        </div>

        <div v-if="questions.length === 0" class="mt-6 rounded-[1.5rem] bg-white px-5 py-12 text-center text-sm font-bold text-slate-400">暂无练习题。</div>

        <div v-else class="mt-6 space-y-5">
          <div v-for="(question, index) in questions" :key="question.id" class="rounded-[1.5rem] border-2 border-slate-100 bg-white p-5">
            <div class="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
              <h3 class="text-lg font-black leading-7 text-slate-900">{{ index + 1 }}. {{ question.question }}</h3>
              <span v-if="question.difficulty" class="shrink-0 rounded-xl bg-amber-50 px-3 py-2 text-xs font-black text-amber-700">{{ question.difficulty }}</span>
            </div>

            <div class="mt-4 grid gap-3 sm:grid-cols-2">
              <button
                v-for="[optionKey, optionText] in getOptionEntries(question)"
                :key="optionKey"
                class="rounded-2xl border-2 px-4 py-3 text-left transition disabled:cursor-default"
                :class="[
                  selectedAnswers[question.id] === optionKey ? 'border-sky-300 bg-sky-50 text-sky-800' : 'border-slate-100 bg-slate-50 text-slate-700 hover:border-sky-200 hover:bg-sky-50',
                  resultItemsByQuestionId[question.id]?.correct_answer === optionKey ? 'result border-emerald-300 bg-emerald-50 text-emerald-800' : '',
                  resultItemsByQuestionId[question.id] && resultItemsByQuestionId[question.id]?.submitted_answer === optionKey && !resultItemsByQuestionId[question.id]?.is_correct ? 'border-rose-300 bg-rose-50 text-rose-800' : '',
                ]"
                :disabled="!!result"
                type="button"
                @click="selectAnswer(question.id, optionKey)"
              >
                <span class="font-black">{{ optionKey }}.</span>
                <span class="ml-2 font-semibold">{{ optionText }}</span>
              </button>
            </div>

            <div v-if="resultItemsByQuestionId[question.id]" class="mt-4 rounded-2xl px-4 py-3 text-sm font-bold" :class="resultItemsByQuestionId[question.id].is_correct ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'">
              <p>{{ resultItemsByQuestionId[question.id].is_correct ? '回答正确' : `回答错误，正确答案是 ${resultItemsByQuestionId[question.id].correct_answer}` }}</p>
              <p v-if="resultItemsByQuestionId[question.id].explanation" class="mt-2 leading-6 text-slate-600">{{ resultItemsByQuestionId[question.id].explanation }}</p>
            </div>
          </div>

          <button
            class="w-full rounded-2xl bg-slate-900 px-5 py-4 text-base font-black text-white shadow-lg shadow-slate-300 transition hover:-translate-y-0.5 hover:bg-sky-600 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:shadow-none"
            :disabled="submitting || !!result"
            type="button"
            @click="submitAnswers"
          >
            {{ result ? '已提交' : submitting ? '提交中...' : '提交答案' }}
          </button>
        </div>
      </section>
      </div>

      <div
        v-if="hoveredKeyPoint"
        class="fixed z-50 max-w-xs rounded-2xl border-2 border-white bg-slate-900 px-4 py-3 text-white shadow-2xl shadow-slate-500/40"
        :style="{ left: `${tooltipPosition.x}px`, top: `${tooltipPosition.y + 8}px` }"
        @mouseenter="clearTooltipTimer"
        @mouseleave="scheduleHideTooltip"
      >
        <p class="text-xs font-black uppercase tracking-[0.2em] text-violet-200">注释</p>
        <p class="mt-2 whitespace-pre-wrap text-sm font-semibold leading-6">{{ hoveredKeyPoint.abbreviation }}</p>
      </div>
    </template>
  </section>
</template>
