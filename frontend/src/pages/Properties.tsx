import { useState } from 'react'
import { useProperties, usePropertyStats } from '@/hooks/useProperties'
import { DataTable } from '@/components/DataTable'
import { ExportButton } from '@/components/ExportButton'
import { formatCurrency, formatNumber } from '@/lib/utils'
import type { PropertyRecord } from '@/lib/api'
import type { ColumnDef } from '@tanstack/react-table'

const columns: ColumnDef<PropertyRecord, unknown>[] = [
  { accessorKey: 'town', header: 'Town' },
  { accessorKey: 'parcel_id', header: 'Parcel ID' },
  {
    id: 'address',
    header: 'Address',
    cell: ({ row }) => `${row.original.street_number ?? ''} ${row.original.street_name ?? ''}`.trim() || '—',
  },
  { accessorKey: 'owner_name', header: 'Owner' },
  {
    accessorKey: 'assessed_value',
    header: 'Assessed Value',
    cell: ({ getValue }) => formatCurrency(getValue() as number | null),
  },
  { accessorKey: 'assessment_year', header: 'Year' },
  { accessorKey: 'property_class', header: 'Class' },
]

export function Properties() {
  const [filters, setFilters] = useState<Record<string, unknown>>({ limit: 100 })
  const { data: records, isLoading } = useProperties(filters)
  const { data: stats } = usePropertyStats()

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Properties</h1>
          <p className="text-sm text-gray-500 mt-1">
            {formatNumber(stats?.total ?? 0)} records across {stats?.towns.length ?? 0} towns
          </p>
        </div>
        <ExportButton type="properties" />
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl border border-gray-200 p-4 flex flex-wrap gap-3">
        <input
          placeholder="Town…"
          className="border rounded-md px-3 py-1.5 text-sm w-36"
          onChange={e => setFilters(f => ({ ...f, town: e.target.value || undefined }))}
        />
        <input
          placeholder="Owner name…"
          className="border rounded-md px-3 py-1.5 text-sm w-44"
          onChange={e => setFilters(f => ({ ...f, owner: e.target.value || undefined }))}
        />
        <input
          placeholder="Parcel ID…"
          className="border rounded-md px-3 py-1.5 text-sm w-36"
          onChange={e => setFilters(f => ({ ...f, parcel_id: e.target.value || undefined }))}
        />
        <input
          placeholder="Min value"
          type="number"
          className="border rounded-md px-3 py-1.5 text-sm w-32"
          onChange={e => setFilters(f => ({ ...f, min_value: e.target.value || undefined }))}
        />
        <input
          placeholder="Max value"
          type="number"
          className="border rounded-md px-3 py-1.5 text-sm w-32"
          onChange={e => setFilters(f => ({ ...f, max_value: e.target.value || undefined }))}
        />
        <input
          placeholder="Year"
          type="number"
          className="border rounded-md px-3 py-1.5 text-sm w-24"
          onChange={e => setFilters(f => ({ ...f, year: e.target.value || undefined }))}
        />
      </div>

      <DataTable data={records ?? []} columns={columns} isLoading={isLoading} />
    </div>
  )
}
