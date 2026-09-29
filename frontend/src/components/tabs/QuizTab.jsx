import { useState } from 'react'
import { api } from '../../api/client.js'
import Loading from '../Loading.jsx'
import ErrorBanner from '../ErrorBanner.jsx'

export default function QuizTab({ sessionId, session }) {
  const [topic, setTopic] = useState('')
  const [level, setLevel] = useState(session.difficulty_level)
  const [numQuestions, setNumQuestions] = useState(5)

  const [quiz, setQuiz] = useState(null)
  const [answers, setAnswers] = useState([])
  const [result, setResult] = useState(null)

  const [generating, setGenerating] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  async function handleGenerate(e) {
    e.preventDefault()
    if (!topic.trim()) return
    setGenerating(true)
    setError('')
    setResult(null)
    try {
      const q = await api.generateQuiz(sessionId, {
        topic: topic.trim(), difficulty_level: level, num_questions: Number(numQuestions),
      })
      setQuiz(q)
      setAnswers(new Array(q.questions.length).fill(null))
    } catch (err) {
      setError(err.message)
    } finally {
      setGenerating(false)
    }
  }

  async function handleSubmit() {
    setSubmitting(true)
    setError('')
    try {
      setResult(await api.submitQuiz(quiz.id, answers))
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  function reset() {
    setQuiz(null)
    setResult(null)
    setAnswers([])
  }

  // ---------- Results view ----------
  if (result) {
    const pct = Math.round((result.score / result.total) * 100)
    return (
      <div className="space-y-4">
        <div className="card text-center">
          <p className="text-sm text-slate-500">Your score</p>
          <p className="text-5xl font-bold text-brand-600 my-2">{result.score} / {result.total}</p>
          <p className="text-slate-500">{pct}% correct</p>
          {result.weak_topics.length > 0 && (
            <p className="text-sm text-amber-700 bg-amber-50 rounded-lg px-3 py-2 mt-4 inline-block">
              Review these topics: {result.weak_topics.join(', ')}
            </p>
          )}
        </div>

        {result.results.map((r, i) => (
          <div key={i} className={`card border-l-4 ${r.is_correct ? 'border-l-green-500' : 'border-l-red-500'}`}>
            <p className="font-medium mb-3">{i + 1}. {r.question}</p>
            <div className="space-y-1.5">
              {r.options.map((opt, oi) => {
                const isCorrect = oi === r.correct_answer_index
                const isSelected = oi === r.selected_answer_index
                let cls = 'border-slate-200'
                if (isCorrect) cls = 'border-green-500 bg-green-50'
                else if (isSelected) cls = 'border-red-500 bg-red-50'
                return (
                  <div key={oi} className={`text-sm rounded-lg border px-3 py-2 ${cls}`}>
                    {opt}
                    {isCorrect && <span className="ml-2 text-green-700 font-medium">✓ correct</span>}
                    {isSelected && !isCorrect && <span className="ml-2 text-red-700 font-medium">your answer</span>}
                  </div>
                )
              })}
            </div>
            <p className="text-sm text-slate-600 mt-3"><span className="font-medium">Why:</span> {r.explanation}</p>
          </div>
        ))}

        <button className="btn-primary" onClick={reset}>Take another quiz</button>
      </div>
    )
  }

  // ---------- Taking the quiz ----------
  if (quiz) {
    const allAnswered = answers.every((a) => a !== null)
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Quiz: {quiz.topic}</h2>
          <button className="text-sm text-slate-500 underline" onClick={reset}>Cancel</button>
        </div>
        {quiz.questions.map((q, qi) => (
          <div key={qi} className="card">
            <p className="font-medium mb-3">{qi + 1}. {q.question}</p>
            <div className="space-y-1.5">
              {q.options.map((opt, oi) => (
                <label
                  key={oi}
                  className={`flex items-center gap-2 text-sm rounded-lg border px-3 py-2 cursor-pointer transition-colors ${
                    answers[qi] === oi ? 'border-brand-500 bg-brand-50' : 'border-slate-200 hover:bg-slate-50'
                  }`}
                >
                  <input
                    type="radio"
                    name={`q-${qi}`}
                    checked={answers[qi] === oi}
                    onChange={() => setAnswers((prev) => prev.map((a, i) => (i === qi ? oi : a)))}
                  />
                  {opt}
                </label>
              ))}
            </div>
          </div>
        ))}
        <ErrorBanner message={error} />
        <button className="btn-primary" disabled={!allAnswered || submitting} onClick={handleSubmit}>
          {submitting ? 'Scoring...' : allAnswered ? 'Submit answers' : 'Answer every question to submit'}
        </button>
      </div>
    )
  }

  // ---------- Setup form ----------
  return (
    <div className="space-y-4">
      <form onSubmit={handleGenerate} className="card grid gap-4 sm:grid-cols-[1fr_160px_120px_auto] items-end">
        <div>
          <label className="label">Quiz topic</label>
          <input className="input" placeholder="e.g. Binary Search Trees" value={topic} onChange={(e) => setTopic(e.target.value)} />
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
          <input className="input" type="number" min="1" max="10" value={numQuestions} onChange={(e) => setNumQuestions(e.target.value)} />
        </div>
        <button className="btn-primary" disabled={generating || !topic.trim()}>
          {generating ? 'Generating...' : 'Start quiz'}
        </button>
      </form>
      <ErrorBanner message={error} />
      {generating && <Loading label="Building your quiz..." />}
    </div>
  )
}
