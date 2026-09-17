<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { getCategory, levelsOf, noteSur20, accorder, glyphOf } from '../data'
import { useProgress } from '../composables/useProgress'
import SignGlyph from '../components/SignGlyph.vue'

const props = defineProps({ catId: { type: String, required: true } })
const router = useRouter()
const { getNiveau, bilanCategorie } = useProgress()

const categorie = computed(() => getCategory(props.catId))

const niveaux = computed(() => {
  if (!categorie.value) return []
  return levelsOf(categorie.value).map((n) => {
    const p = getNiveau(categorie.value.id, n.index)
    const premiere = n.questions[0].num
    const derniere = n.questions[n.questions.length - 1].num
    return {
      index: n.index,
      nombre: n.index + 1,
      premiere,
      derniere,
      total: n.questions.length,
      score: p ? p.best : null,
      note: p ? noteSur20(p.best, p.total) : null,
    }
  })
})

const bilan = computed(() => (categorie.value ? bilanCategorie(categorie.value) : null))

/** Prochain niveau non passé, pour proposer une reprise directe. */
const suivant = computed(() => niveaux.value.find((n) => n.score === null) ?? null)

if (!categorie.value) {
  router.replace('/')
}
</script>

<template>
  <div v-if="categorie" class="mx-auto w-full max-w-[1120px] px-4 sm:px-6">
    <nav class="pt-8 text-[13px] text-encre-soft">
      <RouterLink to="/" class="hover:text-vert underline underline-offset-4">Sommaire</RouterLink>
    </nav>

    <header class="pt-8 pb-8 max-w-[760px]">
      <div class="flex items-start gap-4 sm:gap-5">
        <SignGlyph :kind="glyphOf(categorie)" class="w-12 h-12 sm:w-14 sm:h-14 shrink-0" />
        <div>
          <h1 class="h-display text-[28px] sm:text-[36px] leading-[1.05]">
            {{ categorie.title }}
          </h1>
          <p class="mt-2 text-[15px] leading-relaxed text-encre-soft">
            Chapitre {{ categorie.subtitle.replace('CH ', '') }} du manuel.
            <span class="tab">{{ categorie.count }} questions</span> réparties en
            <span class="tab">{{ niveaux.length }} niveaux</span>.
          </p>
        </div>
      </div>

      <div class="mt-7 flex flex-wrap items-center gap-3">
        <RouterLink
          v-if="suivant"
          :to="{ name: 'niveau', params: { catId: categorie.id, niveau: suivant.index } }"
          class="btn btn-primary"
        >
          {{ bilan.termines ? 'Continuer' : 'Commencer' }} le niveau {{ suivant.nombre }}
        </RouterLink>
        <RouterLink
          v-else
          :to="{ name: 'niveau', params: { catId: categorie.id, niveau: 0 } }"
          class="btn btn-quiet"
        >
          Reprendre depuis le niveau 1
        </RouterLink>

        <p v-if="bilan.termines" class="text-[13px] text-encre-soft">
          <span class="tab font-medium text-encre">{{
            accorder(bilan.termines, 'niveau passé', 'niveaux passés')
          }}</span>
          sur <span class="tab">{{ niveaux.length }}</span>
        </p>
      </div>
    </header>

    <!-- Index des niveaux : colonne tenue courte, sinon l'écart entre le
         numéro de question et l'état du niveau devient un vide. -->
    <section class="pb-8 max-w-[760px]">
      <h2 class="text-[13px] font-medium text-encre-soft pb-3 border-b border-line">
        Les niveaux
      </h2>

      <ul>
        <li v-for="n in niveaux" :key="n.index" class="border-b border-line-soft">
          <RouterLink
            :to="{ name: 'niveau', params: { catId: categorie.id, niveau: n.index } }"
            class="group flex items-center gap-4 py-4"
          >
            <span
              class="ref text-[15px] font-semibold w-[5rem] shrink-0 group-hover:text-vert transition-colors"
            >
              Niveau {{ n.nombre }}
            </span>

            <span class="tab text-[13px] text-encre-soft flex-1">
              questions {{ n.premiere }} à {{ n.derniere }}
            </span>

            <span class="shrink-0 text-right">
              <template v-if="n.score !== null">
                <span
                  class="tab inline-block text-[13px] font-semibold px-2.5 py-1 rounded-full"
                  :class="n.note >= 10 ? 'bg-vert-wash text-vert' : 'bg-rouge-wash text-rouge'"
                >
                  {{ n.note }}/20
                </span>
                <span class="block mt-1 tab text-[12px] text-encre-faint">
                  {{ n.score }} sur {{ n.total }}
                </span>
              </template>
              <span v-else class="text-[13px] text-encre-faint">à faire</span>
            </span>
          </RouterLink>
        </li>
      </ul>
    </section>
  </div>
</template>
