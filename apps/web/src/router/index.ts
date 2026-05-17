import { createRouter, createWebHistory } from 'vue-router'
import AdminLayout from '../layouts/AdminLayout.vue'
import LoginView from '../views/LoginView.vue'
import StudentHomeView from '../views/StudentHomeView.vue'
import SystemSettingsView from '../views/SystemSettingsView.vue'
import TextbookManagementView from '../views/TextbookManagementView.vue'
import UserManagementView from '../views/UserManagementView.vue'
import { isAdmin, isAuthenticated, isManager, restoreSession } from '../services/auth'
import { notify } from '../services/notify'

function getDefaultManagementPath() {
  if (isAdmin()) {
    return '/admin/users'
  }

  return isManager() ? '/textbooks' : '/learn'
}

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: () => getDefaultManagementPath() },
    { path: '/login', component: LoginView },
    { path: '/admin/textbooks', redirect: '/textbooks' },
    {
      path: '/admin',
      component: AdminLayout,
      meta: { requiresManager: true },
      redirect: () => getDefaultManagementPath(),
      children: [
        { path: 'users', component: UserManagementView, meta: { requiresAdmin: true } },
        { path: 'settings', component: SystemSettingsView, meta: { requiresAdmin: true } },
      ],
    },
    {
      path: '/textbooks',
      component: AdminLayout,
      meta: { requiresManager: true },
      children: [{ path: '', component: TextbookManagementView }],
    },
    {
      path: '/learn',
      component: AdminLayout,
      meta: { requiresAuthenticated: true },
      children: [{ path: '', component: StudentHomeView }],
    },
  ],
})

router.beforeEach(async (to) => {
  await restoreSession()

  if (to.path === '/login') {
    return isAuthenticated() ? getDefaultManagementPath() : true
  }

  if (to.matched.some((record) => record.meta.requiresAuthenticated)) {
    if (!isAuthenticated()) {
      return '/login'
    }
  }

  if (to.matched.some((record) => record.meta.requiresManager)) {
    if (!isAuthenticated()) {
      return '/login'
    }

    if (!isManager()) {
      notify.warning('当前账号无管理权限。')
      return '/learn'
    }
  }

  if (to.matched.some((record) => record.meta.requiresAdmin) && !isAdmin()) {
    notify.warning('当前账号无用户管理权限。')
    return '/textbooks'
  }

  return true
})

export default router
