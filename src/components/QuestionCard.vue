<script setup>
import OptionRow from './OptionRow.vue'
import { computed } from 'vue'

const props = defineProps({
  question: { type: Object, required: true },
  selected: { type: Array, default: () => [] },
  locked: { type: Boolean, default: false },
})

defineEmits(['toggle'])

/** Une fois la question corrigée, on annote chaque option. */
const verdicts = computed(() => {
  if (!props.locked) return {}
  const attendues = new Set(props.question.answer)
  const choisies = new Set(props.selected)
  const out = {}
  for (const o of props.question.options) {
    if (attendues.has(o.letter) && choisies.has(o.letter)) out[o.letter] = 'correct'
    else if (attendues.has(o.letter)) out[o.letter] = 'missed'
    else if (choisies.has(o.letter)) out[o.letter] = 'wrong'
  }
  return out
})
</script>

<template>
  <article class="rounded-xl overflow-hidden border border-line bg-papier">
    <!-- Bandeau vert « panneau » : identifie la question -->
    <header
      class="flex flex-wrap items-center gap-x-3 gap-y-2 px-5 sm:px-7 py-3 bg-vert text-papier"
    >
      <p class="ref text-[13px] font-medium text-papier/90">
        Question n°{{ question.num }}
      </p>

      <span
        v-if="question.visual"
        class="text-[11px] px-2 py-0.5 border border-papier/30 text-papier/85"
        title="Cette question renvoie à une illustration du manuel."
      >
        renvoie à une illustration
      </span>

      <span
        v-if="question.corrected"
        class="text-[11px] px-2 py-0.5 border border-jaune text-jaune"
        :title="question.note"
      >
        réponse redressée
      </span>
    </header>

    <div class="px-5 sm:px-7 py-6">
      <h2 class="text-[20px] sm:text-[23px] font-bold tracking-[-0.012em] leading-snug max-w-[62ch]">
        {{ question.text }}
      </h2>

      <div class="mt-6 flex flex-col gap-2">
        <OptionRow
          v-for="o in question.options"
          :key="o.letter"
          :letter="o.letter"
          :text="o.text"
          :illustrative="question.visualOptions"
          :selected="selected.includes(o.letter)"
          :verdict="verdicts[o.letter] ?? null"
          :locked="locked"
          @toggle="$emit('toggle', $event)"
        />
      </div>
    </div>
  </article>
</template>
