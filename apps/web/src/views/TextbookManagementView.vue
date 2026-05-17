<script setup lang="ts">
import { onMounted, ref } from 'vue'
import TextbookFormModal from '../components/TextbookFormModal.vue'
import {
  createTextbookTextbooksPost,
  deleteTextbookTextbooksTextbookIdDelete,
  listTextbooksTextbooksGet,
  updateTextbookTextbooksTextbookIdPut,
} from '../api/client/sdk.gen'
import type { TextbookPublic } from '../api/client/types.gen'
import { getApiErrorMessage } from '../services/api'
import { notify } from '../services/notify'

const textbooks = ref<TextbookPublic[]>([])
const loading = ref(false)
const saving = ref(false)
const modalOpen = ref(false)
const editingTextbook = ref<TextbookPublic | null>(null)

async function loadTextbooks() {
  loading.value = true
  const result = await listTextbooksTextbooksGet()
  loading.value = false

  if (result.data) {
    textbooks.value = result.data
    return
  }

  notify.error(getApiErrorMessage(result.error, '加载教材列表失败。'))
}

function openCreateModal() {
  editingTextbook.value = null
  modalOpen.value = true
}

function openEditModal(textbook: TextbookPublic) {
  editingTextbook.value = textbook
  modalOpen.value = true
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
    await loadTextbooks()
    return
  }

  notify.error(getApiErrorMessage(result.error, '保存教材失败。'))
}

async function deleteTextbook(textbook: TextbookPublic) {
  const confirmed = await notify.confirm({
    title: '确认删除教材',
    message: `确定要删除教材“${textbook.name}”吗？此操作不可恢复。`,
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
  await loadTextbooks()
}

onMounted(loadTextbooks)
</script>

<template>
  <section class="rounded-[2rem] border-4 border-white bg-white/80 p-5 shadow-xl shadow-sky-100/70 backdrop-blur sm:p-6">
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <p class="text-sm font-black uppercase tracking-[0.25em] text-sky-500">Textbooks</p>
        <h2 class="mt-1 text-3xl font-black text-slate-900">教材管理</h2>
      </div>
      <button
        class="rounded-2xl bg-sky-600 px-5 py-3 text-sm font-black text-white shadow-lg shadow-sky-200 transition hover:-translate-y-0.5 hover:bg-sky-700"
        type="button"
        @click="openCreateModal"
      >
        新增教材
      </button>
    </div>

    <div class="mt-6 overflow-hidden rounded-[1.5rem] border-2 border-slate-100 bg-white">
      <div v-if="loading" class="px-5 py-10 text-center text-sm font-bold text-slate-500">正在加载教材...</div>
      <table v-else class="w-full min-w-[640px] text-left text-sm">
        <thead class="bg-slate-50 text-xs font-black uppercase tracking-wider text-slate-500">
          <tr>
            <th class="px-5 py-4">ID</th>
            <th class="px-5 py-4">教材名称</th>
            <th class="px-5 py-4 text-right">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-for="textbook in textbooks" :key="textbook.id" class="font-semibold text-slate-700">
            <td class="max-w-[14rem] truncate px-5 py-4 text-xs text-slate-400">{{ textbook.id }}</td>
            <td class="px-5 py-4">{{ textbook.name }}</td>
            <td class="px-5 py-4">
              <div class="flex justify-end gap-2">
                <button class="rounded-xl bg-sky-50 px-3 py-2 font-black text-sky-700 transition hover:bg-sky-100" type="button" @click="openEditModal(textbook)">
                  编辑
                </button>
                <button class="rounded-xl bg-rose-50 px-3 py-2 font-black text-rose-700 transition hover:bg-rose-100" type="button" @click="deleteTextbook(textbook)">
                  删除
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="textbooks.length === 0">
            <td class="px-5 py-10 text-center text-sm font-bold text-slate-400" colspan="3">暂无教材。</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <TextbookFormModal :open="modalOpen" :saving="saving" :textbook="editingTextbook" @close="modalOpen = false" @save="saveTextbook" />
</template>
