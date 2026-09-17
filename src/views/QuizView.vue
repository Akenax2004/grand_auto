<script setup>
import { computed, ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  getCategory,
  getLevel,
  isCorrect,
  noteSur20,
  appreciation,
  accorder,
  LEVEL_SIZE,
} from '../data'
import { useProgress } from '../composables/useProgress'
import QuestionCard from '../components/QuestionCard.vue'
import RoadStrip from '../components/RoadStrip.vue'

const props = defineProps({
  catId: { type: String, required: true },
  niveau: { type: Number, required: true },
})

const router = useRouter()
const { enregistrer, getNiveau } = useProgress()

const categorie = computed(() => getCategory(props.catId))
const niveau = computed(() => (categorie.value ? getLevel(categorie.value, props.niveau) : null))
const questions = computed(() => niveau.value?.questions ?? [])

const index = ref(0)
const selection = ref([])
const verrouille = ref(false)
const resultats = ref([]) // { ok, selected, answer }
const termine = ref(false)

const question = computed(() => questions.value[index.value] ?? null)
const marks = computed(() => resultats.value.map((r) => (r.ok ? 'ok' : 'ko')))
const score = computed(() => resultats.value.filter((r) => r.ok).length)
const note = computed(() => noteSur20(score.value, questions.value.length))
const derniere = computed(() => index.value === questions.value.length - 1)

const niveauSuivant = computed(() => {
  if (!categorie.value) return null
  const total = Math.ceil(categorie.value.questions.length / LEVEL_SIZE)
  return props.niveau + 1 < total ? props.niveau + 1 : null
})

/** Meilleure note antérieure, figée avant l'enregistrement du passage en cours. */
const meilleurAvant = ref(null)

if (!categorie.value || !niveau.value) {
  router.replace('/')
}

function basculer(lettre) {
  if (verrouille.value) return
  const i = selection.value.indexOf(lettre)
  if (i === -1) selection.value = [...selection.value, lettre]
  else selection.value = selection.value.filter((l) => l !== lettre)
}

function valider() {
  if (!selection.value.length) return
  const ok = isCorrect(selection.value, question.value.answer)
  resultats.value = [...resultats.value, { ok, selected: [...selection.value], answer: [...question.value.answer] }]
  verrouille.value = true
}

function avancer() {
  if (derniere.value) {
    const total = questions.value.length
    const s = resultats.value.filter((r) => r.ok).length
    meilleurAvant.value = getNiveau(categorie.value.id, props.niveau)
    enregistrer(categorie.value.id, props.niveau, s, total)
    termine.value = true
    lancerNote(noteSur20(s, total))
    return
  }
  index.value += 1
  selection.value = []
  verrouille.value = false
}

function recommencer() {
  index.value = 0
  selection.value = []
  verrouille.value = false
  resultats.value = []
  termine.value = false
  noteAffichee.value = 0
  meilleurAvant.value = null
}

/* Révélation du score : le seul moment animé du site. */
const noteAffichee = ref(0)
function lancerNote(cible) {
  const reduire = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
  if (reduire) {
    noteAffichee.value = cible
    return
  }
  const debut = performance.now()
  const duree = 750
  function pas(t) {
    const p = Math.min(1, (t - debut) / duree)
    const e = 1 - Math.pow(1 - p, 3)
    noteAffichee.value = Math.round(cible * e * 10) / 10
    if (p < 1) requestAnimationFrame(pas)
  }
  requestAnimationFrame(pas)
}

/** Questions manquées, pour la relecture en fin de niveau. */
const ratees = computed(() =>
  resultats.value
    .map((r, i) => ({ ...r, question: questions.value[i] }))
    .filter((r) => !r.ok),
)

const texteReponse = (q) =>
  q.answer
    .map((l) => {
      const o = q.options.find((x) => x.letter === l)
      return o && o.text ? `${l}) ${o.text}` : `${l})`
    })
    .join('  ')

watch(index, () => window.scrollTo({ top: 0, behavior: 'smooth' }))
onMounted(() => window.scrollTo({ top: 0 }))
</script>

<template>
  <div v-if="categorie && question" class="mx-auto w-full max-w-[860px] px-4 sm:px-6">
    <!-- En-tête : fil d'ariane + progression du niveau -->
    <nav class="pt-8 flex flex-wrap items-baseline gap-x-3 text-[13px] text-encre-soft">
      <RouterLink to="/" class="hover:text-vert underline underline-offset-4">Sommaire</RouterLink>
      <RouterLink
        :to="{ name: 'categorie', params: { catId: categorie.id } }"
        class="hover:text-vert underline underline-offset-4"
      >
        {{ categorie.title }}
      </RouterLink>
      <span class="tab text-encre-faint">Niveau {{ niveau.index + 1 }}</span>
    </nav>

    <!-- ----------------------------- Passage du niveau ----------------------------- -->
    <template v-if="!termine">
      <div class="pt-6 pb-7">
        <div class="flex items-baseline justify-between gap-4 pb-4">
          <p class="tab text-[13px] text-encre-soft">
            Question {{ index + 1 }} sur {{ questions.length }}
          </p>
          <p class="text-[13px] text-encre-soft">
            {{ selection.length ? 'Sélection en cours' : 'Sélectionnez votre réponse' }}
          </p>
        </div>
        <RoadStrip :total="questions.length" :marks="marks" :current="index" />
      </div>

      <QuestionCard
        :question="question"
        :selected="selection"
        :locked="verrouille"
        @toggle="basculer"
      />

      <div class="pt-5 pb-10 flex flex-wrap items-center gap-3">
        <button
          v-if="!verrouille"
          type="button"
          class="btn btn-primary"
          :disabled="!selection.length"
          @click="valider"
        >
          Valider
        </button>
        <button v-else type="button" class="btn btn-primary" @click="avancer">
          {{ derniere ? 'Voir ma note' : 'Question suivante' }}
        </button>

        <p v-if="verrouille" class="text-[14px]" :class="resultats[index].ok ? 'text-vert' : 'text-rouge'">
          <span class="font-semibold">
            {{ resultats[index].ok ? 'Réponse juste' : 'Réponse fausse' }}
          </span>
          <span v-if="!resultats[index].ok" class="text-encre-soft">
            — la bonne réponse était
            <span class="ref font-medium text-encre">{{ question.answer.join(', ') }}</span>
          </span>
        </p>

        <p v-else class="text-[13px] text-encre-faint">
          Certaines questions admettent plusieurs réponses.
        </p>
      </div>
    </template>

    <!-- ----------------------------- Fin de niveau ----------------------------- -->
    <template v-else>
      <section class="pt-10 pb-6 note-in">
        <p class="tab text-[13px] text-encre-soft">
          {{ categorie.title }}, niveau {{ niveau.index + 1 }}
        </p>

        <div class="mt-6 flex flex-wrap items-end gap-x-8 gap-y-4">
          <p class="num text-[76px] sm:text-[96px] leading-[0.85]" :class="note >= 10 ? 'text-vert' : 'text-rouge'">
            {{ noteAffichee }}<span class="text-[30px] sm:text-[38px] text-encre-soft">/20</span>
          </p>
          <div class="pb-3">
            <p class="h-panel text-[20px] sm:text-[22px]">{{ appreciation(note) }}</p>
            <p class="tab text-[14px] text-encre-soft">
              {{ accorder(score, 'bonne réponse', 'bonnes réponses') }}
              sur {{ questions.length }}
            </p>
          </div>
        </div>

        <div class="mt-9">
          <RoadStrip :total="questions.length" :marks="marks" />
        </div>

        <p
          v-if="meilleurAvant && meilleurAvant.best > score"
          class="mt-4 text-[13px] text-encre-soft"
        >
          Votre meilleur passage sur ce niveau reste
          <span class="tab font-semibold text-encre"
            >{{ noteSur20(meilleurAvant.best, meilleurAvant.total) }}/20</span
          >.
        </p>

        <div class="mt-7 flex flex-wrap gap-3">
          <RouterLink
            v-if="niveauSuivant !== null"
            :to="{ name: 'niveau', params: { catId: categorie.id, niveau: niveauSuivant } }"
            class="btn btn-primary"
          >
            Niveau {{ niveauSuivant + 1 }}
          </RouterLink>
          <button type="button" class="btn btn-quiet" @click="recommencer">
            Refaire ce niveau
          </button>
          <RouterLink
            :to="{ name: 'categorie', params: { catId: categorie.id } }"
            class="btn btn-quiet"
          >
            Tous les niveaux
          </RouterLink>
        </div>
      </section>

      <!-- Relecture des erreurs -->
      <section v-if="ratees.length" class="pb-12">
        <h2 class="tab text-[13px] font-medium text-encre-soft pb-3 border-b border-line">
          À revoir ({{ ratees.length }})
        </h2>
        <ul>
          <li
            v-for="r in ratees"
            :key="r.question.num"
            class="border-b border-line-soft py-5 grid gap-2.5"
          >
            <p class="ref text-[13px] text-encre-faint">Question n°{{ r.question.num }}</p>
            <p class="text-[15px] font-medium leading-relaxed max-w-[62ch]">
              {{ r.question.text }}
            </p>
            <p class="text-[14px] text-encre-soft">
              Vous avez répondu
              <span class="ref text-rouge">{{ r.selected.join(', ') }}</span>. La bonne réponse était
              <span class="ref font-medium text-vert">{{ r.answer.join(', ') }}</span>.
            </p>
            <p class="text-[14px] leading-relaxed max-w-[62ch]">{{ texteReponse(r.question) }}</p>
          </li>
        </ul>
      </section>

      <section v-else class="pb-12">
        <p class="border-b border-line-soft py-5 text-[15px] text-vert font-medium">
          Aucune erreur sur ce niveau.
        </p>
      </section>
    </template>
  </div>
</template>
