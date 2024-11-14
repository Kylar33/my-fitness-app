
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import DatePicker from 'react-datepicker';
import { useAssignments } from '../../hooks/useAssignments';
import { useRoutines } from '../../hooks/useRoutines';
import { Input, Button } from '../ui';

const assignSchema = z.object({
  user_id: z.number(),
  routine_id: z.number(),
  start_date: z.date(),
  end_date: z.date()
});

export function AssignRoutineForm({ userId, onClose }) {
  const { assignRoutine } = useAssignments();
  const { routines } = useRoutines();
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(assignSchema)
  });

  const onSubmit = async (data) => {
    try {
      await assignRoutine.mutate({
        ...data,
        user_id: userId
      });
      onClose();
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <select {...register('routine_id')}>
        {routines.data?.map(routine => (
          <option key={routine.id} value={routine.id}>
            {routine.name}
          </option>
        ))}
      </select>

      <DatePicker
        selected={watch('start_date')}
        onChange={date => setValue('start_date', date)}
        dateFormat="yyyy-MM-dd"
      />

      <DatePicker
        selected={watch('end_date')}
        onChange={date => setValue('end_date', date)}
        dateFormat="yyyy-MM-dd"
      />

      <Button type="submit">Assign Routine</Button>
    </form>
  );
}