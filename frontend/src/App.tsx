import { Routes, Route } from 'react-router-dom'
import { Shell } from '@/components/layout/Shell'
import { Dashboard } from '@/pages/Dashboard'
import { Sources } from '@/pages/Sources'
import { Jobs } from '@/pages/Jobs'
import { Properties } from '@/pages/Properties'
import { LandRecords } from '@/pages/LandRecords'
import { Businesses } from '@/pages/Businesses'
import { OpenData } from '@/pages/OpenData'

export default function App() {
  return (
    <Routes>
      <Route element={<Shell />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/sources" element={<Sources />} />
        <Route path="/jobs" element={<Jobs />} />
        <Route path="/properties" element={<Properties />} />
        <Route path="/land-records" element={<LandRecords />} />
        <Route path="/businesses" element={<Businesses />} />
        <Route path="/open-data" element={<OpenData />} />
      </Route>
    </Routes>
  )
}
