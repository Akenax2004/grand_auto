<script setup>
import { computed } from 'vue'
import { meta, categories, levelsOf, glyphOf } from '../data'
import { useProgress } from '../composables/useProgress'
import RoadStrip from '../components/RoadStrip.vue'
import SignGlyph from '../components/SignGlyph.vue'

const { getNiveau, bilanCategorie, bilanGlobal, reinitialiser } = useProgress()

const lignes = computed(() =>
  categories.map((c) => {
    const niveaux = levelsOf(c)
    return {
      ...c,
      glyph: glyphOf(c),
      nbNiveaux: niveaux.length,
      bilan: bilanCategorie(c),
      marks: niveaux.map((n) => (getNiveau(c.id, n.index) ? 'ok' : null)),
    }
  }),
)

const global = computed(() => bilanGlobal())

function effacer() {
  if (confirm('Effacer toute la progression et les notes enregistrées ?')) {
    reinitialiser()
  }
}
</script>

<template>
  <div class="mx-auto w-full max-w-[1120px] px-4 sm:px-6">
    <!-- Entrée en matière : le départ de la route -->
    <section class="pt-12 sm:pt-16 pb-10">
      <h1 class="h-display text-[34px] sm:text-[48px] leading-[1.02] max-w-[20ch]">
        Le manuel du candidat à l'examen du permis
      </h1>
      <p class="mt-5 text-[16px] sm:text-[17px] leading-relaxed text-encre-soft max-w-[58ch]">
        Les <span class="tab font-semibold text-encre">{{ meta.total }}</span> questions à choix
        multiples de l'édition 2011, telles qu'elles figurent dans le manuel. Chaque chapitre est
        découpé en niveaux de {{ meta.levelSize }} questions ; votre note s'affiche à la fin de
        chacun.
      </p>

      <p v-if="global.niveauxTermines" class="mt-7 text-[14px] text-encre-soft">
        Progression :
        <span class="tab font-semibold text-encre"
          >{{ global.niveauxTermines }} / {{ global.niveauxTotal }} niveaux</span
        >
      </p>
    </section>

    <!-- Les chapitres, présentés comme des panneaux -->
    <section class="pb-6">
      <h2 class="text-[13px] font-medium text-encre-soft pb-4 border-b border-line">
        Choisissez un chapitre
      </h2>

      <div class="mt-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
        <RouterLink
          v-for="c in lignes"
          :key="c.id"
          :to="{ name: 'categorie', params: { catId: c.id } }"
          class="group panel rounded-xl hover:border-vert transition-colors"
        >
          <div class="p-5 flex flex-col h-full">
            <div class="flex items-start justify-between gap-4">
              <SignGlyph :kind="c.glyph" class="w-11 h-11 shrink-0" />
              <span class="ref text-[13px] font-medium text-encre-faint">
                {{ c.subtitle.replace('CH ', '') }}
              </span>
            </div>

            <h3
              class="mt-4 h-panel text-[18px] sm:text-[19px] leading-tight group-hover:text-vert transition-colors"
            >
              {{ c.title }}
            </h3>
            <p class="mt-2 text-[14px] text-encre-soft leading-relaxed">{{ c.description }}</p>

            <div class="mt-auto pt-5">
              <div class="border-t border-line-soft pt-4">
                <div class="flex items-baseline justify-between gap-3 text-[13px]">
                  <span class="tab text-encre-soft">{{ c.count }} questions</span>
                  <span
                    class="tab"
                    :class="c.bilan.termine ? 'text-vert font-semibold' : 'text-encre-faint'"
                  >
                    {{ c.bilan.termines }}/{{ c.nbNiveaux }} niveaux
                  </span>
                </div>
                <div class="mt-2">
                  <RoadStrip :total="c.nbNiveaux" :marks="c.marks" compact />
                </div>
              </div>
            </div>
          </div>
        </RouterLink>
      </div>
    </section>

    <p v-if="global.niveauxTermines" class="py-6 text-[13px] text-encre-faint">
      Les niveaux déjà passés sont conservés dans ce navigateur.
      <button type="button" class="underline underline-offset-4 hover:text-rouge" @click="effacer">
        Effacer ma progression
      </button>
    </p>
  </div>
</template>
