<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { meta, categories } from './data'

const route = useRoute()
const surSommaire = computed(() => route.name === 'sommaire')
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <!-- Bandeau vert « panneau de direction » -->
    <header class="sticky top-0 z-20 bg-vert text-papier">
      <div class="mx-auto w-full max-w-[1120px] px-4 sm:px-6">
        <div class="py-3 flex flex-wrap items-center gap-x-6 gap-y-2">
          <RouterLink to="/" class="group mr-auto flex items-center gap-3">
            <span class="w-[18px] h-[22px] shrink-0 block" aria-hidden="true">
              <svg viewBox="0 0 32 32" class="w-full h-full">
                <rect
                  x="4.5"
                  y="3.5"
                  width="23"
                  height="25"
                  rx="3.5"
                  fill="none"
                  stroke="#ffffff"
                  stroke-width="2.5"
                  opacity="0.9"
                />
                <rect x="9.5" y="18" width="13" height="5" rx="2.5" fill="#f4b73e" />
              </svg>
            </span>
            <span>
              <span class="block text-[12px] text-papier/75 leading-tight">
                République du Bénin, édition 2011
              </span>
              <span
                class="h-panel block text-[17px] sm:text-[18px] leading-tight group-hover:text-jaune transition-colors"
              >
                Manuel du permis de conduire
              </span>
            </span>
          </RouterLink>

          <p class="text-[13px] text-papier/90">
            <span class="tab font-bold text-papier">{{ meta.total }}</span> questions du manuel
          </p>

          <RouterLink
            v-if="!surSommaire"
            to="/"
            class="text-[13px] font-semibold px-3.5 py-2 border border-papier/40 hover:bg-papier hover:text-vert transition-colors"
          >
            Sommaire
          </RouterLink>
        </div>
      </div>
      <!-- Liseré jaune : le marquage au sol, seul accent vif -->
      <div class="h-[3px] bg-jaune" aria-hidden="true"></div>
    </header>

    <main class="flex-1">
      <RouterView />
    </main>

    <footer class="mt-16">
      <!-- Le site se termine sur une route -->
      <div class="road h-[6px]" aria-hidden="true"></div>
      <div
        class="mx-auto w-full max-w-[1120px] px-4 sm:px-6 py-6 text-[13px] text-encre-soft flex flex-wrap gap-x-6 gap-y-2"
      >
        <p>Questions extraites du manuel officiel, sans ajout.</p>
        <p class="tab">
          {{ meta.total }} questions réparties en {{ categories.length }} chapitres
        </p>
      </div>
    </footer>
  </div>
</template>
