import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as api from '@/lib/api'

export const useSources = () =>
  useQuery({ queryKey: ['sources'], queryFn: api.getSources })

export const useSource = (id: number) =>
  useQuery({ queryKey: ['sources', id], queryFn: () => api.getSource(id), enabled: !!id })

export const useCreateSource = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: api.createSource,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['sources'] }),
  })
}

export const useUpdateSource = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<api.SourceCreate> }) =>
      api.updateSource(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['sources'] }),
  })
}

export const useDeleteSource = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: api.deleteSource,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['sources'] }),
  })
}

export const useTriggerSource = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: api.triggerSource,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['jobs'] })
      qc.invalidateQueries({ queryKey: ['sources'] })
    },
  })
}

export const useToggleSource = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: api.toggleSource,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['sources'] }),
  })
}
