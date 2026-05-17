import { reactive } from 'vue'

export type ToastType = 'info' | 'success' | 'warning' | 'error'

export type ToastItem = {
  id: number
  type: ToastType
  message: string
}

type ConfirmOptions = {
  title?: string
  message: string
  confirmText?: string
  cancelText?: string
  variant?: 'default' | 'danger'
}

export const toastState = reactive({
  items: [] as ToastItem[],
})

export const confirmState = reactive({
  visible: false,
  title: '',
  message: '',
  confirmText: '确认',
  cancelText: '取消',
  variant: 'default' as 'default' | 'danger',
})

let nextToastId = 1
let resolveConfirm: ((confirmed: boolean) => void) | null = null

function showToast(type: ToastType, message: string) {
  const id = nextToastId++
  toastState.items.push({ id, type, message })
  window.setTimeout(() => removeToast(id), 3200)
}

export function removeToast(id: number) {
  const index = toastState.items.findIndex((item) => item.id === id)
  if (index >= 0) {
    toastState.items.splice(index, 1)
  }
}

function settleConfirm(confirmed: boolean) {
  confirmState.visible = false
  if (resolveConfirm) {
    resolveConfirm(confirmed)
    resolveConfirm = null
  }
}

export const notify = {
  info(message: string) {
    showToast('info', message)
  },
  success(message: string) {
    showToast('success', message)
  },
  warning(message: string) {
    showToast('warning', message)
  },
  error(message: string) {
    showToast('error', message)
  },
  confirm(options: ConfirmOptions) {
    if (resolveConfirm) {
      settleConfirm(false)
    }

    confirmState.title = options.title ?? '请确认'
    confirmState.message = options.message
    confirmState.confirmText = options.confirmText ?? '确认'
    confirmState.cancelText = options.cancelText ?? '取消'
    confirmState.variant = options.variant ?? 'default'
    confirmState.visible = true

    return new Promise<boolean>((resolve) => {
      resolveConfirm = resolve
    })
  },
  confirmYes() {
    settleConfirm(true)
  },
  confirmNo() {
    settleConfirm(false)
  },
}
