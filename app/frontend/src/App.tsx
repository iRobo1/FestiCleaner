import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Landing from './Landing'

// Code-split the dashboard out of the initial bundle. The landing page
// loads on its own chunk; the dashboard chunk is fetched in the background
// once the landing page mounts (see Landing.tsx) so navigation is instant.
const Dashboard = lazy(() => import('./Dashboard'))

export default function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={null}>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  )
}
