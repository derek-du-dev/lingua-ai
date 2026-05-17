<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  listLearningTextbookArticlesLearningTextbooksTextbookIdArticlesGet,
  listLearningTextbooksLearningTextbooksGet,
} from '../api/client/sdk.gen'
import type { LearningArticleSummaryPublic, LearningTextbookPublic } from '../api/client/types.gen'
import { authState } from '../services/auth'
import { getApiErrorMessage } from '../services/api'
import { notify } from '../services/notify'

const router = useRouter()
const textbooks = ref<LearningTextbookPublic[]>([])
const articles = ref<LearningArticleSummaryPublic[]>([])
const selectedTextbookId = ref('')
const loadingTextbooks = ref(false)
const loadingArticles = ref(false)

const selectedTextbook = computed(() => textbooks.value.find((textbook) => textbook.id === selectedTextbookId.value) ?? null)

async function loadTextbooks() {
  loadingTextbooks.value = true
  const result = await listLearningTextbooksLearningTextbooksGet()
  loadingTextbooks.value = false

  if (result.data) {
    textbooks.value = result.data
    if (!selectedTextbookId.value || !textbooks.value.some((textbook) => textbook.id === selectedTextbookId.value)) {
      selectedTextbookId.value = textbooks.value[0]?.id ?? ''
    }
    await loadArticles()
    return
  }

  notify.error(getApiErrorMessage(result.error, '加载教材列表失败。'))
}

async function loadArticles() {
  articles.value = []
  if (!selectedTextbookId.value) {
    return
  }

  loadingArticles.value = true
  const result = await listLearningTextbookArticlesLearningTextbooksTextbookIdArticlesGet({
    path: { textbook_id: selectedTextbookId.value },
  })
  loadingArticles.value = false

  if (result.data) {
    articles.value = result.data
    return
  }

  notify.error(getApiErrorMessage(result.error, '加载文章列表失败。'))
}

async function selectTextbook(textbook: LearningTextbookPublic) {
  if (selectedTextbookId.value === textbook.id) {
    return
  }

  selectedTextbookId.value = textbook.id
  await loadArticles()
}

function openArticle(article: LearningArticleSummaryPublic) {
  router.push(`/learn/articles/${article.id}`)
}

onMounted(loadTextbooks)
</script>

<template>
  <section class="grid min-h-[calc(100vh-8.5rem)] gap-6 lg:grid-cols-[22rem_minmax(0,1fr)]">
    <aside class="rounded-[2rem] border-4 border-white bg-white/80 p-5 shadow-xl shadow-sky-100/70 backdrop-blur sm:p-6">
      <div>
        <p class="text-sm font-black uppercase tracking-[0.25em] text-sky-500">Learning</p>
        <h2 class="mt-1 text-2xl font-black text-slate-900">学习空间</h2>
        <p class="mt-3 text-sm font-semibold leading-6 text-slate-500">欢迎回来，{{ authState.user?.username }}。请选择教材开始学习。</p>
      </div>

      <div class="mt-6 space-y-3">
        <div v-if="loadingTextbooks" class="rounded-2xl bg-white px-5 py-10 text-center text-sm font-bold text-slate-500">正在加载教材...</div>
        <template v-else>
          <button
            v-for="textbook in textbooks"
            :key="textbook.id"
            class="w-full rounded-2xl border-2 px-4 py-3 text-left transition"
            :class="selectedTextbookId === textbook.id ? 'border-sky-200 bg-sky-50 shadow-lg shadow-sky-100' : 'border-slate-100 bg-white hover:border-sky-100 hover:bg-sky-50/50'"
            type="button"
            @click="selectTextbook(textbook)"
          >
            <span class="block truncate text-base font-black text-slate-800">{{ textbook.name }}</span>
            <span class="mt-2 block text-xs font-black text-sky-600">{{ textbook.article_count ?? 0 }} 篇文章</span>
          </button>
        </template>
        <div v-if="!loadingTextbooks && textbooks.length === 0" class="rounded-2xl bg-white px-5 py-10 text-center text-sm font-bold text-slate-400">暂无教材。</div>
      </div>
    </aside>

    <main class="min-w-0 rounded-[2rem] border-4 border-white bg-white/80 p-5 shadow-xl shadow-sky-100/70 backdrop-blur sm:p-6">
      <div class="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p class="text-sm font-black uppercase tracking-[0.25em] text-amber-500">Articles</p>
          <h2 class="mt-1 text-2xl font-black text-slate-900">{{ selectedTextbook?.name ?? '请选择教材' }}</h2>
        </div>
        <p v-if="selectedTextbook" class="text-sm font-bold text-slate-500">选择文章进入学习页面</p>
      </div>

      <div class="mt-6 overflow-hidden rounded-[1.5rem] border-2 border-slate-100 bg-white">
        <div v-if="!selectedTextbook" class="px-5 py-16 text-center text-sm font-bold text-slate-400">请先选择教材。</div>
        <div v-else-if="loadingArticles" class="px-5 py-16 text-center text-sm font-bold text-slate-500">正在加载文章...</div>
        <div v-else class="divide-y divide-slate-100">
          <button
            v-for="article in articles"
            :key="article.id"
            class="flex w-full items-center justify-between gap-4 px-5 py-5 text-left transition hover:bg-sky-50/70"
            type="button"
            @click="openArticle(article)"
          >
            <span class="min-w-0">
              <span class="block truncate text-lg font-black text-slate-800">{{ article.title }}</span>
              <span class="mt-2 block text-sm font-bold text-slate-500">{{ article.question_count ?? 0 }} 道练习题</span>
            </span>
            <span class="shrink-0 rounded-2xl bg-sky-600 px-4 py-2 text-sm font-black text-white shadow-lg shadow-sky-100">开始学习</span>
          </button>
          <div v-if="articles.length === 0" class="px-5 py-16 text-center text-sm font-bold text-slate-400">该教材暂无文章。</div>
        </div>
      </div>
    </main>
  </section>
</template>
