import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import NewScreening from './pages/NewScreening'
import Results from './pages/Results'
import History from './pages/History'
import SystemInfo from './pages/SystemInfo'

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/screen" element={<NewScreening />} />
          <Route path="/results/:screeningId" element={<Results />} />
          <Route path="/history" element={<History />} />
          <Route path="/system" element={<SystemInfo />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}
