import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as api from '@/lib/api'

interface JobFilters {
  source_id?: number
  status?: api.JobStatus
  limit?: number
  offset?: number
}

export const useJobs = (filters?: JobFilters, refetchInterval?: number) =>
  useQuery({
    queryKey: ['jobs', filters],
    queryFn: () => api.getJobs(filters),
    refetchInterval,
  })

export const useJob = (id: number) =>
  useQuery({
    queryKey: ['jobs', id],
    queryFn: () => api.getJob(id),
    enabled: !!id,
  })

export const useCancelJob = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: api.cancelJob,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['jobs'] }),
  })
}

export const useDeleteJob = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: api.deleteJob,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['jobs'] }),
  })
}
