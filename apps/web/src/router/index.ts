import { createRouter, createWebHistory } from 'vue-router'
import AdminLayout from '../layouts/AdminLayout.vue'
import LoginView from '../views/LoginView.vue'
import TextbookManagementView from '../views/TextbookManagementView.vue'
import UserManagementView from '../views/UserManagementView.vue'
import { isAdmin, isAuthenticated, logout, restoreSession } from '../services/auth'
import { notify } from '../services/notify'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/admin/users' },
    { path: '/login', component: LoginView },
    {
      path: '/admin',
      component: AdminLayout,
      meta: { requiresAdmin: true },
      redirect: '/admin/users',
      children: [
        { path: 'users', component: UserManagementView },
        { path: 'textbooks', component: TextbookManagementView },
      ],
    },
  ],
})

router.beforeEach(async (to) => {
  await restoreSession()

  if (to.path === '/login') {
    return isAuthenticated() && isAdmin() ? '/admin/users' : true
  }

  if (to.matched.some((record) => record.meta.requiresAdmin)) {
    if (!isAuthenticated()) {
      return '/login'
    }

    if (!isAdmin()) {
      notify.warning('当前账号无管理权限。')
      logout()
      return '/login'
    }
  }

  return true
})

export default router
