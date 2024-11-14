import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../lib/axios';

export function useRoutines() {
  const queryClient = useQueryClient();

  const routines = useQuery({
    queryKey: ['routines'],
    queryFn: () => api.get('/routines').then(res => res.data)
  });

  const createRoutine = useMutation({
    mutationFn: (data) => api.post('/routines', data),
    onSuccess: () => queryClient.invalidateQueries(['routines'])
  });

  const updateRoutine = useMutation({
    mutationFn: ({id, data}) => api.put(`/routines/${id}`, data),
    onSuccess: () => queryClient.invalidateQueries(['routines'])
  });

  const deleteRoutine = useMutation({
    mutationFn: (id) => api.delete(`/routines/${id}`),
    onSuccess: () => queryClient.invalidateQueries(['routines'])
  });

  return { routines, createRoutine, updateRoutine, deleteRoutine };
}
