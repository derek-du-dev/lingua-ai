<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { login, logout } from '../services/auth'
import { notify } from '../services/notify'

const router = useRouter()
const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const canSubmit = computed(() => username.value.trim().length > 0 && password.value.length > 0 && !loading.value)

async function handleLogin() {
  if (!canSubmit.value) {
    error.value = '请先填写账号和密码。'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const user = await login(username.value.trim(), password.value)
    password.value = ''

    if (user.user_type !== 3) {
      logout()
      error.value = '当前账号无管理权限。'
      notify.warning(error.value)
      return
    }

    notify.success(`欢迎回来，${user.username}`)
    await router.push('/admin/users')
  } catch (err) {
    error.value = err instanceof Error ? err.message : '登录遇到了一点小问题，请稍后再试。'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="relative min-h-screen overflow-hidden bg-gradient-to-br from-sky-100 via-amber-50 to-pink-100 px-5 py-8 text-slate-800 sm:px-8 lg:px-12">
    <div class="pointer-events-none absolute -left-16 top-14 h-44 w-44 rounded-full bg-yellow-300/45 blur-2xl" />
    <div class="pointer-events-none absolute right-[-4rem] top-28 h-56 w-56 rounded-full bg-cyan-300/40 blur-3xl" />
    <div class="pointer-events-none absolute bottom-[-5rem] left-1/3 h-64 w-64 rounded-full bg-pink-300/40 blur-3xl" />

    <section class="relative mx-auto flex min-h-[calc(100vh-4rem)] w-full max-w-6xl items-center justify-center">
      <div class="grid w-full items-center gap-8 lg:grid-cols-[1.05fr_0.95fr]">
        <div class="order-2 text-center lg:order-1 lg:text-left">
          <div class="mb-6 inline-flex items-center gap-3 rounded-full border-2 border-white/80 bg-white/70 px-4 py-2 text-sm font-bold text-sky-700 shadow-lg shadow-sky-200/60 backdrop-blur">
            <span class="h-3 w-3 rounded-full bg-emerald-400 shadow-[0_0_0_6px_rgba(52,211,153,0.18)]" />
            Lingua AI 管理后台
          </div>

          <h1 class="text-4xl font-black leading-tight tracking-tight text-slate-900 sm:text-5xl lg:text-6xl">
            管理你的
            <span class="relative inline-block text-sky-600">
              语言课堂
              <span class="absolute -bottom-1 left-0 h-3 w-full rounded-full bg-yellow-300/70 -z-10" />
            </span>
          </h1>

          <p class="mx-auto mt-5 max-w-xl text-lg leading-8 text-slate-600 lg:mx-0">
            登录后管理用户账号、教材内容和课堂基础数据，让学习体验保持清晰有序。
          </p>

          <div class="mt-8 grid gap-4 sm:grid-cols-3">
            <div class="rounded-3xl border-2 border-white bg-white/70 p-4 shadow-lg shadow-sky-200/50">
              <div class="mx-auto mb-3 h-12 w-12 rounded-2xl bg-sky-200 p-2 lg:mx-0">
                <div class="h-full w-full rounded-xl bg-sky-500" />
              </div>
              <p class="text-sm font-bold text-slate-900">用户管理</p>
              <p class="mt-1 text-xs text-slate-500">维护账号权限</p>
            </div>
            <div class="rounded-3xl border-2 border-white bg-white/70 p-4 shadow-lg shadow-amber-200/50">
              <div class="mx-auto mb-3 h-12 w-12 rounded-2xl bg-amber-200 p-2 lg:mx-0">
                <div class="h-full w-full rounded-xl bg-amber-500" />
              </div>
              <p class="text-sm font-bold text-slate-900">教材管理</p>
              <p class="mt-1 text-xs text-slate-500">整理教材目录</p>
            </div>
            <div class="rounded-3xl border-2 border-white bg-white/70 p-4 shadow-lg shadow-pink-200/50">
              <div class="mx-auto mb-3 h-12 w-12 rounded-2xl bg-pink-200 p-2 lg:mx-0">
                <div class="h-full w-full rounded-xl bg-pink-500" />
              </div>
              <p class="text-sm font-bold text-slate-900">安全权限</p>
              <p class="mt-1 text-xs text-slate-500">仅管理员可进入</p>
            </div>
          </div>
        </div>

        <div class="order-1 lg:order-2">
          <div class="relative mx-auto max-w-md">
            <div class="absolute -left-6 top-10 h-16 w-16 rotate-[-12deg] rounded-3xl bg-yellow-300 shadow-xl shadow-yellow-200" />
            <div class="absolute -right-5 top-28 h-14 w-14 rotate-12 rounded-full bg-sky-300 shadow-xl shadow-sky-200" />
            <div class="absolute -bottom-5 left-12 h-12 w-12 rotate-45 rounded-2xl bg-pink-300 shadow-xl shadow-pink-200" />

            <div class="relative rounded-[2.5rem] border-4 border-white bg-white/90 p-6 shadow-2xl shadow-sky-200/70 backdrop-blur sm:p-8">
              <div class="text-center">
                <p class="text-sm font-black uppercase tracking-[0.3em] text-sky-500">Welcome Back</p>
                <h2 class="mt-2 text-3xl font-black text-slate-900">管理员登录</h2>
                <p class="mt-2 text-sm leading-6 text-slate-500">输入管理员账号，进入 Lingua AI 管理后台。</p>
              </div>

              <form class="mt-7 space-y-5" @submit.prevent="handleLogin">
                <label class="block text-left">
                  <span class="mb-2 block text-sm font-bold text-slate-700">账号</span>
                  <input
                    v-model="username"
                    autocomplete="username"
                    class="w-full rounded-2xl border-2 border-sky-100 bg-sky-50/70 px-4 py-3 font-semibold text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-sky-400 focus:bg-white focus:ring-4 focus:ring-sky-100"
                    placeholder="请输入账号"
                    type="text"
                  >
                </label>

                <label class="block text-left">
                  <span class="mb-2 block text-sm font-bold text-slate-700">密码</span>
                  <input
                    v-model="password"
                    autocomplete="current-password"
                    class="w-full rounded-2xl border-2 border-amber-100 bg-amber-50/70 px-4 py-3 font-semibold text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-amber-400 focus:bg-white focus:ring-4 focus:ring-amber-100"
                    placeholder="请输入密码"
                    type="password"
                  >
                </label>

                <p v-if="error" class="rounded-2xl border-2 border-rose-100 bg-rose-50 px-4 py-3 text-left text-sm font-bold text-rose-600">
                  {{ error }}
                </p>

                <button
                  class="group w-full rounded-2xl bg-slate-900 px-5 py-4 text-base font-black text-white shadow-xl shadow-slate-300 transition hover:-translate-y-0.5 hover:bg-sky-600 hover:shadow-sky-200 focus:outline-none focus:ring-4 focus:ring-sky-200 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:shadow-none"
                  :disabled="!canSubmit"
                  type="submit"
                >
                  <span class="inline-flex items-center justify-center gap-2">
                    {{ loading ? '正在登录...' : '进入管理后台' }}
                    <span class="transition group-hover:translate-x-1">→</span>
                  </span>
                </button>
              </form>

              <div class="mt-6 rounded-3xl bg-gradient-to-r from-sky-50 to-yellow-50 px-4 py-3 text-center text-xs font-semibold leading-5 text-slate-500">
                小提示：默认演示账号可使用 admin / 123qwe。
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>
