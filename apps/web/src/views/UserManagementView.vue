<script setup lang="ts">
import { onMounted, ref } from 'vue'
import UserFormModal from '../components/UserFormModal.vue'
import {
  createUserUsersPost,
  deleteUserUsersUserIdDelete,
  listUsersUsersGet,
  resetUserPasswordUsersUserIdResetPasswordPost,
  updateUserUsersUserIdPut,
} from '../api/client/sdk.gen'
import type { UserPublic } from '../api/client/types.gen'
import { getApiErrorMessage } from '../services/api'
import { notify } from '../services/notify'

const users = ref<UserPublic[]>([])
const loading = ref(false)
const saving = ref(false)
const modalOpen = ref(false)
const editingUser = ref<UserPublic | null>(null)

function userTypeLabel(userType: number) {
  return userType === 3 ? '管理员' : userType === 2 ? '老师' : '学生'
}

function formatDate(value: string) {
  return new Date(value).toLocaleString('zh-CN')
}

async function loadUsers() {
  loading.value = true
  const result = await listUsersUsersGet()
  loading.value = false

  if (result.data) {
    users.value = result.data
    return
  }

  notify.error(getApiErrorMessage(result.error, '加载用户列表失败。'))
}

function openCreateModal() {
  editingUser.value = null
  modalOpen.value = true
}

function openEditModal(user: UserPublic) {
  if (user.username === 'admin') {
    notify.info('内置管理员不能编辑。')
    return
  }

  editingUser.value = user
  modalOpen.value = true
}

async function saveUser(payload: { username: string; user_type: number; password?: string }) {
  saving.value = true
  const result = editingUser.value
    ? await updateUserUsersUserIdPut({
        path: { user_id: editingUser.value.id },
        body: {
          username: payload.username,
          user_type: payload.user_type,
        },
      })
    : await createUserUsersPost({
        body: {
          username: payload.username,
          password: payload.password ?? '',
          user_type: payload.user_type,
        },
      })
  saving.value = false

  if (result.data) {
    notify.success(editingUser.value ? '用户已更新。' : '用户已创建。')
    modalOpen.value = false
    await loadUsers()
    return
  }

  notify.error(getApiErrorMessage(result.error, '保存用户失败。'))
}

async function deleteUser(user: UserPublic) {
  if (user.username === 'admin') {
    notify.warning('内置管理员不能删除。')
    return
  }

  const confirmed = await notify.confirm({
    title: '确认删除用户',
    message: `确定要删除用户“${user.username}”吗？此操作不可恢复。`,
    confirmText: '删除',
    variant: 'danger',
  })

  if (!confirmed) {
    return
  }

  const result = await deleteUserUsersUserIdDelete({ path: { user_id: user.id } })
  if (result.error) {
    notify.error(getApiErrorMessage(result.error, '删除用户失败。'))
    return
  }

  notify.success('用户已删除。')
  await loadUsers()
}

async function resetPassword(user: UserPublic) {
  if (user.username === 'admin') {
    notify.warning('内置管理员不能重置密码。')
    return
  }

  const confirmed = await notify.confirm({
    title: '确认重置密码',
    message: `确定要将用户“${user.username}”的密码重置为系统默认密码吗？`,
    confirmText: '重置密码',
    variant: 'danger',
  })

  if (!confirmed) {
    return
  }

  const result = await resetUserPasswordUsersUserIdResetPasswordPost({ path: { user_id: user.id } })
  if (result.data) {
    notify.success(result.data.message)
    return
  }

  notify.error(getApiErrorMessage(result.error, '重置密码失败。'))
}

onMounted(loadUsers)
</script>

<template>
  <section class="rounded-[2rem] border-4 border-white bg-white/80 p-5 shadow-xl shadow-sky-100/70 backdrop-blur sm:p-6">
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <p class="text-sm font-black uppercase tracking-[0.25em] text-sky-500">Users</p>
        <h2 class="mt-1 text-3xl font-black text-slate-900">用户管理</h2>
      </div>
      <button
        class="rounded-2xl bg-sky-600 px-5 py-3 text-sm font-black text-white shadow-lg shadow-sky-200 transition hover:-translate-y-0.5 hover:bg-sky-700"
        type="button"
        @click="openCreateModal"
      >
        新增用户
      </button>
    </div>

    <div class="mt-6 overflow-hidden rounded-[1.5rem] border-2 border-slate-100 bg-white">
      <div v-if="loading" class="px-5 py-10 text-center text-sm font-bold text-slate-500">正在加载用户...</div>
      <table v-else class="w-full min-w-[760px] text-left text-sm">
        <thead class="bg-slate-50 text-xs font-black uppercase tracking-wider text-slate-500">
          <tr>
            <th class="px-5 py-4">ID</th>
            <th class="px-5 py-4">用户名</th>
            <th class="px-5 py-4">用户类型</th>
            <th class="px-5 py-4">创建时间</th>
            <th class="px-5 py-4 text-right">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-for="user in users" :key="user.id" class="font-semibold text-slate-700">
            <td class="max-w-[12rem] truncate px-5 py-4 text-xs text-slate-400">{{ user.id }}</td>
            <td class="px-5 py-4">{{ user.username }}</td>
            <td class="px-5 py-4">{{ user.user_type_description || userTypeLabel(user.user_type) }}</td>
            <td class="px-5 py-4">{{ formatDate(user.created_at) }}</td>
            <td class="px-5 py-4">
              <div class="flex justify-end gap-2">
                <button class="rounded-xl bg-sky-50 px-3 py-2 font-black text-sky-700 transition hover:bg-sky-100 disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-400" :disabled="user.username === 'admin'" type="button" @click="openEditModal(user)">
                  编辑
                </button>
                <button class="rounded-xl bg-amber-50 px-3 py-2 font-black text-amber-700 transition hover:bg-amber-100 disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-400" :disabled="user.username === 'admin'" type="button" @click="resetPassword(user)">
                  重置密码
                </button>
                <button class="rounded-xl bg-rose-50 px-3 py-2 font-black text-rose-700 transition hover:bg-rose-100 disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-400" :disabled="user.username === 'admin'" type="button" @click="deleteUser(user)">
                  删除
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="users.length === 0">
            <td class="px-5 py-10 text-center text-sm font-bold text-slate-400" colspan="5">暂无用户。</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <UserFormModal :open="modalOpen" :saving="saving" :user="editingUser" @close="modalOpen = false" @save="saveUser" />
</template>
