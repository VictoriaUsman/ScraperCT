import { useState } from 'react'
import { useSources, useCreateSource, useUpdateSource, useDeleteSource, useTriggerSource, useToggleSource } from '@/hooks/useSources'
import { SourceForm } from '@/components/SourceForm'
import { formatDate } from '@/lib/utils'
import type { Source, SourceCreate } from '@/lib/api'
import { Plus, Play, Pencil, Trash2, ToggleLeft, ToggleRight } from 'lucide-react'

export function Sources() {
  const { data: sources, isLoading } = useSources()
  const createMutation = useCreateSource()
  const updateMutation = useUpdateSource()
  const deleteMutation = useDeleteSource()
  const triggerMutation = useTriggerSource()
  const toggleMutation = useToggleSource()

  const [showAdd, setShowAdd] = useState(false)
  const [editing, setEditing] = useState<Source | null>(null)

  const handleCreate = async (data: SourceCreate) => {
    await createMutation.mutateAsync(data)
    setShowAdd(false)
  }

  const handleUpdate = async (data: SourceCreate) => {
    if (!editing) return
    await updateMutation.mutateAsync({ id: editing.id, data })
    setEditing(null)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Sources</h1>
          <p className="text-sm text-gray-500 mt-1">Manage scraping data sources</p>
        </div>
        <button
          onClick={() => setShowAdd(true)}
          className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
        >
          <Plus className="h-4 w-4" /> Add Source
        </button>
      </div>

      {/* Add/Edit Dialog */}
      {(showAdd || editing) && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg p-6">
            <h2 className="text-lg font-semibold mb-4">{editing ? 'Edit Source' : 'Add Source'}</h2>
            <SourceForm
              initial={editing ?? undefined}
              onSubmit={editing ? handleUpdate : handleCreate}
              onCancel={() => { setShowAdd(false); setEditing(null) }}
              loading={createMutation.isPending || updateMutation.isPending}
            />
          </div>
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full text-sm text-left">
          <thead className="bg-gray-50 text-gray-500 uppercase text-xs border-b">
            <tr>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Type</th>
              <th className="px-4 py-3">Schedule</th>
              <th className="px-4 py-3">Last Run</th>
              <th className="px-4 py-3">Active</th>
              <th className="px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {isLoading ? (
              <tr><td colSpan={6} className="px-4 py-8 text-center text-gray-400">Loading…</td></tr>
            ) : sources?.length === 0 ? (
              <tr><td colSpan={6} className="px-4 py-8 text-center text-gray-400">No sources yet — add one above</td></tr>
            ) : sources?.map(source => (
              <tr key={source.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium text-gray-900">{source.name}</td>
                <td className="px-4 py-3 text-gray-500">
                  <span className="inline-block px-2 py-0.5 bg-blue-50 text-blue-700 text-xs rounded">
                    {source.source_type}
                  </span>
                </td>
                <td className="px-4 py-3 font-mono text-xs text-gray-500">
                  {source.cron_schedule ?? '—'}
                </td>
                <td className="px-4 py-3 text-gray-500">
                  {source.last_scraped_at ? formatDate(source.last_scraped_at) : '—'}
                </td>
                <td className="px-4 py-3">
                  <button
                    onClick={() => toggleMutation.mutate(source.id)}
                    className="text-gray-400 hover:text-blue-600 transition-colors"
                    title="Toggle active"
                  >
                    {source.is_active
                      ? <ToggleRight className="h-5 w-5 text-green-500" />
                      : <ToggleLeft className="h-5 w-5" />}
                  </button>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => triggerMutation.mutate(source.id)}
                      className="p-1.5 text-gray-400 hover:text-blue-600 transition-colors"
                      title="Run now"
                    >
                      <Play className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => setEditing(source)}
                      className="p-1.5 text-gray-400 hover:text-amber-600 transition-colors"
                      title="Edit"
                    >
                      <Pencil className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => {
                        if (confirm(`Delete "${source.name}"?`)) deleteMutation.mutate(source.id)
                      }}
                      className="p-1.5 text-gray-400 hover:text-red-600 transition-colors"
                      title="Delete"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
