<script setup lang="ts">
import { computed, reactive, watch } from 'vue'
import type { UserPublic } from '../api/client/types.gen'

const props = defineProps<{
  open: boolean
  user: UserPublic | null
  saving: boolean
}>()

const emit = defineEmits<{
  close: []
  save: [payload: { username: string; user_type: number; password?: string }]
}>()

const form = reactive({
  username: '',
  password: '',
  user_type: 1,
})

const isEdit = computed(() => Boolean(props.user))
const isAdminUser = computed(() => props.user?.username === 'admin')
const canSubmit = computed(() => {
  if (props.saving || isAdminUser.value) {
    return false
  }

  if (!form.username.trim()) {
    return false
  }

  return isEdit.value || form.password.length > 0
})

watch(
  () => [props.open, props.user] as const,
  () => {
    if (!props.open) {
      return
    }

    form.username = props.user?.username ?? ''
    form.password = ''
    form.user_type = props.user?.user_type ?? 1
  },
  { immediate: true },
)

function handleSubmit() {
  if (!canSubmit.value) {
    return
  }

  emit('save', {
    username: form.username.trim(),
    user_type: Number(form.user_type),
    password: isEdit.value ? undefined : form.password,
  })
}
</script>

<template>
  <div v-if="open" class="fixed inset-0 z-40 flex items-center justify-center bg-slate-900/35 px-4 backdrop-blur-sm">
    <form class="w-full max-w-lg rounded-[2rem] border-4 border-white bg-white p-6 shadow-2xl shadow-slate-400/30" @submit.prevent="handleSubmit">
      <div class="flex items-start justify-between gap-4">
        <div>
          <p class="text-sm font-black uppercase tracking-[0.25em] text-sky-500">User</p>
          <h2 class="mt-1 text-2xl font-black text-slate-900">{{ isEdit ? '编辑用户' : '新增用户' }}</h2>
        </div>
        <button class="text-2xl font-black text-slate-300 transition hover:text-slate-600" type="button" @click="emit('close')">×</button>
      </div>

      <div class="mt-6 space-y-5">
        <label class="block">
          <span class="mb-2 block text-sm font-bold text-slate-700">用户名</span>
          <input
            v-model="form.username"
            class="w-full rounded-2xl border-2 border-sky-100 bg-sky-50/70 px-4 py-3 font-semibold outline-none transition focus:border-sky-400 focus:bg-white focus:ring-4 focus:ring-sky-100 disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-400"
            :disabled="isAdminUser"
            placeholder="请输入用户名"
            type="text"
          >
        </label>

        <label class="block">
          <span class="mb-2 block text-sm font-bold text-slate-700">用户类型</span>
          <select
            v-model="form.user_type"
            class="w-full rounded-2xl border-2 border-amber-100 bg-amber-50/70 px-4 py-3 font-semibold outline-none transition focus:border-amber-400 focus:bg-white focus:ring-4 focus:ring-amber-100 disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-400"
            :disabled="isAdminUser"
          >
            <option :value="1">学生</option>
            <option :value="2">老师</option>
            <option :value="3">管理员</option>
          </select>
        </label>

        <label v-if="!isEdit" class="block">
          <span class="mb-2 block text-sm font-bold text-slate-700">初始密码</span>
          <input
            v-model="form.password"
            class="w-full rounded-2xl border-2 border-pink-100 bg-pink-50/70 px-4 py-3 font-semibold outline-none transition focus:border-pink-400 focus:bg-white focus:ring-4 focus:ring-pink-100"
            placeholder="请输入初始密码"
            type="password"
          >
        </label>

        <p v-if="isAdminUser" class="rounded-2xl border-2 border-amber-100 bg-amber-50 px-4 py-3 text-sm font-bold text-amber-700">
          内置管理员账号不能编辑、删除或重置密码。
        </p>
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
