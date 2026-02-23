import { useQuery } from '@tanstack/react-query'
import * as api from '@/lib/api'

export const useDashboardSummary = () =>
  useQuery({ queryKey: ['dashboard', 'summary'], queryFn: api.getDashboardSummary, refetchInterval: 10_000 })

export const useJobHistory = (days = 30) =>
  useQuery({ queryKey: ['dashboard', 'job-history', days], queryFn: () => api.getJobHistory(days) })
