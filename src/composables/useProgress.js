import { reactive, watch } from 'vue'
import { categories, levelsOf } from '../data'

const CLE = 'permis-qcm:progression:v1'

function charger() {
  try {
    const brut = localStorage.getItem(CLE)
    return brut ? JSON.parse(brut) : {}
  } catch {
    // Navigation privee ou stockage refuse : on repart d'une progression vide.
    return {}
  }
}

const state = reactive({ niveaux: charger() })

watch(
  state,
  (v) => {
    try {
      localStorage.setItem(CLE, JSON.stringify(v.niveaux))
    } catch {
      /* stockage indisponible : la progression reste en memoire */
    }
  },
  { deep: true },
)

function cle(catId, levelIndex) {
  return `${catId}:${levelIndex}`
}

export function useProgress() {
  function getNiveau(catId, levelIndex) {
    return state.niveaux[cle(catId, levelIndex)] ?? null
  }

  function enregistrer(catId, levelIndex, score, total) {
    const k = cle(catId, levelIndex)
    const ancien = state.niveaux[k]
    if (!ancien || score > ancien.best) {
      state.niveaux[k] = { best: score, total }
    }
  }

  /** Bilan d'une categorie : niveaux termines, questions reussies au mieux. */
  function bilanCategorie(category) {
    const niveaux = levelsOf(category)
    let termines = 0
    let reussies = 0
    let vues = 0
    for (const n of niveaux) {
      const p = getNiveau(category.id, n.index)
      if (p) {
        termines += 1
        reussies += p.best
        vues += p.total
      }
    }
    return {
      niveaux: niveaux.length,
      termines,
      reussies,
      vues,
      termine: termines === niveaux.length,
    }
  }

  function bilanGlobal() {
    let niveauxTotal = 0
    let niveauxTermines = 0
    let reussies = 0
    let vues = 0
    for (const c of categories) {
      const b = bilanCategorie(c)
      niveauxTotal += b.niveaux
      niveauxTermines += b.termines
      reussies += b.reussies
      vues += b.vues
    }
    return { niveauxTotal, niveauxTermines, reussies, vues }
  }

  function reinitialiser() {
    state.niveaux = {}
  }

  return { state, getNiveau, enregistrer, bilanCategorie, bilanGlobal, reinitialiser }
}
