import { useQuery } from '@tanstack/react-query'
import * as api from '@/lib/api'

export const useOpenData = (params?: Record<string, unknown>) =>
  useQuery({ queryKey: ['open-data', params], queryFn: () => api.getOpenData(params) })

export const useDatasets = () =>
  useQuery({ queryKey: ['datasets'], queryFn: api.getDatasets })
