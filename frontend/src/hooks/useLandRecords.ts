import { useQuery } from '@tanstack/react-query'
import * as api from '@/lib/api'

export const useLandRecords = (params?: Record<string, unknown>) =>
  useQuery({ queryKey: ['land-records', params], queryFn: () => api.getLandRecords(params) })

export const useLandRecord = (id: number) =>
  useQuery({ queryKey: ['land-records', id], queryFn: () => api.getLandRecord(id), enabled: !!id })

export const useLandRecordStats = () =>
  useQuery({ queryKey: ['land-records', 'stats'], queryFn: api.getLandRecordStats })
