import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Database,
  Briefcase,
  FileText,
  Building2,
  Globe,
  ChevronRight,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/sources', label: 'Sources', icon: Database },
  { to: '/jobs', label: 'Jobs', icon: Briefcase },
  { to: '/properties', label: 'Properties', icon: Building2 },
  { to: '/land-records', label: 'Land Records', icon: FileText },
  { to: '/businesses', label: 'Businesses', icon: Building2 },
  { to: '/open-data', label: 'Open Data', icon: Globe },
]

export function Sidebar() {
  return (
    <aside className="w-64 bg-slate-900 text-slate-100 flex flex-col h-full">
      <div className="px-6 py-5 border-b border-slate-700">
        <h1 className="text-lg font-semibold leading-tight">
          CT Public Records
        </h1>
        <p className="text-xs text-slate-400 mt-0.5">Data Platform</p>
      </div>
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors',
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              )
            }
          >
            <Icon className="h-4 w-4 shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="px-6 py-4 border-t border-slate-700">
        <p className="text-xs text-slate-500">v1.0.0</p>
      </div>
    </aside>
  )
}
