import { useQuery } from '@tanstack/react-query'
import * as api from '@/lib/api'

export const useProperties = (params?: Record<string, unknown>) =>
  useQuery({ queryKey: ['properties', params], queryFn: () => api.getProperties(params) })

export const useProperty = (id: number) =>
  useQuery({ queryKey: ['properties', id], queryFn: () => api.getProperty(id), enabled: !!id })

export const usePropertyStats = () =>
  useQuery({ queryKey: ['properties', 'stats'], queryFn: api.getPropertyStats })
