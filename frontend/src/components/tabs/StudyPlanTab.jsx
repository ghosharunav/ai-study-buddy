import { useEffect, useState } from 'react'
import { api } from '../../api/client.js'
import Loading from '../Loading.jsx'
import ErrorBanner from '../ErrorBanner.jsx'

function PlanCard({ plan }) {
  return (
    <div className="card space-y-4">
      <h3 className="text-lg font-semibold">{plan.goal}</h3>
      <div className="space-y-3">
        {plan.days.map((d) => (
          <div key={d.day_number} className="rounded-lg border border-slate-200 p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold text-brand-600">Day {d.day_number}</span>
              <span className="text-xs text-slate-500">~{d.estimated_minutes} min</span>
            </div>
            <p className="text-sm text-slate-500 mb-2">Focus: {d.focus_topics.join(', ')}</p>
            <ul className="list-disc list-inside text-sm text-slate-700 space-y-1">
              {d.activities.map((a, i) => <li key={i}>{a}</li>)}
            </ul>
          </div>
        ))}
      </div>
    </div>
  )
}

export default function StudyPlanTab({ sessionId }) {
  const [plans, setPlans] = useState([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState('')
  const [goal, setGoal] = useState('')
  const [days, setDays] = useState(7)

  useEffect(() => {
    api.listStudyPlans(sessionId)
      .then((p) => setPlans([...p].reverse()))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [sessionId])

  async function handleGenerate(e) {
    e.preventDefault()
    if (!goal.trim()) return
    setGenerating(true)
    setError('')
    try {
      const plan = await api.generateStudyPlan(sessionId, { goal: goal.trim(), num_days: Number(days) })
      setPlans((prev) => [plan, ...prev])
      setGoal('')
    } catch (err) {
      setError(err.message)
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div className="space-y-4">
      <form onSubmit={handleGenerate} className="card space-y-3">
        <div className="grid gap-4 sm:grid-cols-[1fr_120px] items-end">
          <div>
            <label className="label">What's your goal?</label>
            <input className="input" placeholder="e.g. Pass my midterm next week" value={goal} onChange={(e) => setGoal(e.target.value)} />
          </div>
          <div>
            <label className="label">Days</label>
            <input className="input" type="number" min="1" max="14" value={days} onChange={(e) => setDays(e.target.value)} />
          </div>
        </div>
        <p className="text-xs text-slate-400">
          Your plan automatically prioritizes weak topics detected from your quiz results.
        </p>
        <button className="btn-primary" disabled={generating || !goal.trim()}>
          {generating ? 'Building plan...' : 'Generate my study plan'}
        </button>
      </form>

      <ErrorBanner message={error} />
      {generating && <Loading label="Personalizing your plan..." />}
      {loading ? <Loading /> : plans.map((p) => <PlanCard key={p.id} plan={p} />)}
    </div>
  )
}
