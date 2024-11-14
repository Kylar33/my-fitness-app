import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../lib/axios';

export function useUsers() {
  const queryClient = useQueryClient();

  const users = useQuery({
    queryKey: ['users'],
    queryFn: () => api.get('/users').then(res => res.data)
  });

  const createUser = useMutation({
    mutationFn: (data) => api.post('/users', data),
    onSuccess: () => queryClient.invalidateQueries(['users'])
  });

  const updateUser = useMutation({
    mutationFn: ({id, data}) => api.put(`/users/${id}`, data),
    onSuccess: () => queryClient.invalidateQueries(['users'])
  });

  const deleteUser = useMutation({
    mutationFn: (id) => api.delete(`/users/${id}`),
    onSuccess: () => queryClient.invalidateQueries(['users'])
  });

  return { users, createUser, updateUser, deleteUser };
}