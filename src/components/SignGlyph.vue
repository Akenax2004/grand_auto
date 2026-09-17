<script setup>
/**
 * Glyphe de signalisation d'un chapitre.
 * Chaque chapitre du manuel est identifié par le panneau qui lui correspond
 * dans le langage de la route : les chapitres réglementaires portent un
 * panneau à liseré rouge (danger, cédez-le-passage, interdiction), les
 * chapitres « véhicules / permis / équipement » un panneau vert à pictogramme.
 */
const props = defineProps({
  kind: { type: String, required: true },
})

const LABELS = {
  danger: 'Panneau de danger',
  yield: 'Cédez-le-passage',
  interdit: 'Interdiction',
  autoroute: 'Route pour automobile et autoroute',
  secours: 'Premiers secours',
  moto: 'Cyclomoteur et motocyclette',
  voiture: 'Voiture',
  camion: 'Camion',
  bus: 'Bus',
  cle: 'Équipement et entretien',
}

const C = {
  vert: '#0b6a3c',
  rouge: '#c41430',
  encre: '#16191c',
  blanc: '#ffffff',
}
</script>

<template>
  <svg
    viewBox="0 0 40 40"
    class="block"
    role="img"
    :aria-label="LABELS[kind] ?? 'Panneau de signalisation'"
    fill="none"
  >
    <title>{{ LABELS[kind] ?? 'Panneau de signalisation' }}</title>

    <!-- Danger : triangle -->
    <template v-if="kind === 'danger'">
      <path
        d="M20 4.5 L36 33.5 H4 Z"
        :stroke="C.rouge"
        stroke-width="2.6"
        stroke-linejoin="round"
        fill="#fff"
      />
      <path d="M20 12 v9.5" :stroke="C.encre" stroke-width="3.2" stroke-linecap="round" />
      <circle cx="20" cy="27.5" r="1.9" :fill="C.encre" />
    </template>

    <!-- Cédez-le-passage : triangle inversé -->
    <template v-else-if="kind === 'yield'">
      <path
        d="M20 34.5 L36 6 H4 Z"
        :stroke="C.rouge"
        stroke-width="2.6"
        stroke-linejoin="round"
        fill="#fff"
      />
    </template>

    <!-- Interdiction : cercle barré -->
    <template v-else-if="kind === 'interdit'">
      <circle cx="20" cy="20" r="14.5" :stroke="C.rouge" stroke-width="2.6" fill="#fff" />
      <path d="M10.5 29.5 L29.5 10.5" :stroke="C.rouge" stroke-width="2.6" stroke-linecap="round" />
    </template>

    <!-- Route pour automobile / autoroute : chaussées séparées -->
    <template v-else-if="kind === 'autoroute'">
      <rect x="5" y="6" width="30" height="28" rx="3.5" :fill="C.vert" />
      <path d="M8.5 15.5 H31.5 M8.5 24.5 H31.5" :stroke="C.blanc" stroke-width="3" stroke-linecap="round" />
      <path d="M11 20 h5 M17.5 20 h5 M24 20 h5" :stroke="C.blanc" stroke-width="2.6" stroke-linecap="round" />
    </template>

    <!-- Secourisme : croix blanche -->
    <template v-else-if="kind === 'secours'">
      <rect x="5" y="6" width="30" height="28" rx="3.5" :fill="C.vert" />
      <path
        d="M17 11.5 h6 v5.5 h5.5 v6 H23 v5.5 h-6 V23 h-5.5 v-6 H17 Z"
        :fill="C.blanc"
      />
    </template>

    <!-- Cyclomoteur / motocyclette -->
    <template v-else-if="kind === 'moto'">
      <rect x="5" y="6" width="30" height="28" rx="3.5" :fill="C.vert" />
      <circle cx="11" cy="27.5" r="3.5" :stroke="C.blanc" stroke-width="2.4" />
      <circle cx="29" cy="27.5" r="3.5" :stroke="C.blanc" stroke-width="2.4" />
      <path
        d="M11 27.5 L14.5 20 H20 L29 27.5"
        :stroke="C.blanc"
        stroke-width="2.4"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path d="M29 27.5 V21 H24" :stroke="C.blanc" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" />
    </template>

    <!-- Voiture -->
    <template v-else-if="kind === 'voiture'">
      <rect x="5" y="6" width="30" height="28" rx="3.5" :fill="C.vert" />
      <rect x="6.5" y="21.5" width="27" height="8" rx="4" :fill="C.blanc" />
      <path
        d="M13.5 21.5 v-3 a4 4 0 0 1 4-4 h5 a4 4 0 0 1 4 4 v3 Z"
        :fill="C.blanc"
      />
      <circle cx="14" cy="26.5" r="3.1" :fill="C.vert" />
      <circle cx="26" cy="26.5" r="3.1" :fill="C.vert" />
    </template>

    <!-- Camion -->
    <template v-else-if="kind === 'camion'">
      <rect x="5" y="6" width="30" height="28" rx="3.5" :fill="C.vert" />
      <rect x="20" y="12" width="14" height="14.5" rx="2" :fill="C.blanc" />
      <path d="M6 21.5 h8 l1.6-3 h4.4 v8 h-14 Z" :fill="C.blanc" />
      <circle cx="12" cy="27" r="3" :fill="C.vert" />
      <circle cx="27" cy="27" r="3" :fill="C.vert" />
    </template>

    <!-- Bus -->
    <template v-else-if="kind === 'bus'">
      <rect x="5" y="6" width="30" height="28" rx="3.5" :fill="C.vert" />
      <rect x="7" y="12.5" width="26" height="14" rx="2.5" :fill="C.blanc" />
      <rect x="9.5" y="15" width="12" height="5" rx="1" :fill="C.vert" />
      <rect x="24" y="15" width="6.5" height="5" rx="1" :fill="C.vert" />
      <circle cx="14" cy="27" r="3.1" :fill="C.vert" />
      <circle cx="26" cy="27" r="3.1" :fill="C.vert" />
    </template>

    <!-- Équipement / entretien : engrenage -->
    <template v-else>
      <rect x="5" y="6" width="30" height="28" rx="3.5" :fill="C.vert" />
      <g :stroke="C.blanc" stroke-width="2.8" stroke-linecap="round">
        <line x1="20" y1="9.5" x2="20" y2="12.5" />
        <line x1="20" y1="27.5" x2="20" y2="30.5" />
        <line x1="9.5" y1="20" x2="12.5" y2="20" />
        <line x1="27.5" y1="20" x2="30.5" y2="20" />
        <line x1="12.6" y1="12.6" x2="14.7" y2="14.7" />
        <line x1="25.3" y1="25.3" x2="27.4" y2="27.4" />
        <line x1="27.4" y1="12.6" x2="25.3" y2="14.7" />
        <line x1="14.7" y1="25.3" x2="12.6" y2="27.4" />
      </g>
      <circle cx="20" cy="20" r="7.2" :stroke="C.blanc" stroke-width="2.8" />
      <circle cx="20" cy="20" r="2.2" :fill="C.blanc" />
    </template>
  </svg>
</template>
