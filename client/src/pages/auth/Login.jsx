  import { useForm } from 'react-hook-form';
  import { zodResolver } from '@hookform/resolvers/zod';
  import { z } from 'zod';
  import { useAuth } from '../../contexts/AuthContext';
  import { Input } from '../../components/ui/Input';
  import { Button } from '../../components/ui/Button';
  import { Card } from '../../components/ui/Card';
  import { useNavigate } from 'react-router-dom';

  const loginSchema = z.object({
    email: z.string().email('Email inválido').trim(),
    password: z.string().min(6, 'La contraseña debe tener al menos 6 caracteres').trim()
  });

  export function Login() {
    const { login } = useAuth();
    const navigate = useNavigate();
    const { register, handleSubmit, formState: { errors }, setError } = useForm({
      resolver: zodResolver(loginSchema)
    });

    const onSubmit = async (data) => {
      try {
        await login(data.email, data.password);
        navigate('/dashboard');
      } catch (error) {
        console.error('Login failed:', error);
        setError('root', {
          type: 'manual',
          message: 'Credenciales inválidas'
        });
      }
    };

    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Card className="w-full max-w-md">
          <h2 className="text-2xl font-bold text-center mb-6">Login</h2>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
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
            {errors.root && (
              <p className="text-red-500 text-sm">{errors.root.message}</p>
            )}
            <Button type="submit" className="w-full">
              Login
            </Button>
          </form>
        </Card>
      </div>
    );
  }