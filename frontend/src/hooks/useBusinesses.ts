import { useQuery } from '@tanstack/react-query'
import * as api from '@/lib/api'

export const useBusinesses = (params?: Record<string, unknown>) =>
  useQuery({ queryKey: ['businesses', params], queryFn: () => api.getBusinesses(params) })

export const useBusiness = (id: number) =>
  useQuery({ queryKey: ['businesses', id], queryFn: () => api.getBusiness(id), enabled: !!id })

export const useBusinessStats = () =>
  useQuery({ queryKey: ['businesses', 'stats'], queryFn: api.getBusinessStats })
