import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../lib/axios';

export function useNutritionPlans() {
  const queryClient = useQueryClient();
  
  return {
    plans: useQuery(['nutrition-plans'], () => 
      api.get('/nutrition-plans').then(res => res.data)
    ),
    createPlan: useMutation(
      data => api.post('/nutrition-plans', data),
      {
        onSuccess: () => queryClient.invalidateQueries(['nutrition-plans'])
      }
    ),
    updatePlan: useMutation(
      ({id, data}) => api.put(`/nutrition-plans/${id}`, data),
      {
        onSuccess: () => queryClient.invalidateQueries(['nutrition-plans'])
      }
    ),
    deletePlan: useMutation(
      id => api.delete(`/nutrition-plans/${id}`),
      {
        onSuccess: () => queryClient.invalidateQueries(['nutrition-plans'])
      }
    )
  };
}