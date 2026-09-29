const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

/**
 * Every request goes through here. Throws a plain Error with a readable
 * message (pulled from FastAPI's {"detail": "..."} shape) on any non-2xx
 * response, so every page can just try/catch and show err.message.
 */
async function request(path, options = {}) {
  const isFormData = options.body instanceof FormData
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: isFormData ? options.headers : { 'Content-Type': 'application/json', ...options.headers },
  })

  let data = null
  try {
    data = await res.json()
  } catch {
    // no JSON body (e.g. a network-level failure) — data stays null
  }

  if (!res.ok) {
    const detail = data?.detail
    const message = typeof detail === 'string' ? detail : JSON.stringify(detail) || `Request failed (${res.status})`
    throw new Error(message)
  }
  return data
}

const post = (path, body) => request(path, { method: 'POST', body: JSON.stringify(body) })
const get = (path) => request(path)

export const api = {
  // Sessions
  listSessions: () => get('/sessions'),
  createSession: (payload) => post('/sessions', payload),
  getSession: (id) => get(`/sessions/${id}`),

  // Chat
  getMessages: (id) => get(`/sessions/${id}/messages`),
  sendMessage: (id, message) => post(`/sessions/${id}/chat`, { message }),

  // Notes / Explainer
  explainTopic: (id, topic, difficulty_level) => post(`/sessions/${id}/explain`, { topic, difficulty_level }),
  listNotes: (id) => get(`/sessions/${id}/notes`),

  // Quiz
  generateQuiz: (id, payload) => post(`/sessions/${id}/quiz`, payload),
  getQuiz: (quizId) => get(`/quizzes/${quizId}`),
  submitQuiz: (quizId, answers) => post(`/quizzes/${quizId}/submit`, { answers }),

  // Summarize
  summarize: (id, payload) => post(`/sessions/${id}/summarize`, payload),
  listSummaries: (id) => get(`/sessions/${id}/summaries`),

  // Practice questions
  generatePractice: (id, payload) => post(`/sessions/${id}/practice`, payload),
  submitPracticeAnswer: (setId, question_index, answer) =>
    post(`/practice/${setId}/feedback`, { question_index, answer }),

  // Flashcards
  generateFlashcards: (id, payload) => post(`/sessions/${id}/flashcards`, payload),
  listFlashcardSets: (id) => get(`/sessions/${id}/flashcards`),

  // Progress
  getProgress: (id) => get(`/sessions/${id}/progress`),

  // Study plan
  generateStudyPlan: (id, payload) => post(`/sessions/${id}/study-plan`, payload),
  listStudyPlans: (id) => get(`/sessions/${id}/study-plans`),

  // Materials (upload uses FormData, so it bypasses the JSON content-type header)
  uploadMaterial: (id, file) => {
    const formData = new FormData()
    formData.append('file', file)
    return request(`/sessions/${id}/materials`, { method: 'POST', body: formData })
  },
  listMaterials: (id) => get(`/sessions/${id}/materials`),
  askMaterial: (materialId, question) => post(`/materials/${materialId}/ask`, { question }),
}
