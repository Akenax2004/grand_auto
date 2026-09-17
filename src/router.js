import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from './views/HomeView.vue'

export const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', name: 'sommaire', component: HomeView },
    {
      path: '/c/:catId',
      name: 'categorie',
      component: () => import('./views/CategoryView.vue'),
      props: true,
    },
    {
      path: '/c/:catId/n/:niveau',
      name: 'niveau',
      component: () => import('./views/QuizView.vue'),
      props: (route) => ({
        catId: route.params.catId,
        niveau: Number(route.params.niveau),
      }),
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
  scrollBehavior: () => ({ top: 0 }),
})
