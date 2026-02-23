import React, { useState } from 'react'
import { useJobs, useCancelJob, useDeleteJob } from '@/hooks/useJobs'
import { StatusBadge } from '@/components/StatusBadge'
import { formatDate } from '@/lib/utils'
import type { JobStatus } from '@/lib/api'
import { ChevronDown, ChevronRight, XCircle, Trash2 } from 'lucide-react'

export function Jobs() {
  const [expandedId, setExpandedId] = useState<number | null>(null)
  const { data: jobs, isLoading } = useJobs(
    {},
    // Auto-refresh every 5s if any job is running
    5000
  )
  const cancelMutation = useCancelJob()
  const deleteMutation = useDeleteJob()

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Scrape Jobs</h1>
        <p className="text-sm text-gray-500 mt-1">Execution history and status</p>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full text-sm text-left">
          <thead className="bg-gray-50 text-gray-500 uppercase text-xs border-b">
            <tr>
              <th className="px-4 py-3 w-8"></th>
              <th className="px-4 py-3">ID</th>
              <th className="px-4 py-3">Source</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Triggered By</th>
              <th className="px-4 py-3">Started</th>
              <th className="px-4 py-3">Records</th>
              <th className="px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {isLoading ? (
              <tr><td colSpan={8} className="px-4 py-8 text-center text-gray-400">Loading…</td></tr>
            ) : jobs?.length === 0 ? (
              <tr><td colSpan={8} className="px-4 py-8 text-center text-gray-400">No jobs yet</td></tr>
            ) : jobs?.map(job => (
              <React.Fragment key={job.id}>
                <tr className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <button
                      onClick={() => setExpandedId(expandedId === job.id ? null : job.id)}
                      className="text-gray-400 hover:text-gray-600"
                    >
                      {expandedId === job.id
                        ? <ChevronDown className="h-4 w-4" />
                        : <ChevronRight className="h-4 w-4" />}
                    </button>
                  </td>
                  <td className="px-4 py-3 text-gray-500">#{job.id}</td>
                  <td className="px-4 py-3 font-medium text-gray-900">#{job.source_id}</td>
                  <td className="px-4 py-3"><StatusBadge status={job.status} /></td>
                  <td className="px-4 py-3 text-gray-500 capitalize">{job.triggered_by}</td>
                  <td className="px-4 py-3 text-gray-500">
                    {job.started_at ? formatDate(job.started_at) : '—'}
                  </td>
                  <td className="px-4 py-3 text-gray-500">
                    {job.records_found > 0
                      ? `${job.records_found} (${job.records_new}N / ${job.records_updated}U / ${job.records_skipped}S)`
                      : '—'}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      {(job.status === 'pending' || job.status === 'running') && (
                        <button
                          onClick={() => cancelMutation.mutate(job.id)}
                          className="p-1.5 text-gray-400 hover:text-amber-600"
                          title="Cancel"
                        >
                          <XCircle className="h-4 w-4" />
                        </button>
                      )}
                      <button
                        onClick={() => { if (confirm('Delete this job?')) deleteMutation.mutate(job.id) }}
                        className="p-1.5 text-gray-400 hover:text-red-600"
                        title="Delete"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
                {expandedId === job.id && (
                  <tr className="bg-gray-50">
                    <td colSpan={8} className="px-6 pb-4">
                      {job.error_message && (
                        <p className="text-red-600 text-xs mb-2 font-medium">
                          Error: {job.error_message}
                        </p>
                      )}
                      {job.log_text ? (
                        <pre className="text-xs font-mono text-gray-600 whitespace-pre-wrap bg-gray-100 rounded p-3 max-h-48 overflow-y-auto">
                          {job.log_text}
                        </pre>
                      ) : (
                        <p className="text-xs text-gray-400">No log available</p>
                      )}
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
