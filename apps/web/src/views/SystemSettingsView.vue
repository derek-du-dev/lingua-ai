<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  readSystemSettingsSystemSettingsGet,
  saveSystemSettingsSystemSettingsPut,
} from '../api/client/sdk.gen'
import { getApiErrorMessage } from '../services/api'
import { notify } from '../services/notify'

const defaultPassword = ref('')
const edgeTtsRate = ref(1)
const loading = ref(false)
const saving = ref(false)

const ratePercent = computed(() => Math.round((edgeTtsRate.value - 1) * 100))
const canSave = computed(() => Boolean(defaultPassword.value.trim()) && Number.isFinite(edgeTtsRate.value) && edgeTtsRate.value >= 0 && edgeTtsRate.value <= 1)

async function loadSettings() {
  loading.value = true
  const result = await readSystemSettingsSystemSettingsGet()
  loading.value = false

  if (result.data) {
    defaultPassword.value = result.data.default_password
    edgeTtsRate.value = result.data.edge_tts_rate
    return
  }

  notify.error(getApiErrorMessage(result.error, '加载系统参数失败。'))
}

async function saveSettings() {
  if (!canSave.value) {
    notify.warning('请填写默认密码，并将音频语速设置在 0 到 1 之间。')
    return
  }

  saving.value = true
  const result = await saveSystemSettingsSystemSettingsPut({
    body: {
      default_password: defaultPassword.value,
      edge_tts_rate: edgeTtsRate.value,
    },
  })
  saving.value = false

  if (result.data) {
    defaultPassword.value = result.data.default_password
    edgeTtsRate.value = result.data.edge_tts_rate
    notify.success('系统参数已保存。')
    return
  }

  notify.error(getApiErrorMessage(result.error, '保存系统参数失败。'))
}

onMounted(loadSettings)
</script>

<template>
  <section class="rounded-[2rem] border-4 border-white bg-white/80 p-5 shadow-xl shadow-sky-100/70 backdrop-blur sm:p-6">
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <p class="text-sm font-black uppercase tracking-[0.25em] text-sky-500">Settings</p>
        <h2 class="mt-1 text-3xl font-black text-slate-900">系统参数</h2>
        <p class="mt-2 text-sm font-semibold text-slate-500">配置默认密码和 edge-tts 音频语速。</p>
      </div>
      <button
        class="rounded-2xl bg-sky-600 px-5 py-3 text-sm font-black text-white shadow-lg shadow-sky-200 transition hover:-translate-y-0.5 hover:bg-sky-700 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:shadow-none"
        :disabled="loading || saving || !canSave"
        type="button"
        @click="saveSettings"
      >
        {{ saving ? '保存中...' : '保存参数' }}
      </button>
    </div>

    <div v-if="loading" class="mt-6 rounded-[1.5rem] border-2 border-slate-100 bg-white px-5 py-10 text-center text-sm font-bold text-slate-500">
      正在加载系统参数...
    </div>

    <form v-else class="mt-6 grid gap-5 rounded-[1.5rem] border-2 border-slate-100 bg-white p-5" @submit.prevent="saveSettings">
      <label class="grid gap-2">
        <span class="text-sm font-black text-slate-700">默认密码</span>
        <input
          v-model="defaultPassword"
          class="rounded-2xl border-2 border-slate-100 px-4 py-3 text-sm font-bold text-slate-800 outline-none transition focus:border-sky-300"
          maxlength="128"
          placeholder="请输入默认密码"
          type="text"
        />
        <span class="text-xs font-semibold text-slate-400">用于初始化内置管理员和重置用户密码。</span>
      </label>

      <label class="grid gap-2">
        <span class="text-sm font-black text-slate-700">edge-tts 音频语速</span>
        <input
          v-model.number="edgeTtsRate"
          class="rounded-2xl border-2 border-slate-100 px-4 py-3 text-sm font-bold text-slate-800 outline-none transition focus:border-sky-300"
          max="1"
          min="0"
          step="0.01"
          type="number"
        />
        <span class="text-xs font-semibold text-slate-400">1 为正常语速；当前为 {{ edgeTtsRate }} 倍速，传给 edge-tts 的 rate 为 {{ ratePercent > 0 ? `+${ratePercent}` : ratePercent }}%。</span>
      </label>
    </form>
  </section>
</template>
