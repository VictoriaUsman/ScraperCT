import { useState } from 'react'
import { useBusinesses, useBusinessStats } from '@/hooks/useBusinesses'
import { DataTable } from '@/components/DataTable'
import { ExportButton } from '@/components/ExportButton'
import { formatDate, formatNumber } from '@/lib/utils'
import type { BusinessRecord } from '@/lib/api'
import type { ColumnDef } from '@tanstack/react-table'

const columns: ColumnDef<BusinessRecord, unknown>[] = [
  { accessorKey: 'business_id', header: 'ID' },
  { accessorKey: 'business_name', header: 'Name' },
  { accessorKey: 'business_type', header: 'Type' },
  {
    accessorKey: 'status',
    header: 'Status',
    cell: ({ getValue }) => {
      const s = getValue() as string | null
      if (!s) return '—'
      const color = s.toLowerCase() === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
      return <span className={`px-2 py-0.5 text-xs rounded-full ${color}`}>{s}</span>
    },
  },
  {
    accessorKey: 'formation_date',
    header: 'Formed',
    cell: ({ getValue }) => formatDate(getValue() as string | null),
  },
  { accessorKey: 'state_of_formation', header: 'State' },
  { accessorKey: 'principal_office', header: 'Office' },
]

export function Businesses() {
  const [filters, setFilters] = useState<Record<string, unknown>>({ limit: 100 })
  const { data: records, isLoading } = useBusinesses(filters)
  const { data: stats } = useBusinessStats()

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Businesses</h1>
          <p className="text-sm text-gray-500 mt-1">
            {formatNumber(stats?.total ?? 0)} business filings
          </p>
        </div>
        <ExportButton type="businesses" />
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-4 flex flex-wrap gap-3">
        <input
          placeholder="Business name…"
          className="border rounded-md px-3 py-1.5 text-sm w-52"
          onChange={e => setFilters(f => ({ ...f, name: e.target.value || undefined }))}
        />
        <input
          placeholder="Type…"
          className="border rounded-md px-3 py-1.5 text-sm w-36"
          onChange={e => setFilters(f => ({ ...f, business_type: e.target.value || undefined }))}
        />
        <input
          placeholder="Status…"
          className="border rounded-md px-3 py-1.5 text-sm w-36"
          onChange={e => setFilters(f => ({ ...f, status: e.target.value || undefined }))}
        />
      </div>

      <DataTable data={records ?? []} columns={columns} isLoading={isLoading} />
    </div>
  )
}
