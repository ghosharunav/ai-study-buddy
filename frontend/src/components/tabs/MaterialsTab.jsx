import { useEffect, useState } from 'react'
import { api } from '../../api/client.js'
import Loading from '../Loading.jsx'
import ErrorBanner from '../ErrorBanner.jsx'

function AskPanel({ material }) {
  const [question, setQuestion] = useState('')
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleAsk(e) {
    e.preventDefault()
    const q = question.trim()
    if (!q) return
    setLoading(true)
    setError('')
    try {
      const res = await api.askMaterial(material.id, q)
      setHistory((prev) => [...prev, { question: q, ...res }])
      setQuestion('')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mt-4 space-y-3">
      {history.map((h, i) => (
        <div key={i} className="space-y-2">
          <div className="flex justify-end">
            <div className="max-w-[85%] rounded-2xl bg-brand-500 text-white text-sm px-4 py-2">{h.question}</div>
          </div>
          <div className="flex justify-start">
            <div className="max-w-[85%] rounded-2xl bg-slate-100 text-sm px-4 py-2 space-y-1">
              <p className="whitespace-pre-wrap">{h.answer}</p>
              <p className={`text-xs ${h.grounded ? 'text-green-700' : 'text-amber-700'}`}>
                {h.grounded
                  ? `Grounded in your material (excerpt ${h.source_chunk_indices.join(', ')})`
                  : 'Not clearly covered in your material'}
              </p>
            </div>
          </div>
        </div>
      ))}
      <ErrorBanner message={error} />
      <form onSubmit={handleAsk} className="flex gap-2">
        <input
          className="input"
          placeholder="Ask something about this material..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <button className="btn-primary" disabled={loading || !question.trim()}>
          {loading ? '...' : 'Ask'}
        </button>
      </form>
    </div>
  )
}

export default function MaterialsTab({ sessionId }) {
  const [materials, setMaterials] = useState([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [openId, setOpenId] = useState(null)

  useEffect(() => {
    api.listMaterials(sessionId)
      .then(setMaterials)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [sessionId])

  async function handleUpload(e) {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true)
    setError('')
    try {
      const material = await api.uploadMaterial(sessionId, file)
      setMaterials((prev) => [...prev, material])
      setOpenId(material.id)
    } catch (err) {
      setError(err.message)
    } finally {
      setUploading(false)
      e.target.value = ''
    }
  }

  return (
    <div className="space-y-4">
      <div className="card">
        <label className="label">Upload study material (.txt or .md)</label>
        <input
          type="file"
          accept=".txt,.md,text/plain,text/markdown"
          onChange={handleUpload}
          disabled={uploading}
          className="block w-full text-sm text-slate-500 file:mr-4 file:rounded-lg file:border-0 file:bg-brand-500 file:px-4 file:py-2 file:text-sm file:font-medium file:text-white hover:file:bg-brand-600"
        />
        <p className="text-xs text-slate-400 mt-2">
          Then ask questions and get answers grounded strictly in your own material.
        </p>
      </div>

      <ErrorBanner message={error} />
      {uploading && <Loading label="Processing your file..." />}
      {loading ? <Loading /> : materials.map((m) => (
        <div key={m.id} className="card">
          <button className="w-full flex items-center justify-between text-left" onClick={() => setOpenId(openId === m.id ? null : m.id)}>
            <div>
              <p className="font-medium">{m.filename}</p>
              <p className="text-xs text-slate-400">{m.num_chunks} section(s) indexed</p>
            </div>
            <span className="text-sm text-brand-600">{openId === m.id ? 'Close' : 'Chat'}</span>
          </button>
          {openId === m.id && <AskPanel material={m} />}
        </div>
      ))}
      {!loading && materials.length === 0 && !uploading && (
        <p className="text-center text-slate-400 text-sm">No material uploaded yet.</p>
      )}
    </div>
  )
}
