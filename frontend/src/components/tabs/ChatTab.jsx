import { useEffect, useRef, useState } from 'react'
import { api } from '../../api/client.js'
import Loading from '../Loading.jsx'
import ErrorBanner from '../ErrorBanner.jsx'

export default function ChatTab({ sessionId }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [error, setError] = useState('')
  const bottomRef = useRef(null)

  useEffect(() => {
    api.getMessages(sessionId)
      .then(setMessages)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [sessionId])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, sending])

  async function handleSend(e) {
    e.preventDefault()
    const text = input.trim()
    if (!text || sending) return

    setInput('')
    setError('')
    setSending(true)
    // Show the student's message immediately (optimistic update)
    const optimistic = { id: `tmp-${Date.now()}`, role: 'user', content: text }
    setMessages((prev) => [...prev, optimistic])

    try {
      const res = await api.sendMessage(sessionId, text)
      setMessages((prev) => [...prev.filter((m) => m.id !== optimistic.id), res.user_message, res.assistant_message])
    } catch (err) {
      // The backend saves the user message even if the AI call fails, so keep it visible
      setError(`${err.message} — your message was saved, you can try again.`)
    } finally {
      setSending(false)
    }
  }

  if (loading) return <Loading />

  return (
    <div className="card flex flex-col h-[65vh]">
      <div className="flex-1 overflow-y-auto space-y-3 pr-1">
        {messages.length === 0 && (
          <p className="text-center text-slate-400 text-sm mt-10">
            Ask Aria anything about this subject to get started.
          </p>
        )}
        {messages.map((m) => (
          <div key={m.id} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-2 text-sm whitespace-pre-wrap ${
                m.role === 'user' ? 'bg-brand-500 text-white' : 'bg-slate-100 text-slate-800'
              }`}
            >
              {m.content}
            </div>
          </div>
        ))}
        {sending && (
          <div className="flex justify-start">
            <div className="bg-slate-100 rounded-2xl px-4 py-2 text-sm text-slate-500">Aria is thinking...</div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="mt-3">
        <ErrorBanner message={error} />
      </div>
      <form onSubmit={handleSend} className="flex gap-2 mt-3">
        <input
          className="input"
          placeholder="Ask a question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button className="btn-primary" disabled={sending || !input.trim()}>Send</button>
      </form>
    </div>
  )
}
