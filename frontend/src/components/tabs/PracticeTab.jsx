import { useState } from 'react'
import { api } from '../../api/client.js'
import Loading from '../Loading.jsx'
import ErrorBanner from '../ErrorBanner.jsx'

function PracticeQuestion({ setId, index, question }) {
  const [answer, setAnswer] = useState('')
  const [feedback, setFeedback] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showChecklist, setShowChecklist] = useState(false)

  async function handleSubmit() {
    setLoading(true)
    setError('')
    try {
      setFeedback(await api.submitPracticeAnswer(setId, index, answer.trim()))
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card space-y-3">
      <p className="font-medium">{index + 1}. {question.question}</p>
      <textarea
        className="input min-h-[100px]"
        placeholder="Write your answer here..."
        value={answer}
        onChange={(e) => setAnswer(e.target.value)}
      />
      <div className="flex items-center gap-3 flex-wrap">
        <button className="btn-primary" disabled={loading || !answer.trim()} onClick={handleSubmit}>
          {loading ? 'Checking...' : 'Get feedback'}
        </button>
        <button className="text-sm text-slate-500 underline" onClick={() => setShowChecklist((s) => !s)}>
          {showChecklist ? 'Hide' : 'Show'} self-check checklist
        </button>
      </div>

      {showChecklist && (
        <ul className="list-disc list-inside text-sm text-slate-600 bg-slate-50 rounded-lg p-3 space-y-1">
          {question.ideal_answer_points.map((p, i) => <li key={i}>{p}</li>)}
        </ul>
      )}

      <ErrorBanner message={error} />

      {feedback && (
        <div className="rounded-lg border border-brand-100 bg-brand-50 p-4 space-y-3">
          <p className="text-sm font-semibold text-brand-700">Score estimate: {feedback.score_estimate}/100</p>
          <p className="text-sm text-slate-700">{feedback.overall_feedback}</p>
          {feedback.covered_points.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-green-700 uppercase mb-1">You covered</p>
              <ul className="list-disc list-inside text-sm text-slate-700">
                {feedback.covered_points.map((p, i) => <li key={i}>{p}</li>)}
              </ul>
            </div>
          )}
          {feedback.missed_points.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-red-700 uppercase mb-1">You missed</p>
              <ul className="list-disc list-inside text-sm text-slate-700">
                {feedback.missed_points.map((p, i) => <li key={i}>{p}</li>)}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default function PracticeTab({ sessionId, session }) {
  const [topic, setTopic] = useState('')
  const [level, setLevel] = useState(session.difficulty_level)
  const [count, setCount] = useState(3)
  const [pset, setPset] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleGenerate(e) {
    e.preventDefault()
    if (!topic.trim()) return
    setLoading(true)
    setError('')
    try {
      setPset(await api.generatePractice(sessionId, {
        topic: topic.trim(), difficulty_level: level, num_questions: Number(count),
      }))
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <form onSubmit={handleGenerate} className="card grid gap-4 sm:grid-cols-[1fr_160px_120px_auto] items-end">
        <div>
          <label className="label">Practice topic</label>
          <input className="input" placeholder="e.g. Recursion" value={topic} onChange={(e) => setTopic(e.target.value)} />
        </div>
        <div>
          <label className="label">Difficulty</label>
          <select className="input" value={level} onChange={(e) => setLevel(e.target.value)}>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        </div>
        <div>
          <label className="label">Questions</label>
          <input className="input" type="number" min="1" max="10" value={count} onChange={(e) => setCount(e.target.value)} />
        </div>
        <button className="btn-primary" disabled={loading || !topic.trim()}>
          {loading ? 'Generating...' : 'Generate'}
        </button>
      </form>

      <ErrorBanner message={error} />
      {loading && <Loading label="Writing practice questions..." />}
      {pset && pset.questions.map((q, i) => (
        <PracticeQuestion key={`${pset.id}-${i}`} setId={pset.id} index={i} question={q} />
      ))}
    </div>
  )
}
