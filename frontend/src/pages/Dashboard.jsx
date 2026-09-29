import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api/client.js'
import Loading from '../components/Loading.jsx'
import ErrorBanner from '../components/ErrorBanner.jsx'
import DifficultyBadge from '../components/DifficultyBadge.jsx'

export default function Dashboard() {
  const navigate = useNavigate()
  const [sessions, setSessions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [subject, setSubject] = useState('')
  const [difficulty, setDifficulty] = useState('beginner')
  const [creating, setCreating] = useState(false)

  async function loadSessions() {
    setLoading(true)
    setError('')
    try {
      setSessions(await api.listSessions())
    } catch (err) {
      setError(`Could not reach the backend: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadSessions()
  }, [])

  async function handleCreate(e) {
    e.preventDefault()
    if (!subject.trim()) return
    setCreating(true)
    setError('')
    try {
      const session = await api.createSession({ subject: subject.trim(), difficulty_level: difficulty })
      navigate(`/sessions/${session.id}`)
    } catch (err) {
      setError(err.message)
      setCreating(false)
    }
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">
          AI Study <span className="text-brand-500">Buddy</span>
        </h1>
        <p className="text-slate-500 mt-1">Your personalized AI tutor. Pick a subject and start learning.</p>
      </header>

      <form onSubmit={handleCreate} className="card mb-8 grid gap-4 sm:grid-cols-[1fr_200px_auto] items-end">
        <div>
          <label className="label">What are you studying?</label>
          <input
            className="input"
            placeholder="e.g. Data Structures, Organic Chemistry, World History"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
          />
        </div>
        <div>
          <label className="label">Level</label>
          <select className="input" value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        </div>
        <button className="btn-primary" disabled={creating || !subject.trim()}>
          {creating ? 'Creating...' : 'Start session'}
        </button>
      </form>

      <ErrorBanner message={error} onRetry={loadSessions} />

      <h2 className="text-lg font-semibold mt-6 mb-3">Your study sessions</h2>
      {loading ? (
        <Loading />
      ) : sessions.length === 0 ? (
        <div className="card text-center text-slate-500 py-10">
          No sessions yet. Create your first one above.
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {sessions.map((s) => (
            <Link key={s.id} to={`/sessions/${s.id}`} className="card hover:border-brand-500 transition-colors">
              <div className="flex items-start justify-between gap-2">
                <h3 className="font-semibold text-slate-900">{s.title || s.subject}</h3>
                <DifficultyBadge level={s.difficulty_level} />
              </div>
              <p className="text-sm text-slate-500 mt-1">{s.subject}</p>
              <p className="text-xs text-slate-400 mt-3">
                Last active {new Date(s.updated_at).toLocaleString()}
              </p>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
