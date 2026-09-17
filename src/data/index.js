import brut from './questions.json'

export const meta = brut.meta
export const categories = brut.categories
export const LEVEL_SIZE = brut.meta.levelSize

export function getCategory(id) {
  return categories.find((c) => c.id === id) ?? null
}

/** Panneau de signalisation associé à chaque chapitre (voir SignGlyph.vue). */
const GLYPHES = {
  signalisation: 'danger',
  priorites: 'yield',
  'arret-stationnement': 'interdit',
  'route-autoroute': 'autoroute',
  'infractions-secourisme': 'secours',
  'permis-a': 'moto',
  'permis-b': 'voiture',
  'permis-c': 'camion',
  'permis-d': 'bus',
  equipement: 'cle',
}

export function glyphOf(category) {
  return GLYPHES[category.id] ?? 'danger'
}

/** Decoupe une categorie en niveaux successifs de LEVEL_SIZE questions. */
export function levelsOf(category) {
  const niveaux = []
  for (let i = 0; i < category.questions.length; i += LEVEL_SIZE) {
    niveaux.push({
      index: niveaux.length,
      questions: category.questions.slice(i, i + LEVEL_SIZE),
    })
  }
  return niveaux
}

export function getLevel(category, index) {
  return levelsOf(category)[index] ?? null
}

/** Compare deux ensembles de lettres, sans tenir compte de l'ordre. */
export function isCorrect(selected, answer) {
  if (selected.length !== answer.length) return false
  const a = [...selected].sort().join('')
  const b = [...answer].sort().join('')
  return a === b
}

/** Note sur 20, selon l'usage scolaire francophone. */
export function noteSur20(score, total) {
  if (!total) return 0
  return Math.round((score / total) * 20 * 10) / 10
}

/** Accorde un nom avec son nombre : « 1 bonne réponse », « 3 bonnes réponses ». */
export function accorder(n, singulier, pluriel) {
  return `${n} ${n > 1 ? pluriel : singulier}`
}

export function appreciation(note) {
  if (note >= 18) return 'Excellent'
  if (note >= 16) return 'Très bien'
  if (note >= 14) return 'Bien'
  if (note >= 12) return 'Assez bien'
  if (note >= 10) return 'Passable'
  if (note >= 8) return 'Insuffisant'
  return 'Faible'
}
