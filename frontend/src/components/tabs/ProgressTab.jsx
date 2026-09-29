import { useEffect, useState } from 'react'
import { api } from '../../api/client.js'
import Loading from '../Loading.jsx'
import ErrorBanner from '../ErrorBanner.jsx'
import DifficultyBadge from '../DifficultyBadge.jsx'

function barColor(accuracy) {
  if (accuracy >= 80) return 'bg-green-500'
  if (accuracy >= 60) return 'bg-amber-500'
  return 'bg-red-500'
}

export default function ProgressTab({ sessionId }) {
  const [progress, setProgress] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.getProgress(sessionId).then(setProgress).catch((err) => setError(err.message))
  }, [sessionId])

  if (error) return <ErrorBanner message={error} />
  if (!progress) return <Loading />

  if (progress.total_quizzes_taken === 0) {
    return (
      <div className="card text-center text-slate-500 py-10">
        Take a quiz first — your progress, weak topics, and difficulty suggestions will show up here.
      </div>
    )
  }

  const changed = progress.suggested_difficulty && progress.suggested_difficulty !== progress.current_difficulty

  return (
    <div className="space-y-5">
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="card text-center">
          <p className="text-sm text-slate-500">Quizzes taken</p>
          <p className="text-3xl font-bold mt-1">{progress.total_quizzes_taken}</p>
        </div>
        <div className="card text-center">
          <p className="text-sm text-slate-500">Questions answered</p>
          <p className="text-3xl font-bold mt-1">{progress.total_questions_answered}</p>
        </div>
        <div className="card text-center">
          <p className="text-sm text-slate-500">Overall accuracy</p>
          <p className="text-3xl font-bold mt-1 text-brand-600">{progress.overall_accuracy}%</p>
        </div>
      </div>

      {changed && (
        <div className="card border-brand-500 bg-brand-50 flex items-center gap-3 flex-wrap">
          <span className="text-sm text-slate-700">Adaptive difficulty suggestion: try</span>
          <DifficultyBadge level={progress.suggested_difficulty} />
          <span className="text-sm text-slate-500">(you're currently on {progress.current_difficulty})</span>
        </div>
      )}

      {progress.weak_topics.length > 0 && (
        <div className="card border-amber-300 bg-amber-50">
          <p className="text-sm font-semibold text-amber-800 mb-2">Weak topics to focus on</p>
          <div className="flex flex-wrap gap-2">
            {progress.weak_topics.map((t) => (
              <span key={t} className="rounded-full bg-white border border-amber-300 text-amber-800 text-xs px-3 py-1">{t}</span>
            ))}
          </div>
        </div>
      )}

      <div className="card">
        <h3 className="font-semibold mb-4">Topic mastery</h3>
        <div className="space-y-3">
          {progress.topic_mastery.map((t) => (
            <div key={t.topic_tag}>
              <div className="flex justify-between text-sm mb-1">
                <span>{t.topic_tag}</span>
                <span className="text-slate-500">{t.accuracy}% ({t.correct}/{t.attempts})</span>
              </div>
              <div className="h-2.5 rounded-full bg-slate-100 overflow-hidden">
                <div className={`h-full rounded-full ${barColor(t.accuracy)}`} style={{ width: `${t.accuracy}%` }} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
