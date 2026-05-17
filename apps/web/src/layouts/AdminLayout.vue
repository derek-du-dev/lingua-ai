<script setup lang="ts">
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { authState, logout } from '../services/auth'
import { notify } from '../services/notify'

const router = useRouter()

async function handleLogout() {
  logout()
  notify.success('已退出登录')
  await router.push('/login')
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-sky-100 via-amber-50 to-pink-100 text-slate-800">
    <header class="border-b-2 border-white/80 bg-white/75 shadow-lg shadow-sky-100/60 backdrop-blur">
      <div class="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 sm:px-8">
        <div>
          <p class="text-sm font-black uppercase tracking-[0.25em] text-sky-500">Lingua AI</p>
          <h1 class="text-2xl font-black text-slate-900">管理后台</h1>
        </div>
        <div class="flex items-center gap-4">
          <span class="hidden rounded-full bg-sky-50 px-4 py-2 text-sm font-bold text-sky-700 sm:inline-flex">
            {{ authState.user?.username }}
          </span>
          <button
            class="rounded-2xl bg-slate-900 px-5 py-3 text-sm font-black text-white shadow-lg shadow-slate-300 transition hover:-translate-y-0.5 hover:bg-sky-600"
            type="button"
            @click="handleLogout"
          >
            退出登录
          </button>
        </div>
      </div>
    </header>

    <div class="mx-auto grid max-w-7xl gap-6 px-5 py-6 sm:px-8 lg:grid-cols-[14rem_1fr]">
      <aside class="rounded-[2rem] border-4 border-white bg-white/80 p-4 shadow-xl shadow-sky-100/70 backdrop-blur">
        <nav class="space-y-3">
          <RouterLink
            class="block rounded-2xl px-4 py-3 text-sm font-black text-slate-600 transition hover:bg-sky-50 hover:text-sky-700"
            active-class="bg-sky-600 text-white shadow-lg shadow-sky-200 hover:bg-sky-600 hover:text-white"
            to="/admin/users"
          >
            用户管理
          </RouterLink>
          <RouterLink
            class="block rounded-2xl px-4 py-3 text-sm font-black text-slate-600 transition hover:bg-sky-50 hover:text-sky-700"
            active-class="bg-sky-600 text-white shadow-lg shadow-sky-200 hover:bg-sky-600 hover:text-white"
            to="/admin/textbooks"
          >
            教材管理
          </RouterLink>
        </nav>
      </aside>

      <main>
        <RouterView />
      </main>
    </div>
  </div>
</template>
