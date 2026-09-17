/**
 * Verification de bout en bout du parcours candidat.
 * Pilote Chrome (deja installe) pour traverser un niveau et capturer
 * l'ecran de score. Script de developpement, non livre avec le site.
 *
 *   node scripts/verifier.mjs [url]
 */
import puppeteer from 'puppeteer-core'
import { mkdirSync } from 'node:fs'

const BASE = process.argv[2] ?? 'http://localhost:5174'
const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe'
const DOSSIER = '.shots'
mkdirSync(DOSSIER, { recursive: true })

const navigateur = await puppeteer.launch({
  executablePath: CHROME,
  headless: true,
  args: ['--hide-scrollbars'],
})

const page = await navigateur.newPage()
const erreurs = []
page.on('pageerror', (e) => erreurs.push(`pageerror: ${e.message}`))
page.on('console', (m) => {
  if (m.type() === 'error') erreurs.push(`console: ${m.text()}`)
})

const pause = (ms) => new Promise((r) => setTimeout(r, ms))

/** Navigue puis attend qu'un texte soit rendu : entre deux routes, seul le
 *  hash change et Vue re-rend sans rechargement, donc networkidle0 ne suffit pas. */
async function aller(hash, texteAttendu) {
  await page.goto(`${BASE}/#${hash}`, { waitUntil: 'networkidle0' })
  await page.waitForFunction(
    (t) => document.body.innerText.includes(t),
    { timeout: 8000 },
    texteAttendu,
  )
}

// ---------------------------------------------------------------- accueil
await page.setViewport({ width: 1280, height: 1150 })
await aller('/', 'Choisissez une catégorie')

const categories = await page.$$eval('ul li a', (as) =>
  as.map((a) => a.textContent.replace(/\s+/g, ' ').trim()),
)
console.log(`Accueil : ${categories.length} categories listees`)
if (categories.length !== 10) throw new Error('Attendu 10 categories')

const total = await page.$eval('header p:last-child', (p) => p.textContent.trim())
console.log(`En-tete : ${total}`)

// ------------------------------------------------------- traversee d'un niveau
await aller('/c/signalisation', 'Les niveaux')
const niveaux = await page.$$eval('ul li a', (as) => as.length)
console.log(`Signalisation : ${niveaux} niveaux proposes`)
if (niveaux !== 21) throw new Error(`Attendu 21 niveaux, obtenu ${niveaux}`)
await page.screenshot({ path: `${DOSSIER}/cat.png` })

await aller('/c/signalisation/n/0', 'Question 1 sur 10')
await page.waitForSelector('article button[aria-pressed]', { timeout: 8000 })

async function cliquerSur(texte) {
  for (const b of await page.$$('button')) {
    const t = await b.evaluate((el) => el.textContent.trim())
    if (t === texte) {
      await b.click()
      return true
    }
  }
  return false
}

/** Repond a chaque question en cochant l'option voulue puis Valider.
 *  Compte les verdicts affiches pour les confronter au score final. */
async function jouer(choix) {
  let justes = 0
  for (let i = 0; i < 10; i++) {
    // Le rang de la question affiche fait foi : il n'y a pas de rechargement
    // de page entre deux questions, seulement un rendu Vue.
    await page.waitForFunction(
      (n) => document.body.innerText.includes(`Question ${n} sur 10`),
      { timeout: 8000 },
      i + 1,
    )

    const options = await page.$$('article button[aria-pressed]')
    if (!options.length) throw new Error(`Question ${i + 1} : aucune option rendue`)
    await options[choix(i, options.length)].click()

    await page.waitForFunction(
      () => [...document.querySelectorAll('button')].some((b) => b.textContent.trim() === 'Valider'),
      { timeout: 5000 },
    )
    if (!(await cliquerSur('Valider'))) throw new Error(`Question ${i + 1} : bouton Valider absent`)

    await page.waitForFunction(
      () =>
        [...document.querySelectorAll('button')].some(
          (b) => ['Question suivante', 'Voir ma note'].includes(b.textContent.trim()),
        ),
      { timeout: 5000 },
    )

    // Verdict rendu par l'application pour cette question
    const verdict = await page.evaluate(() => {
      const p = [...document.querySelectorAll('p')].find((el) =>
        /^Réponse (juste|fausse)/.test(el.textContent.trim()),
      )
      return p ? p.textContent.trim() : null
    })
    if (verdict?.startsWith('Réponse juste')) justes += 1

    const dernier = i === 9
    await cliquerSur(dernier ? 'Voir ma note' : 'Question suivante')
  }
  return justes
}

// Repartit les choix pour obtenir un melange de bonnes et de mauvaises
// reponses ; le score affiche doit correspondre aux verdicts observes.
const justesAttendus = await jouer((i) => (i % 3 === 0 ? 0 : i % 2))
await pause(1400) // laisse l'animation de note se terminer

// La note est le seul paragraphe au corps de 64px ; on le cible par sa classe
// d'aspect pour ne pas dependre d'un ordre de noeuds.
const noteTexte = await page.$eval('.note-in p[class*="text-[64px]"]', (p) =>
  p.textContent.replace(/\s+/g, '').trim(),
)
const note = Number(noteTexte.split('/')[0])
const verdict = await page.$eval('.note-in p.text-\\[19px\\]', (p) => p.textContent.trim())
const detail = await page.$eval('.note-in p.text-\\[14px\\]', (p) =>
  p.textContent.replace(/\s+/g, ' ').trim(),
)
console.log(`Score : ${noteTexte} (${verdict}), ${detail}`)

const ratees = await page.$$eval('.border-b.border-line-soft.py-5', (els) => els.length)
console.log(`Relecture : ${ratees} question(s) a revoir`)

// Coherence : le score affiche doit egaler les verdicts « juste » observes,
// et la note sur 20 doit en decouler.
const scoreAffiche = Number(detail.match(/^(\d+)/)?.[1])
if (scoreAffiche !== justesAttendus) {
  throw new Error(`Score incoherent : ${scoreAffiche} affiche, ${justesAttendus} verdicts justes`)
}
if (Number(note) !== Math.round((justesAttendus / 10) * 20 * 10) / 10) {
  throw new Error(`Note sur 20 incoherente : ${note} pour ${justesAttendus}/10`)
}
if (ratees !== 10 - justesAttendus) {
  throw new Error(`Relecture incoherente : ${ratees} ratees pour ${justesAttendus} justes`)
}
console.log('Coherence score / verdicts / relecture : OK')

await page.screenshot({ path: `${DOSSIER}/score.png`, fullPage: true })

// -------------------------------------------------- persistance de la note
await aller('/c/signalisation', 'Les niveaux')
const ligne = await page.$eval('ul li a', (a) => a.textContent.replace(/\s+/g, ' ').trim())
console.log(`Retour categorie : ${ligne}`)

// --------------------------------------------------- affichage mobile 400px
await page.setViewport({ width: 400, height: 900 })
await aller('/c/signalisation/n/1', 'Question 1 sur 10')
const debordement = await page.evaluate(
  () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
)
console.log(`Debordement horizontal en 400px : ${debordement}px`)
await page.screenshot({ path: `${DOSSIER}/mobile.png` })

await navigateur.close()

if (erreurs.length) {
  console.log('\nERREURS CONSOLE :')
  for (const e of erreurs) console.log('  -', e)
  process.exit(1)
}
console.log('\nParcours complet verifie, aucune erreur console.')
