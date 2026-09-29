import { useEffect, useState } from 'react'
import { api } from '../../api/client.js'
import Loading from '../Loading.jsx'
import ErrorBanner from '../ErrorBanner.jsx'

function FlashcardDeck({ fset }) {
  const [index, setIndex] = useState(0)
  const [flipped, setFlipped] = useState(false)
  const card = fset.cards[index]

  function go(delta) {
    setFlipped(false)
    setIndex((i) => (i + delta + fset.cards.length) % fset.cards.length)
  }

  return (
    <div className="card space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">{fset.topic}</h3>
        <span className="text-sm text-slate-500">{index + 1} / {fset.cards.length}</span>
      </div>

      <button
        onClick={() => setFlipped((f) => !f)}
        className={`w-full min-h-[180px] rounded-xl border-2 p-6 text-center flex flex-col items-center justify-center transition-colors ${
          flipped ? 'bg-brand-50 border-brand-500' : 'bg-white border-slate-200 hover:border-brand-500'
        }`}
      >
        <span className="text-xs uppercase tracking-wide text-slate-400 mb-2">{flipped ? 'Answer' : 'Question'}</span>
        <span className="text-lg font-medium">{flipped ? card.back : card.front}</span>
        <span className="text-xs text-slate-400 mt-3">Click to flip</span>
      </button>

      <div className="flex justify-between">
        <button className="btn-secondary" onClick={() => go(-1)}>Previous</button>
        <button className="btn-secondary" onClick={() => go(1)}>Next</button>
      </div>
    </div>
  )
}

export default function FlashcardsTab({ sessionId, session }) {
  const [sets, setSets] = useState([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState('')
  const [topic, setTopic] = useState('')
  const [count, setCount] = useState(10)

  useEffect(() => {
    api.listFlashcardSets(sessionId)
      .then((s) => setSets([...s].reverse()))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [sessionId])

  async function handleGenerate(e) {
    e.preventDefault()
    if (!topic.trim()) return
    setGenerating(true)
    setError('')
    try {
      const fset = await api.generateFlashcards(sessionId, {
        topic: topic.trim(), difficulty_level: session.difficulty_level, num_cards: Number(count),
      })
      setSets((prev) => [fset, ...prev])
      setTopic('')
    } catch (err) {
      setError(err.message)
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div className="space-y-4">
      <form onSubmit={handleGenerate} className="card grid gap-4 sm:grid-cols-[1fr_120px_auto] items-end">
        <div>
          <label className="label">Flashcard topic</label>
          <input className="input" placeholder="e.g. Sorting algorithms" value={topic} onChange={(e) => setTopic(e.target.value)} />
        </div>
        <div>
          <label className="label">Cards</label>
          <input className="input" type="number" min="1" max="20" value={count} onChange={(e) => setCount(e.target.value)} />
        </div>
        <button className="btn-primary" disabled={generating || !topic.trim()}>
          {generating ? 'Generating...' : 'Generate'}
        </button>
      </form>

      <ErrorBanner message={error} />
      {generating && <Loading label="Making flashcards..." />}
      {loading ? <Loading /> : sets.map((s) => <FlashcardDeck key={s.id} fset={s} />)}
      {!loading && sets.length === 0 && !generating && (
        <p className="text-center text-slate-400 text-sm">No flashcards yet.</p>
      )}
    </div>
  )
}
