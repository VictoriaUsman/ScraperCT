import { useState } from 'react'
import { useLandRecords, useLandRecordStats } from '@/hooks/useLandRecords'
import { DataTable } from '@/components/DataTable'
import { ExportButton } from '@/components/ExportButton'
import { formatCurrency, formatDate, formatNumber } from '@/lib/utils'
import type { LandRecord, LandRecordType } from '@/lib/api'
import type { ColumnDef } from '@tanstack/react-table'
import { ExternalLink } from 'lucide-react'

const RECORD_TYPES: LandRecordType[] = ['deed', 'mortgage', 'lien', 'release', 'other']

const columns: ColumnDef<LandRecord, unknown>[] = [
  { accessorKey: 'town', header: 'Town' },
  { accessorKey: 'record_type', header: 'Type', cell: ({ getValue }) => (
    <span className="capitalize">{String(getValue() ?? '—')}</span>
  )},
  { accessorKey: 'grantor', header: 'Grantor' },
  { accessorKey: 'grantee', header: 'Grantee' },
  {
    accessorKey: 'recorded_date',
    header: 'Recorded',
    cell: ({ getValue }) => formatDate(getValue() as string | null),
  },
  { accessorKey: 'book', header: 'Book' },
  { accessorKey: 'page', header: 'Page' },
  {
    accessorKey: 'consideration',
    header: 'Consideration',
    cell: ({ getValue }) => formatCurrency(getValue() as number | null),
  },
  {
    accessorKey: 'document_url',
    header: 'Doc',
    cell: ({ getValue }) => {
      const url = getValue() as string | null
      return url ? (
        <a href={url} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline inline-flex items-center gap-1">
          <ExternalLink className="h-3 w-3" /> View
        </a>
      ) : '—'
    },
  },
]

export function LandRecords() {
  const [filters, setFilters] = useState<Record<string, unknown>>({ limit: 100 })
  const { data: records, isLoading } = useLandRecords(filters)
  const { data: stats } = useLandRecordStats()

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Land Records</h1>
          <p className="text-sm text-gray-500 mt-1">
            {formatNumber(stats?.total ?? 0)} records across {stats?.towns.length ?? 0} towns
          </p>
        </div>
        <ExportButton type="land-records" />
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-4 flex flex-wrap gap-3">
        <input
          placeholder="Town…"
          className="border rounded-md px-3 py-1.5 text-sm w-36"
          onChange={e => setFilters(f => ({ ...f, town: e.target.value || undefined }))}
        />
        <select
          className="border rounded-md px-3 py-1.5 text-sm"
          onChange={e => setFilters(f => ({ ...f, record_type: e.target.value || undefined }))}
        >
          <option value="">All types</option>
          {RECORD_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
        <input
          placeholder="Grantor…"
          className="border rounded-md px-3 py-1.5 text-sm w-44"
          onChange={e => setFilters(f => ({ ...f, grantor: e.target.value || undefined }))}
        />
        <input
          placeholder="Grantee…"
          className="border rounded-md px-3 py-1.5 text-sm w-44"
          onChange={e => setFilters(f => ({ ...f, grantee: e.target.value || undefined }))}
        />
        <input
          type="date"
          className="border rounded-md px-3 py-1.5 text-sm"
          onChange={e => setFilters(f => ({ ...f, date_from: e.target.value || undefined }))}
        />
        <input
          type="date"
          className="border rounded-md px-3 py-1.5 text-sm"
          onChange={e => setFilters(f => ({ ...f, date_to: e.target.value || undefined }))}
        />
      </div>

      <DataTable data={records ?? []} columns={columns} isLoading={isLoading} />
    </div>
  )
}
