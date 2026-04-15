import { Routes, Route, Navigate } from 'react-router-dom'
import { Landing } from './pages/Landing'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Resumen from './pages/Resumen'
import Lotes from './pages/Lotes'
import Cosechas from './pages/Cosechas'
import Fitosanitario from './pages/Fitosanitario'
import ChatIA from './pages/ChatIA'
import PerfilAdmin from './pages/PerfilAdmin'
import FincaPublica from './pages/FincaPublica'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/finca/:slug" element={<FincaPublica />} />

      <Route
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      >
        <Route path="/dashboard" element={<Resumen />} />
        <Route path="/dashboard/resumen" element={<Resumen />} />
        <Route path="/dashboard/lotes" element={<Lotes />} />
        <Route path="/dashboard/cosechas" element={<Cosechas />} />
        <Route path="/dashboard/fitosanitario" element={<Fitosanitario />} />
        <Route path="/dashboard/chat" element={<ChatIA />} />
        <Route path="/dashboard/perfil" element={<PerfilAdmin />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
