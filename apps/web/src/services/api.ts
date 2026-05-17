import { client } from '../api/client/client.gen'

let accessToken = ''

export function initializeApi() {
  client.setConfig({
    baseUrl: '/api',
    auth: () => accessToken,
  })
}

export function setApiToken(token: string | null) {
  accessToken = token ?? ''
}

export function getApiErrorMessage(apiError: unknown, fallback = '操作失败，请稍后再试。') {
  if (apiError && typeof apiError === 'object' && 'detail' in apiError) {
    const detail = (apiError as { detail?: unknown }).detail

    if (typeof detail === 'string') {
      const messages: Record<string, string> = {
        'Invalid username or password': '账号或密码不正确，再检查一下吧。',
        'Admin permission required': '当前账号无管理员权限。',
        'Management permission required': '当前账号无管理权限。',
      }

      return messages[detail] ?? detail
    }

    if (Array.isArray(detail)) {
      const messages = detail
        .map((item) => (item && typeof item === 'object' && 'msg' in item ? String(item.msg) : ''))
        .filter(Boolean)

      if (messages.length > 0) {
        return messages.join('；')
      }
    }
  }

  return fallback
}
