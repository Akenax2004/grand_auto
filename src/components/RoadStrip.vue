<script setup>
/**
 * Dispositif de progression : un tronçon de chaussée.
 * Chaque question (ou niveau) est un catadioptre planté sur la voie.
 * C'est l'élément expressif du site ; le reste reste sobre.
 */
const props = defineProps({
  total: { type: Number, required: true },
  marks: { type: Array, default: () => [] }, // 'ok' | 'ko' | 'missed' | null, par question
  current: { type: Number, default: -1 },
  compact: { type: Boolean, default: false },
})

function etat(i) {
  if (props.current === i) return 'current'
  return props.marks[i] ?? 'idle'
}

const CLASSES = {
  ok: 'stud--ok',
  ko: 'stud--ko',
  missed: 'stud--missed',
  current: 'stud--current',
  idle: 'stud--idle',
}
</script>

<template>
  <div class="relative" :class="compact ? 'py-1' : 'py-1.5'">
    <!-- La chaussée et sa ligne axiale -->
    <div
      class="road rounded-full"
      :class="compact ? 'h-[10px]' : 'h-[14px]'"
      aria-hidden="true"
    ></div>

    <!-- Les catadioptres -->
    <div
      class="absolute inset-y-0 left-[6px] right-[6px] flex items-center justify-between"
      aria-hidden="true"
    >
      <span
        v-for="i in total"
        :key="i"
        class="stud rounded-[3px]"
        :class="[compact ? 'w-[5px] h-[13px]' : 'w-[7px] h-[22px]', CLASSES[etat(i - 1)]]"
      ></span>
    </div>
  </div>
</template>
