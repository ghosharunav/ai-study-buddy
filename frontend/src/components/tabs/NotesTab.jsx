import { useEffect, useState } from 'react'
import { api } from '../../api/client.js'
import Loading from '../Loading.jsx'
import ErrorBanner from '../ErrorBanner.jsx'
import DifficultyBadge from '../DifficultyBadge.jsx'

function NoteCard({ note }) {
  const c = note.content
  return (
    <div className="card space-y-4">
      <div className="flex items-start justify-between gap-2">
        <h3 className="text-lg font-semibold">{note.topic}</h3>
        <DifficultyBadge level={note.difficulty_level} />
      </div>
      <p className="text-slate-700">{c.summary}</p>

      <div>
        <h4 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-1">Key points</h4>
        <ul className="list-disc list-inside space-y-1 text-slate-700 text-sm">
          {c.key_points.map((p, i) => <li key={i}>{p}</li>)}
        </ul>
      </div>

      <div className="rounded-lg bg-brand-50 border border-brand-100 p-3">
        <h4 className="text-sm font-semibold text-brand-700 mb-1">Analogy</h4>
        <p className="text-sm text-slate-700">{c.analogy}</p>
      </div>

      {c.common_mistakes.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-1">Common mistakes</h4>
          <ul className="list-disc list-inside space-y-1 text-slate-700 text-sm">
            {c.common_mistakes.map((p, i) => <li key={i}>{p}</li>)}
          </ul>
        </div>
      )}

      {c.follow_up_questions.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-1">Keep exploring</h4>
          <ul className="list-disc list-inside space-y-1 text-slate-700 text-sm">
            {c.follow_up_questions.map((p, i) => <li key={i}>{p}</li>)}
          </ul>
        </div>
      )}
    </div>
  )
}

export default function NotesTab({ sessionId, session }) {
  const [notes, setNotes] = useState([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState('')
  const [topic, setTopic] = useState('')
  const [level, setLevel] = useState(session.difficulty_level)

  useEffect(() => {
    api.listNotes(sessionId)
      .then((n) => setNotes([...n].reverse()))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [sessionId])

  async function handleGenerate(e) {
    e.preventDefault()
    if (!topic.trim()) return
    setGenerating(true)
    setError('')
    try {
      const note = await api.explainTopic(sessionId, topic.trim(), level)
      setNotes((prev) => [note, ...prev])
      setTopic('')
    } catch (err) {
      setError(err.message)
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div className="space-y-5">
      <form onSubmit={handleGenerate} className="card grid gap-4 sm:grid-cols-[1fr_200px_auto] items-end">
        <div>
          <label className="label">Topic to explain</label>
          <input className="input" placeholder="e.g. Recursion" value={topic} onChange={(e) => setTopic(e.target.value)} />
        </div>
        <div>
          <label className="label">Explanation style</label>
          <select className="input" value={level} onChange={(e) => setLevel(e.target.value)}>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
            <option value="eli5">Explain like I'm 5</option>
          </select>
        </div>
        <button className="btn-primary" disabled={generating || !topic.trim()}>
          {generating ? 'Generating...' : 'Explain'}
        </button>
      </form>

      <ErrorBanner message={error} />
      {generating && <Loading label="Aria is writing your notes..." />}
      {loading ? <Loading /> : notes.map((n) => <NoteCard key={n.id} note={n} />)}
      {!loading && notes.length === 0 && !generating && (
        <p className="text-center text-slate-400 text-sm">No notes yet. Enter a topic above.</p>
      )}
    </div>
  )
}
