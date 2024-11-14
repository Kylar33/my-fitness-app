
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../lib/axios';

export function useAssignments() {
  const queryClient = useQueryClient();
  return {
    getAssignments: (userId) => useQuery(
      ['assignments', userId],
      () => api.get(`/user/${userId}/assignments`).then(res => res.data)
    ),
    assignRoutine: useMutation(
      data => api.post('/assign/routine', data),
      {
        onSuccess: () => queryClient.invalidateQueries(['assignments'])
      }
    ),
    assignNutrition: useMutation(
      data => api.post('/assign/nutrition', data),
      {
        onSuccess: () => queryClient.invalidateQueries(['assignments'])
      }
    )
  };
}