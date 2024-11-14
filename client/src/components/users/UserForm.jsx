import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useUsers } from '../../hooks/useUsers';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';

const userSchema = z.object({
  email: z.string().email(),
  password: z.string().min(6).optional(),
  first_name: z.string().min(1),
  last_name: z.string().min(1)
});

export function UserForm({ user, onClose }) {
  const { createUser, updateUser } = useUsers();
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(userSchema),
    defaultValues: user
  });

  const onSubmit = async (data) => {
    try {
      if (user) {
        await updateUser.mutate({ id: user.id, data });
      } else {
        await createUser.mutate(data);
      }
      onClose();
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 className="text-xl font-bold mb-4">
          {user ? 'Edit User' : 'Create User'}
        </h2>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Email"
            {...register('email')}
            error={errors.email?.message}
          />
          {!user && (
            <Input
              label="Password"
              type="password"
              {...register('password')}
              error={errors.password?.message}
            />
          )}
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
            <Button variant="secondary" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit">
              Save
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}