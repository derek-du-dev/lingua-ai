<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import ArticleFormModal from '../components/ArticleFormModal.vue'
import TextbookFormModal from '../components/TextbookFormModal.vue'
import {
  createTextbookArticleTextbooksTextbookIdArticlesPost,
  createTextbookTextbooksPost,
  deleteArticleArticlesArticleIdDelete,
  deleteTextbookTextbooksTextbookIdDelete,
  listTextbookArticlesTextbooksTextbookIdArticlesGet,
  listTextbooksTextbooksGet,
  updateArticleArticlesArticleIdPut,
  updateTextbookTextbooksTextbookIdPut,
} from '../api/client/sdk.gen'
import type { ArticlePublic, TextbookPublic } from '../api/client/types.gen'
import { getApiErrorMessage } from '../services/api'
import { notify } from '../services/notify'

type ArticlePayload = {
  title: string
  content: string
  keywords: string[]
  audio_url: string
  sentences: Array<{ content: string; audio_url: string }>
}

const textbooks = ref<TextbookPublic[]>([])
const articles = ref<ArticlePublic[]>([])
const selectedTextbookId = ref('')
const loading = ref(false)
const articlesLoading = ref(false)
const saving = ref(false)
const articleSaving = ref(false)
const modalOpen = ref(false)
const articleModalOpen = ref(false)
const editingTextbook = ref<TextbookPublic | null>(null)
const editingArticle = ref<ArticlePublic | null>(null)

const selectedTextbook = computed(() => textbooks.value.find((textbook) => textbook.id === selectedTextbookId.value) ?? null)

async function loadTextbooks() {
  loading.value = true
  const result = await listTextbooksTextbooksGet()
  loading.value = false

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

  articlesLoading.value = true
  const result = await listTextbookArticlesTextbooksTextbookIdArticlesGet({
    path: { textbook_id: selectedTextbookId.value },
  })
  articlesLoading.value = false

  if (result.data) {
    articles.value = result.data
    return
  }

  notify.error(getApiErrorMessage(result.error, '加载文章列表失败。'))
}

async function selectTextbook(textbook: TextbookPublic) {
  if (selectedTextbookId.value === textbook.id) {
    return
  }

  selectedTextbookId.value = textbook.id
  await loadArticles()
}

function openCreateModal() {
  editingTextbook.value = null
  modalOpen.value = true
}

function openEditModal(textbook: TextbookPublic) {
  editingTextbook.value = textbook
  modalOpen.value = true
}

function openCreateArticleModal() {
  if (!selectedTextbook.value) {
    return
  }

  editingArticle.value = null
  articleModalOpen.value = true
}

function openEditArticleModal(article: ArticlePublic) {
  editingArticle.value = article
  articleModalOpen.value = true
}

async function saveTextbook(payload: { name: string }) {
  saving.value = true
  const result = editingTextbook.value
    ? await updateTextbookTextbooksTextbookIdPut({
        path: { textbook_id: editingTextbook.value.id },
        body: payload,
      })
    : await createTextbookTextbooksPost({ body: payload })
  saving.value = false

  if (result.data) {
    notify.success(editingTextbook.value ? '教材已更新。' : '教材已创建。')
    modalOpen.value = false
    selectedTextbookId.value = result.data.id
    await loadTextbooks()
    return
  }

  notify.error(getApiErrorMessage(result.error, '保存教材失败。'))
}

async function saveArticle(payload: ArticlePayload) {
  if (!selectedTextbook.value) {
    return
  }

  articleSaving.value = true
  const result = editingArticle.value
    ? await updateArticleArticlesArticleIdPut({
        path: { article_id: editingArticle.value.id },
        body: payload,
      })
    : await createTextbookArticleTextbooksTextbookIdArticlesPost({
        path: { textbook_id: selectedTextbook.value.id },
        body: payload,
      })
  articleSaving.value = false

  if (result.data) {
    notify.success(editingArticle.value ? '文章已更新。' : '文章已创建。')
    articleModalOpen.value = false
    await loadArticles()
    return
  }

  notify.error(getApiErrorMessage(result.error, '保存文章失败。'))
}

async function deleteTextbook(textbook: TextbookPublic) {
  const confirmed = await notify.confirm({
    title: '确认删除教材',
    message: `确定要删除教材“${textbook.name}”吗？此操作会同时删除教材下的文章，且不可恢复。`,
    confirmText: '删除',
    variant: 'danger',
  })

  if (!confirmed) {
    return
  }

  const result = await deleteTextbookTextbooksTextbookIdDelete({ path: { textbook_id: textbook.id } })
  if (result.error) {
    notify.error(getApiErrorMessage(result.error, '删除教材失败。'))
    return
  }

  notify.success('教材已删除。')
  selectedTextbookId.value = ''
  await loadTextbooks()
}

async function deleteArticle(article: ArticlePublic) {
  const confirmed = await notify.confirm({
    title: '确认删除文章',
    message: `确定要删除文章“${article.title}”吗？此操作不可恢复。`,
    confirmText: '删除',
    variant: 'danger',
  })

  if (!confirmed) {
    return
  }

  const result = await deleteArticleArticlesArticleIdDelete({ path: { article_id: article.id } })
  if (result.error) {
    notify.error(getApiErrorMessage(result.error, '删除文章失败。'))
    return
  }

  notify.success('文章已删除。')
  await loadArticles()
}

onMounted(loadTextbooks)
</script>

<template>
  <section class="grid min-h-[calc(100vh-8.5rem)] gap-6 lg:grid-cols-[22rem_minmax(0,1fr)]">
    <aside class="rounded-[2rem] border-4 border-white bg-white/80 p-5 shadow-xl shadow-sky-100/70 backdrop-blur sm:p-6">
      <div class="flex items-center justify-between gap-4">
        <div>
          <p class="text-sm font-black uppercase tracking-[0.25em] text-sky-500">Textbooks</p>
          <h2 class="mt-1 text-2xl font-black text-slate-900">教材管理</h2>
        </div>
        <button
          class="rounded-2xl bg-sky-600 px-4 py-3 text-sm font-black text-white shadow-lg shadow-sky-200 transition hover:-translate-y-0.5 hover:bg-sky-700"
          type="button"
          @click="openCreateModal"
        >
          新增
        </button>
      </div>

      <div class="mt-6 space-y-3">
        <div v-if="loading" class="rounded-2xl bg-white px-5 py-10 text-center text-sm font-bold text-slate-500">正在加载教材...</div>
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
            <span class="mt-3 flex gap-2">
              <span class="rounded-xl bg-sky-100 px-3 py-1.5 text-xs font-black text-sky-700" @click.stop="openEditModal(textbook)">编辑</span>
              <span class="rounded-xl bg-rose-50 px-3 py-1.5 text-xs font-black text-rose-700" @click.stop="deleteTextbook(textbook)">删除</span>
            </span>
          </button>
        </template>
        <div v-if="!loading && textbooks.length === 0" class="rounded-2xl bg-white px-5 py-10 text-center text-sm font-bold text-slate-400">暂无教材。</div>
      </div>
    </aside>

    <main class="min-w-0 rounded-[2rem] border-4 border-white bg-white/80 p-5 shadow-xl shadow-sky-100/70 backdrop-blur sm:p-6">
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p class="text-sm font-black uppercase tracking-[0.25em] text-amber-500">Articles</p>
          <h2 class="mt-1 text-2xl font-black text-slate-900">{{ selectedTextbook?.name ?? '请选择教材' }}</h2>
        </div>
        <button
          class="rounded-2xl bg-slate-900 px-5 py-3 text-sm font-black text-white shadow-lg shadow-slate-300 transition hover:-translate-y-0.5 hover:bg-sky-600 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:shadow-none"
          :disabled="!selectedTextbook"
          type="button"
          @click="openCreateArticleModal"
        >
          新增文章
        </button>
      </div>

      <div class="mt-6 overflow-hidden rounded-[1.5rem] border-2 border-slate-100 bg-white">
        <div v-if="!selectedTextbook" class="px-5 py-16 text-center text-sm font-bold text-slate-400">请先在左侧选择教材。</div>
        <div v-else-if="articlesLoading" class="px-5 py-16 text-center text-sm font-bold text-slate-500">正在加载文章...</div>
        <table v-else class="w-full min-w-[520px] text-left text-sm">
          <thead class="bg-slate-50 text-xs font-black uppercase tracking-wider text-slate-500">
            <tr>
              <th class="px-5 py-4">文章标题</th>
              <th class="px-5 py-4 text-right">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="article in articles" :key="article.id" class="font-semibold text-slate-700">
              <td class="px-5 py-4">
                <span class="block truncate text-base font-black text-slate-800">{{ article.title }}</span>
              </td>
              <td class="px-5 py-4">
                <div class="flex justify-end gap-2">
                  <button class="rounded-xl bg-sky-50 px-3 py-2 font-black text-sky-700 transition hover:bg-sky-100" type="button" @click="openEditArticleModal(article)">
                    编辑
                  </button>
                  <button class="rounded-xl bg-rose-50 px-3 py-2 font-black text-rose-700 transition hover:bg-rose-100" type="button" @click="deleteArticle(article)">
                    删除
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="articles.length === 0">
              <td class="px-5 py-16 text-center text-sm font-bold text-slate-400" colspan="2">该教材暂无文章。</td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>
  </section>

  <TextbookFormModal :open="modalOpen" :saving="saving" :textbook="editingTextbook" @close="modalOpen = false" @save="saveTextbook" />
  <ArticleFormModal :article="editingArticle" :open="articleModalOpen" :saving="articleSaving" @close="articleModalOpen = false" @save="saveArticle" />
</template>
