<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { ArticleKeyPoint, ArticleKeyPointRange, ArticlePublic } from '../api/client/types.gen'
import { notify } from '../services/notify'

const props = defineProps<{
  open: boolean
  article: ArticlePublic | null
  saving: boolean
}>()

const emit = defineEmits<{
  close: []
  save: [keyPoints: ArticleKeyPoint[]]
}>()

type HighlightRange = ArticleKeyPointRange & {
  keyPointId: string
  type: ArticleKeyPoint['type']
}

type TextSegment = {
  text: string
  highlight: boolean
  type?: ArticleKeyPoint['type']
  keyPointId?: string
}

type Draft = {
  id: string
  text: string
  note: string
  ranges: ArticleKeyPointRange[]
  editingIndex: number | null
}

const contentRef = ref<HTMLElement | null>(null)
const keyPoints = ref<ArticleKeyPoint[]>([])
const originalKeyPoints = ref('[]')
const draft = ref<Draft | null>(null)
const hoveredKeyPointId = ref('')
const tooltipPosition = ref({ x: 0, y: 0 })
let tooltipHideTimer: ReturnType<typeof setTimeout> | null = null

const articleContent = computed(() => props.article?.content ?? '')
const dirty = computed(() => JSON.stringify(normalizeKeyPoints(keyPoints.value)) !== originalKeyPoints.value)

const highlightRanges = computed(() => buildHighlightRanges(articleContent.value, keyPoints.value))
const textSegments = computed(() => buildTextSegments(articleContent.value, highlightRanges.value))
const hoveredKeyPoint = computed(() => keyPoints.value.find((point) => point.id === hoveredKeyPointId.value && point.abbreviation) ?? null)
const hoveredKeyPointIndex = computed(() => keyPoints.value.findIndex((point) => point.id === hoveredKeyPointId.value))
const draftTitle = computed(() => (!draft.value || draft.value.editingIndex === null ? '添加重点' : '编辑重点'))

watch(
  () => [props.open, props.article] as const,
  () => {
    if (!props.open) {
      return
    }

    keyPoints.value = normalizeKeyPoints(props.article?.key_points ?? [])
    originalKeyPoints.value = JSON.stringify(keyPoints.value)
    draft.value = null
  },
  { immediate: true },
)

function normalizeKeyPoints(points: ArticleKeyPoint[]) {
  return points.map((point) => ({
    id: point.id,
    type: point.type,
    text: point.text.trim(),
    abbreviation: point.abbreviation?.trim() ?? '',
    ranges: normalizeRanges(point.ranges ?? []),
  }))
}

function normalizeRanges(ranges: ArticleKeyPointRange[]) {
  return ranges
    .filter((range) => Number.isFinite(range.start) && Number.isFinite(range.end) && range.start < range.end)
    .map((range) => ({ start: Math.max(0, Math.floor(range.start)), end: Math.max(0, Math.floor(range.end)) }))
    .sort((left, right) => left.start - right.start || left.end - right.end)
}

function createId() {
  return crypto.randomUUID?.() ?? `${Date.now()}-${Math.random().toString(16).slice(2)}`
}

function escapeRegex(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function isWordChar(value: string) {
  return /[\p{L}\p{N}_]/u.test(value)
}

function shouldUseWordBoundary(value: string) {
  return /[\p{L}\p{N}_]/u.test(value)
}

function buildPhraseRegex(phrase: string) {
  const escapedParts = phrase.trim().split(/\s+/).map(escapeRegex).filter(Boolean)
  if (escapedParts.length === 0) {
    return null
  }

  return new RegExp(escapedParts.join('\\s+'), 'giu')
}

function findTextRanges(content: string, point: ArticleKeyPoint) {
  const ranges: HighlightRange[] = []
  const regex = buildPhraseRegex(point.text)
  if (!regex) {
    return ranges
  }

  let match: RegExpExecArray | null
  while ((match = regex.exec(content))) {
    const matched = match[0]
    if (!matched) {
      regex.lastIndex += 1
      continue
    }

    const start = match.index
    const end = start + matched.length
    const before = start > 0 ? content[start - 1] : ''
    const after = end < content.length ? content[end] : ''
    const first = matched[0]
    const last = matched[matched.length - 1]
    if (shouldUseWordBoundary(first) && before && isWordChar(before)) {
      continue
    }
    if (shouldUseWordBoundary(last) && after && isWordChar(after)) {
      continue
    }

    ranges.push({ start, end, keyPointId: point.id, type: point.type })
  }

  return ranges
}

function hasSameRange(ranges: HighlightRange[], range: ArticleKeyPointRange, keyPointId: string) {
  return ranges.some((item) => item.keyPointId === keyPointId && item.start === range.start && item.end === range.end)
}

function buildHighlightRanges(content: string, points: ArticleKeyPoint[]) {
  const ranges: HighlightRange[] = []

  for (const point of points) {
    ranges.push(...findTextRanges(content, point))

    for (const range of normalizeRanges(point.ranges ?? [])) {
      if (range.start < content.length && range.end <= content.length && !hasSameRange(ranges, range, point.id)) {
        ranges.push({ ...range, keyPointId: point.id, type: point.type })
      }
    }
  }

  return ranges.sort((left, right) => left.start - right.start || right.end - left.end)
}

function buildTextSegments(content: string, ranges: HighlightRange[]) {
  const segments: TextSegment[] = []
  let cursor = 0

  for (const range of ranges) {
    const start = Math.max(cursor, range.start)
    const end = Math.min(content.length, range.end)
    if (end <= cursor) {
      continue
    }

    if (start > cursor) {
      segments.push({ text: content.slice(cursor, start), highlight: false })
    }
    segments.push({ text: content.slice(start, end), highlight: true, type: range.type, keyPointId: range.keyPointId })
    cursor = end
  }

  if (cursor < content.length) {
    segments.push({ text: content.slice(cursor), highlight: false })
  }

  return segments.length > 0 ? segments : [{ text: content, highlight: false }]
}

function getSelectionRange() {
  const container = contentRef.value
  const selection = window.getSelection()
  if (!container || !selection || selection.rangeCount === 0 || selection.isCollapsed) {
    return null
  }

  const range = selection.getRangeAt(0)
  if (!container.contains(range.commonAncestorContainer)) {
    return null
  }

  const startRange = document.createRange()
  startRange.selectNodeContents(container)
  startRange.setEnd(range.startContainer, range.startOffset)
  const endRange = document.createRange()
  endRange.selectNodeContents(container)
  endRange.setEnd(range.endContainer, range.endOffset)

  let start = startRange.toString().length
  let end = endRange.toString().length
  if (start > end) {
    ;[start, end] = [end, start]
  }

  const raw = articleContent.value.slice(start, end)
  const leading = raw.match(/^\s*/)?.[0].length ?? 0
  const trailing = raw.match(/\s*$/)?.[0].length ?? 0
  start += leading
  end -= trailing

  if (start >= end) {
    return null
  }

  return { start, end }
}

function findKeyPointIndexByRange(range: ArticleKeyPointRange) {
  const existingRange = highlightRanges.value.find((item) => item.start < range.end && item.end > range.start)
  if (!existingRange) {
    return -1
  }

  return keyPoints.value.findIndex((point) => point.id === existingRange.keyPointId)
}

function activateSelectionDraft() {
  const range = getSelectionRange()
  if (!range) {
    return
  }

  const existingIndex = findKeyPointIndexByRange(range)
  if (existingIndex >= 0) {
    editKeyPoint(existingIndex)
    return
  }

  draft.value = {
    id: createId(),
    text: articleContent.value.slice(range.start, range.end),
    note: '',
    ranges: [range],
    editingIndex: null,
  }
}

function editKeyPoint(index: number) {
  const point = keyPoints.value[index]
  draft.value = {
    id: point.id,
    text: point.text,
    note: point.abbreviation ?? '',
    ranges: normalizeRanges(point.ranges ?? []),
    editingIndex: index,
  }
}

function saveDraft() {
  if (!draft.value) {
    return
  }

  const keyPoint: ArticleKeyPoint = {
    id: draft.value.id,
    type: 'selection',
    text: draft.value.text,
    abbreviation: draft.value.note.trim(),
    ranges: normalizeRanges(draft.value.ranges),
  }

  if (draft.value.editingIndex === null) {
    keyPoints.value.push(keyPoint)
  } else {
    keyPoints.value[draft.value.editingIndex] = keyPoint
  }

  draft.value = null
  window.getSelection()?.removeAllRanges()
}

async function removeKeyPoint(index: number) {
  const point = keyPoints.value[index]
  if (!point) {
    return
  }

  const confirmed = await notify.confirm({
    title: '确认删除重点词',
    message: `确定要删除“${point.text}”吗？`,
    confirmText: '删除',
    variant: 'danger',
  })
  if (!confirmed) {
    return
  }

  keyPoints.value.splice(index, 1)
  if (hoveredKeyPointId.value === point.id) {
    hoveredKeyPointId.value = ''
  }
  const currentDraft = draft.value
  if (currentDraft?.editingIndex === index) {
    draft.value = null
  } else if (currentDraft && currentDraft.editingIndex !== null && currentDraft.editingIndex > index) {
    currentDraft.editingIndex -= 1
  }
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

  const point = keyPoints.value.find((item) => item.id === segment.keyPointId)
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

function editHoveredKeyPoint() {
  if (hoveredKeyPointIndex.value >= 0) {
    editKeyPoint(hoveredKeyPointIndex.value)
    hoveredKeyPointId.value = ''
  }
}

async function removeHoveredKeyPoint() {
  if (hoveredKeyPointIndex.value >= 0) {
    await removeKeyPoint(hoveredKeyPointIndex.value)
  }
}

async function removeDraftKeyPoint() {
  const currentDraft = draft.value
  if (currentDraft && currentDraft.editingIndex !== null) {
    await removeKeyPoint(currentDraft.editingIndex)
  }
}

async function closeDrawer() {
  if (dirty.value) {
    const confirmed = await notify.confirm({
      title: '放弃未保存的重点词修改？',
      message: '关闭抽屉会丢失当前未保存的重点词修改。',
      confirmText: '放弃修改',
      variant: 'danger',
    })
    if (!confirmed) {
      return
    }
  }

  emit('close')
}

function saveKeyPoints() {
  emit('save', normalizeKeyPoints(keyPoints.value))
}

function highlightClass(type?: ArticleKeyPoint['type']) {
  return type === 'phrase' ? 'bg-amber-200 text-amber-950' : 'bg-violet-200 text-violet-950'
}
</script>

<template>
  <div v-if="open && article" class="fixed inset-0 z-40 flex justify-end bg-slate-900/35 backdrop-blur-sm">
    <aside class="flex h-full w-full flex-col overflow-hidden border-l-4 border-white bg-white shadow-2xl shadow-slate-500/30 lg:w-[85vw]">
      <header class="flex items-start justify-between gap-4 border-b border-slate-100 px-6 py-5">
        <div class="min-w-0">
          <p class="text-sm font-black uppercase tracking-[0.25em] text-sky-500">Key Points</p>
          <h2 class="mt-1 truncate text-2xl font-black text-slate-900">{{ article.title }}</h2>
          <p class="mt-1 text-sm font-semibold text-slate-500">在左侧选择内容后，右侧可保存为重点并添加注释。</p>
        </div>
        <button class="text-2xl font-black text-slate-300 transition hover:text-slate-600" type="button" @click="closeDrawer">×</button>
      </header>

      <div class="grid min-h-0 flex-1 gap-5 overflow-hidden p-5 xl:grid-cols-[minmax(0,1.3fr)_26rem]">
        <section class="min-h-0 overflow-hidden rounded-[1.75rem] border-2 border-slate-100 bg-slate-50/80 p-5">
          <div>
            <h3 class="text-lg font-black text-slate-900">文章预览</h3>
            <p class="text-xs font-semibold text-slate-500">用鼠标选择正文内容，右侧会出现编辑区域。</p>
          </div>

          <div
            ref="contentRef"
            class="mt-4 h-[calc(100%-3.25rem)] overflow-y-auto whitespace-pre-wrap rounded-[1.25rem] border-2 border-white bg-white p-5 text-base font-semibold leading-8 text-slate-700 shadow-inner selection:bg-sky-200"
            @mouseup="activateSelectionDraft"
          >
            <span
              v-for="(segment, index) in textSegments"
              :key="index"
              :class="segment.highlight ? `rounded px-1 py-0.5 ${highlightClass(segment.type)}` : ''"
              @mouseenter="segment.highlight && showTooltip(segment, $event)"
              @mouseleave="segment.highlight && scheduleHideTooltip()"
            >{{ segment.text }}</span>
          </div>
        </section>

        <section class="grid min-h-0 gap-4 overflow-hidden grid-rows-[auto_minmax(0,1fr)]">
          <div class="rounded-[1.5rem] border-2 border-slate-100 bg-white p-5 shadow-sm">
            <div class="flex items-center justify-between gap-3">
              <h3 class="text-lg font-black text-slate-900">{{ draftTitle }}</h3>
              <span v-if="draft?.editingIndex !== null && draft" class="rounded-full bg-sky-50 px-3 py-1 text-xs font-black text-sky-700">编辑中</span>
            </div>

            <div v-if="draft" class="mt-4 space-y-4">
              <label class="block">
                <span class="mb-2 block text-sm font-black text-slate-700">重点</span>
                <div class="max-h-28 overflow-y-auto rounded-2xl border-2 border-violet-100 bg-violet-50/60 px-4 py-3 text-sm font-bold leading-6 text-violet-900">
                  {{ draft.text }}
                </div>
              </label>

              <label class="block">
                <span class="mb-2 block text-sm font-black text-slate-700">注释</span>
                <textarea
                  v-model="draft.note"
                  class="min-h-24 w-full resize-y rounded-2xl border-2 border-slate-100 bg-slate-50/70 px-4 py-3 text-sm font-bold outline-none transition focus:border-sky-300 focus:bg-white"
                  placeholder="填写这个重点的说明、用法或提示"
                />
              </label>

              <div class="flex justify-end gap-2">
                <button class="rounded-2xl border-2 border-slate-200 px-4 py-2 text-sm font-black text-slate-600 transition hover:bg-slate-50" type="button" @click="draft = null">
                  取消
                </button>
                <button class="rounded-2xl bg-sky-600 px-4 py-2 text-sm font-black text-white shadow-lg shadow-sky-100 transition hover:bg-sky-700" type="button" @click="saveDraft">
                  保存
                </button>
                <button v-if="draft.editingIndex !== null" class="rounded-2xl bg-rose-600 px-4 py-2 text-sm font-black text-white shadow-lg shadow-rose-100 transition hover:bg-rose-700" type="button" @click="removeDraftKeyPoint">
                  删除
                </button>
              </div>
            </div>

            <div v-else class="mt-4 rounded-2xl border-2 border-dashed border-slate-200 bg-slate-50/70 px-4 py-8 text-center text-sm font-bold text-slate-400">
              左侧文章选择内容后可以设为重点。
            </div>
          </div>

          <div class="min-h-0 overflow-y-auto rounded-[1.5rem] border-2 border-slate-100 bg-white p-5 shadow-sm">
            <div class="flex items-center justify-between gap-3">
              <h3 class="text-lg font-black text-slate-900">已添加重点词</h3>
              <span v-if="dirty" class="rounded-full bg-amber-50 px-3 py-1 text-xs font-black text-amber-700">未保存</span>
            </div>

            <div class="mt-4 space-y-3">
              <article v-for="(point, index) in keyPoints" :key="point.id" class="rounded-[1.25rem] border-2 border-violet-100 bg-violet-50/50 p-4">
                <div class="flex items-start justify-between gap-3">
                  <div class="min-w-0">
                    <p class="line-clamp-2 text-sm font-black leading-6 text-violet-950">{{ point.text }}</p>
                    <p v-if="point.abbreviation" class="mt-2 whitespace-pre-wrap text-xs font-semibold leading-5 text-slate-500">{{ point.abbreviation }}</p>
                    <p class="mt-2 text-xs font-semibold text-violet-500">{{ point.ranges?.length ?? 0 }} 个片段</p>
                  </div>
                  <div class="flex shrink-0 gap-2">
                    <button class="rounded-xl bg-white px-3 py-2 text-xs font-black text-sky-700 transition hover:bg-sky-50" type="button" @click="editKeyPoint(index)">
                      编辑
                    </button>
                    <button class="rounded-xl bg-white px-3 py-2 text-xs font-black text-rose-600 transition hover:bg-rose-50" type="button" @click="removeKeyPoint(index)">
                      删除
                    </button>
                  </div>
                </div>
              </article>

              <div v-if="keyPoints.length === 0" class="rounded-[1.25rem] border-2 border-dashed border-slate-200 px-4 py-10 text-center text-sm font-bold text-slate-400">
                暂无重点词。
              </div>
            </div>
          </div>
        </section>
      </div>

      <footer class="flex justify-end gap-3 border-t border-slate-100 px-6 py-4">
        <button class="rounded-2xl border-2 border-slate-200 px-5 py-3 text-sm font-black text-slate-600 transition hover:bg-slate-50" type="button" @click="closeDrawer">
          关闭
        </button>
        <button
          class="rounded-2xl bg-sky-600 px-5 py-3 text-sm font-black text-white shadow-lg shadow-sky-200 transition hover:-translate-y-0.5 hover:bg-sky-700 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:shadow-none"
          :disabled="saving || !dirty"
          type="button"
          @click="saveKeyPoints"
        >
          {{ saving ? '保存中...' : '保存重点词' }}
        </button>
      </footer>
    </aside>

    <div
      v-if="hoveredKeyPoint"
      class="fixed z-50 max-w-xs rounded-2xl border-2 border-white bg-slate-900 px-4 py-3 text-white shadow-2xl shadow-slate-500/40"
      :style="{ left: `${tooltipPosition.x}px`, top: `${tooltipPosition.y + 8}px` }"
      @mouseenter="clearTooltipTimer"
      @mouseleave="scheduleHideTooltip"
    >
      <p class="whitespace-pre-wrap text-sm font-semibold leading-6">{{ hoveredKeyPoint.abbreviation }}</p>
      <div class="mt-3 flex justify-end gap-2">
        <button class="rounded-xl bg-white/10 p-2 text-white transition hover:bg-sky-500" title="编辑" type="button" @click="editHoveredKeyPoint">
          <svg class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path d="M12 20h9" stroke-linecap="round" />
            <path d="m16.5 3.5 4 4L8 20H4v-4L16.5 3.5Z" stroke-linejoin="round" />
          </svg>
        </button>
        <button class="rounded-xl bg-white/10 p-2 text-white transition hover:bg-rose-500" title="删除" type="button" @click="removeHoveredKeyPoint">
          <svg class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path d="M3 6h18" stroke-linecap="round" />
            <path d="M8 6V4h8v2" stroke-linecap="round" stroke-linejoin="round" />
            <path d="m6 6 1 14h10l1-14" stroke-linejoin="round" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>
