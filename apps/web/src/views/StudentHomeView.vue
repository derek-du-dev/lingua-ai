<script setup lang="ts">
import { authState } from '../services/auth'
</script>

<template>
  <section class="rounded-[2rem] border-4 border-white bg-white/80 p-6 shadow-xl shadow-sky-100/70 backdrop-blur">
    <p class="text-sm font-black uppercase tracking-[0.25em] text-sky-500">Learning</p>
    <h2 class="mt-1 text-3xl font-black text-slate-900">学习空间</h2>
    <p class="mt-4 max-w-2xl text-base font-semibold leading-7 text-slate-600">
      欢迎回来，{{ authState.user?.username }}。学生端学习内容正在接入中，登录入口已经支持学生、老师和管理员统一进入。
    </p>
  </section>
</template>
