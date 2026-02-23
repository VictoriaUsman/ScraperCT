import { useState } from 'react'
import { useOpenData, useDatasets } from '@/hooks/useOpenData'
import { ExportButton } from '@/components/ExportButton'
import { formatNumber } from '@/lib/utils'
import type { OpenDataRecord } from '@/lib/api'

export function OpenData() {
  const [selectedDataset, setSelectedDataset] = useState<string>('')
  const { data: datasets } = useDatasets()
  const { data: records, isLoading } = useOpenData(
    selectedDataset ? { dataset_id: selectedDataset, limit: 100 } : { limit: 100 }
  )

  // Build dynamic columns from first row's keys
  const firstRow = records?.[0]
  const dynamicKeys = firstRow?.data_json ? Object.keys(firstRow.data_json).slice(0, 8) : []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Open Data</h1>
          <p className="text-sm text-gray-500 mt-1">
            CT CKAN datasets — {formatNumber(records?.length ?? 0)} records shown
          </p>
        </div>
        <ExportButton type="open-data" />
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-4 flex flex-wrap gap-3 items-center">
        <label className="text-sm font-medium text-gray-700">Dataset:</label>
        <select
          className="border rounded-md px-3 py-1.5 text-sm min-w-[280px]"
          value={selectedDataset}
          onChange={e => setSelectedDataset(e.target.value)}
        >
          <option value="">All datasets</option>
          {datasets?.map(d => (
            <option key={d.dataset_id} value={d.dataset_id}>
              {d.dataset_name ?? d.dataset_id} ({formatNumber(d.record_count)})
            </option>
          ))}
        </select>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead className="bg-gray-50 text-gray-500 uppercase text-xs border-b">
            <tr>
              <th className="px-4 py-3">Dataset</th>
              <th className="px-4 py-3">Row ID</th>
              {dynamicKeys.map(k => (
                <th key={k} className="px-4 py-3">{k}</th>
              ))}
              <th className="px-4 py-3">Tags</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {isLoading ? (
              <tr><td colSpan={dynamicKeys.length + 3} className="px-4 py-8 text-center text-gray-400">Loading…</td></tr>
            ) : records?.length === 0 ? (
              <tr><td colSpan={dynamicKeys.length + 3} className="px-4 py-8 text-center text-gray-400">No records found</td></tr>
            ) : records?.map(rec => (
              <tr key={rec.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-gray-500 max-w-[120px] truncate">{rec.dataset_name ?? rec.dataset_id}</td>
                <td className="px-4 py-3 text-gray-500 font-mono text-xs">{rec.row_id}</td>
                {dynamicKeys.map(k => (
                  <td key={k} className="px-4 py-3 max-w-[150px] truncate">
                    {String((rec.data_json as Record<string, unknown>)?.[k] ?? '—')}
                  </td>
                ))}
                <td className="px-4 py-3">
                  {rec.tags?.map((t, i) => (
                    <span key={i} className="inline-block px-1.5 py-0.5 mr-1 bg-blue-50 text-blue-600 text-xs rounded">
                      {t}
                    </span>
                  ))}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
