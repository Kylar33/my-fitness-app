import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import api from '../../lib/axios';
import { useMutation, useQueryClient } from '@tanstack/react-query';

const userSchema = z.object({
 email: z.string().email('Email inválido'),
 password: z.string().min(6, 'La contraseña debe tener al menos 6 caracteres'),
 first_name: z.string().min(1, 'El nombre es requerido'),
 last_name: z.string().min(1, 'El apellido es requerido')
});

export function UserForm({ onClose }) {
 const queryClient = useQueryClient();
 
 const { register, handleSubmit, formState: { errors } } = useForm({
   resolver: zodResolver(userSchema)
 });

 const createUser = useMutation({
   mutationFn: (data) => api.post('/users/', data),
   onSuccess: () => {
     queryClient.invalidateQueries(['users']);
     onClose?.();
   }
 });

 return (
   <Card className="p-6">
     <h2 className="text-xl font-bold mb-4">Create User</h2>
     <form onSubmit={handleSubmit(data => createUser.mutate(data))} className="space-y-4">
       <Input
         label="Email"
         type="email"
         {...register('email')}
         error={errors.email?.message}
       />
       <Input
         label="Password"
         type="password"
         {...register('password')}
         error={errors.password?.message}
       />
       <Input
         label="First Name"
         {...register('first_name')}
         error={errors.first_name?.message}
       />
       <Input
         label="Last Name"
         {...register('last_name')}
         error={errors.last_name?.message}
       />
       <div className="flex justify-end space-x-2">
         <Button type="submit" disabled={createUser.isLoading}>
           {createUser.isLoading ? 'Creating...' : 'Create User'}
         </Button>
       </div>
     </form>
   </Card>
 );
}