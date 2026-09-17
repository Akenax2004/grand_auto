<script setup>
const props = defineProps({
  letter: { type: String, required: true },
  text: { type: String, default: '' },
  illustrative: { type: Boolean, default: false },
  selected: { type: Boolean, default: false },
  /** null tant que la question n'est pas corrigée */
  verdict: { type: String, default: null }, // 'correct' | 'wrong' | 'missed'
  locked: { type: Boolean, default: false },
})

defineEmits(['toggle'])
</script>

<template>
  <button
    type="button"
    :disabled="locked"
    :aria-pressed="selected"
    class="group w-full text-left flex items-center gap-3.5 rounded-lg border px-4 py-3.5 transition-colors duration-150"
    :class="[
      verdict === 'correct' && 'border-vert bg-vert-wash',
      verdict === 'wrong' && 'border-rouge bg-rouge-wash',
      verdict === 'missed' && 'border-vert border-dashed bg-vert-wash/70',
      !verdict && selected && 'border-vert bg-vert-wash',
      !verdict && !selected && 'border-line bg-papier',
      !verdict && !locked && !selected && 'hover:border-encre-faint',
      locked && !verdict && 'opacity-50',
      locked ? 'cursor-default' : 'cursor-pointer',
    ]"
    @click="$emit('toggle', letter)"
  >
    <!-- Médaillon : lettre d'option, en cercle comme un panneau d'obligation -->
    <span
      class="ref shrink-0 w-7 h-7 grid place-items-center rounded-full border text-[13px] font-semibold uppercase transition-colors duration-150"
      :class="[
        verdict === 'correct' && 'border-vert bg-vert text-papier',
        verdict === 'wrong' && 'border-rouge bg-rouge text-papier',
        verdict === 'missed' && 'border-vert text-vert',
        !verdict && selected && 'border-vert bg-vert text-papier',
        !verdict && !selected && 'border-line text-encre-soft group-hover:border-encre-faint',
      ]"
      >{{ letter }}</span
    >

    <span class="flex-1 text-[15px] leading-relaxed pt-0.5">
      <template v-if="text">{{ text }}</template>
      <template v-else-if="illustrative">
        <span class="text-encre-soft italic">
          Option illustrée dans le manuel (image non reproduite ici).
        </span>
      </template>
    </span>

    <!-- Verdict : icône non colorée seule, pour la lisibilité -->
    <span v-if="verdict === 'correct'" class="shrink-0 text-vert" aria-hidden="true">
      <svg
        viewBox="0 0 16 16"
        class="w-4 h-4"
        fill="none"
        stroke="currentColor"
        stroke-width="2.4"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M3 8.5 L6.5 12 L13 4.5" />
      </svg>
    </span>
    <span v-else-if="verdict === 'wrong'" class="shrink-0 text-rouge" aria-hidden="true">
      <svg
        viewBox="0 0 16 16"
        class="w-4 h-4"
        fill="none"
        stroke="currentColor"
        stroke-width="2.4"
        stroke-linecap="round"
      >
        <path d="M4 4 L12 12 M12 4 L4 12" />
      </svg>
    </span>
  </button>
</template>
