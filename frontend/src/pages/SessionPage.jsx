import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api/client.js'
import Loading from '../components/Loading.jsx'
import ErrorBanner from '../components/ErrorBanner.jsx'
import DifficultyBadge from '../components/DifficultyBadge.jsx'

import ChatTab from '../components/tabs/ChatTab.jsx'
import NotesTab from '../components/tabs/NotesTab.jsx'
import QuizTab from '../components/tabs/QuizTab.jsx'
import PracticeTab from '../components/tabs/PracticeTab.jsx'
import SummarizeTab from '../components/tabs/SummarizeTab.jsx'
import FlashcardsTab from '../components/tabs/FlashcardsTab.jsx'
import MaterialsTab from '../components/tabs/MaterialsTab.jsx'
import ProgressTab from '../components/tabs/ProgressTab.jsx'
import StudyPlanTab from '../components/tabs/StudyPlanTab.jsx'

const TABS = [
  { key: 'chat', label: 'Chat', component: ChatTab },
  { key: 'notes', label: 'Explain', component: NotesTab },
  { key: 'quiz', label: 'Quiz', component: QuizTab },
  { key: 'practice', label: 'Practice', component: PracticeTab },
  { key: 'flashcards', label: 'Flashcards', component: FlashcardsTab },
  { key: 'summarize', label: 'Summarize', component: SummarizeTab },
  { key: 'materials', label: 'My Material', component: MaterialsTab },
  { key: 'progress', label: 'Progress', component: ProgressTab },
  { key: 'plan', label: 'Study Plan', component: StudyPlanTab },
]

export default function SessionPage() {
  const { sessionId } = useParams()
  const [session, setSession] = useState(null)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState('chat')

  useEffect(() => {
    api.getSession(sessionId).then(setSession).catch((err) => setError(err.message))
  }, [sessionId])

  if (error) {
    return (
      <div className="max-w-3xl mx-auto p-6">
        <ErrorBanner message={error} />
        <Link to="/" className="text-brand-600 underline text-sm mt-4 inline-block">Back to dashboard</Link>
      </div>
    )
  }
  if (!session) return <Loading label="Loading session..." />

  const ActiveComponent = TABS.find((t) => t.key === activeTab).component

  return (
    <div className="max-w-5xl mx-auto px-4 py-6">
      <div className="flex items-center justify-between flex-wrap gap-3 mb-5">
        <div>
          <Link to="/" className="text-sm text-slate-500 hover:text-brand-600">&larr; All sessions</Link>
          <h1 className="text-2xl font-bold mt-1">{session.subject}</h1>
        </div>
        <DifficultyBadge level={session.difficulty_level} />
      </div>

      <nav className="flex gap-1 overflow-x-auto border-b border-slate-200 mb-6 pb-px">
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => setActiveTab(t.key)}
            className={`px-4 py-2 text-sm font-medium whitespace-nowrap rounded-t-lg border-b-2 transition-colors ${
              activeTab === t.key
                ? 'border-brand-500 text-brand-600'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            {t.label}
          </button>
        ))}
      </nav>

      {/* key={sessionId+tab} remounts the tab when switching so it reloads fresh data */}
      <ActiveComponent key={`${sessionId}-${activeTab}`} sessionId={sessionId} session={session} />
    </div>
  )
}
