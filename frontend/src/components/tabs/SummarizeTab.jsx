import { useEffect, useState } from 'react'
import { api } from '../../api/client.js'
import Loading from '../Loading.jsx'
import ErrorBanner from '../ErrorBanner.jsx'

function SummaryCard({ summary }) {
  const c = summary.content
  return (
    <div className="card space-y-4">
      <h3 className="text-lg font-semibold">{c.title}</h3>
      <p className="text-slate-700">{c.overview}</p>
      <div>
        <h4 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-1">Key points</h4>
        <ul className="list-disc list-inside space-y-1 text-sm text-slate-700">
          {c.key_points.map((p, i) => <li key={i}>{p}</li>)}
        </ul>
      </div>
      {c.important_terms.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-1">Important terms</h4>
          <dl className="space-y-1 text-sm">
            {c.important_terms.map((t, i) => (
              <div key={i}><dt className="inline font-medium">{t.term}: </dt><dd className="inline text-slate-600">{t.definition}</dd></div>
            ))}
          </dl>
        </div>
      )}
      {c.suggested_next_steps.length > 0 && (
        <div className="rounded-lg bg-brand-50 border border-brand-100 p-3">
          <h4 className="text-sm font-semibold text-brand-700 mb-1">Suggested next steps</h4>
          <ul className="list-disc list-inside text-sm text-slate-700 space-y-1">
            {c.suggested_next_steps.map((p, i) => <li key={i}>{p}</li>)}
          </ul>
        </div>
      )}
    </div>
  )
}

export default function SummarizeTab({ sessionId, session }) {
  const [summaries, setSummaries] = useState([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState('')
  const [text, setText] = useState('')

  useEffect(() => {
    api.listSummaries(sessionId)
      .then((s) => setSummaries([...s].reverse()))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [sessionId])

  async function handleSummarize(e) {
    e.preventDefault()
    setGenerating(true)
    setError('')
    try {
      const summary = await api.summarize(sessionId, { text, difficulty_level: session.difficulty_level })
      setSummaries((prev) => [summary, ...prev])
      setText('')
    } catch (err) {
      setError(err.message)
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div className="space-y-4">
      <form onSubmit={handleSummarize} className="card space-y-3">
        <label className="label">Paste lecture notes or a textbook excerpt (at least 50 characters)</label>
        <textarea
          className="input min-h-[160px]"
          placeholder="Paste your study material here. Long text is automatically chunked and summarized in parts."
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-400">{text.length.toLocaleString()} characters</span>
          <button className="btn-primary" disabled={generating || text.trim().length < 50}>
            {generating ? 'Summarizing...' : 'Summarize'}
          </button>
        </div>
      </form>

      <ErrorBanner message={error} />
      {generating && <Loading label="Reading and summarizing your material..." />}
      {loading ? <Loading /> : summaries.map((s) => <SummaryCard key={s.id} summary={s} />)}
    </div>
  )
}
