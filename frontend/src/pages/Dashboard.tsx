import { useDashboardSummary, useJobHistory } from '@/hooks/useDashboard'
import { formatNumber } from '@/lib/utils'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { Building2, FileText, Briefcase, Globe, Activity } from 'lucide-react'

function StatCard({
  label,
  value,
  icon: Icon,
  color,
}: {
  label: string
  value: number
  icon: React.ElementType
  color: string
}) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 flex items-center gap-4">
      <div className={`p-3 rounded-lg ${color}`}>
        <Icon className="h-6 w-6 text-white" />
      </div>
      <div>
        <p className="text-sm text-gray-500">{label}</p>
        <p className="text-2xl font-bold text-gray-900">{formatNumber(value)}</p>
      </div>
    </div>
  )
}

export function Dashboard() {
  const { data: summary, isLoading: sumLoading } = useDashboardSummary()
  const { data: history, isLoading: histLoading } = useJobHistory(30)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-sm text-gray-500 mt-1">Overview of CT public records data</p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Property Records"
          value={summary?.record_counts.properties ?? 0}
          icon={Building2}
          color="bg-blue-500"
        />
        <StatCard
          label="Land Records"
          value={summary?.record_counts.land_records ?? 0}
          icon={FileText}
          color="bg-emerald-500"
        />
        <StatCard
          label="Businesses"
          value={summary?.record_counts.businesses ?? 0}
          icon={Briefcase}
          color="bg-violet-500"
        />
        <StatCard
          label="Open Data Records"
          value={summary?.record_counts.open_data ?? 0}
          icon={Globe}
          color="bg-orange-500"
        />
      </div>

      {/* Running jobs indicator */}
      {summary && summary.running_jobs > 0 && (
        <div className="flex items-center gap-2 px-4 py-3 bg-blue-50 border border-blue-200 rounded-lg text-blue-700 text-sm">
          <Activity className="h-4 w-4 animate-spin" />
          {summary.running_jobs} scrape job{summary.running_jobs !== 1 ? 's' : ''} running
        </div>
      )}

      {/* Job history chart */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-base font-semibold text-gray-800 mb-4">
          Scrape Jobs — Last 30 Days
        </h2>
        {histLoading ? (
          <div className="h-64 flex items-center justify-center text-gray-400 text-sm">
            Loading chart…
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={history ?? []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="success" fill="#10b981" name="Success" stackId="a" />
              <Bar dataKey="failed" fill="#ef4444" name="Failed" stackId="a" />
              <Bar dataKey="cancelled" fill="#9ca3af" name="Cancelled" stackId="a" />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  )
}
