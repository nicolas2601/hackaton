import { Routes, Route } from 'react-router-dom'
import { Landing } from './pages/Landing'
import { FincaPublica } from './pages/FincaPublica'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/finca/:slug" element={<FincaPublica />} />
    </Routes>
  )
}

export default App
