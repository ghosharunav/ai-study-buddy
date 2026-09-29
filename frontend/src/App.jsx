import { Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard.jsx'
import SessionPage from './pages/SessionPage.jsx'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/sessions/:sessionId" element={<SessionPage />} />
    </Routes>
  )
}
