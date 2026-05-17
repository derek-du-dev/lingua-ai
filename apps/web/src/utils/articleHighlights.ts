import type { ArticleKeyPoint, ArticleKeyPointRange } from '../api/client/types.gen'

export type HighlightRange = ArticleKeyPointRange & {
  keyPointId: string
  type: ArticleKeyPoint['type']
}

export type TextSegment = {
  text: string
  highlight: boolean
  type?: ArticleKeyPoint['type']
  keyPointId?: string
}

export function normalizeRanges(ranges: ArticleKeyPointRange[]) {
  return ranges
    .filter((range) => Number.isFinite(range.start) && Number.isFinite(range.end) && range.start < range.end)
    .map((range) => ({ start: Math.max(0, Math.floor(range.start)), end: Math.max(0, Math.floor(range.end)) }))
    .sort((left, right) => left.start - right.start || left.end - right.end)
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

export function buildHighlightRanges(content: string, points: ArticleKeyPoint[]) {
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

export function buildTextSegments(content: string, ranges: HighlightRange[]) {
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

export function highlightClass(type?: ArticleKeyPoint['type']) {
  return type === 'phrase' ? 'bg-amber-200 text-amber-950' : 'bg-violet-200 text-violet-950'
}
