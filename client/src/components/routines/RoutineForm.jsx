import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useRoutines } from '../../hooks/useRoutines';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';

const exerciseSchema = z.object({
  name: z.string().min(1),
  description: z.string().optional(),
  sets: z.number().min(1),
  reps: z.number().min(1),
  rest_time: z.number().optional()
});

const routineSchema = z.object({
  name: z.string().min(1),
  description: z.string().optional(),
  exercises: z.array(exerciseSchema).min(1)
});

export function RoutineForm({ routine, onClose }) {
  const { createRoutine, updateRoutine } = useRoutines();
  const { register, control, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(routineSchema),
    defaultValues: routine || {
      exercises: [{ name: '', sets: 3, reps: 10 }]
    }
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'exercises'
  });

  const onSubmit = async (data) => {
    try {
      if (routine) {
        await updateRoutine.mutate({ id: routine.id, data });
      } else {
        await createRoutine.mutate(data);
      }
      onClose();
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <h2 className="text-xl font-bold mb-4">
          {routine ? 'Edit Routine' : 'Create Routine'}
        </h2>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div className="space-y-4">
            <Input
              label="Name"
              {...register('name')}
              error={errors.name?.message}
            />
            <Input
              label="Description"
              {...register('description')}
              error={errors.description?.message}
            />
          </div>

          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="font-medium">Exercises</h3>
              <Button 
                type="button"
                onClick={() => append({ name: '', sets: 3, reps: 10 })}
              >
                Add Exercise
              </Button>
            </div>

            {fields.map((field, index) => (
              <div key={field.id} className="p-4 border rounded-lg space-y-4">
                <div className="flex justify-between">
                  <h4>Exercise {index + 1}</h4>
                  <button
                    type="button"
                    onClick={() => remove(index)}
                    className="text-red-500"
                  >
                    Remove
                  </button>
                </div>

                <Input
                  label="Name"
                  {...register(`exercises.${index}.name`)}
                  error={errors.exercises?.[index]?.name?.message}
                />
                <Input
                  label="Description"
                  {...register(`exercises.${index}.description`)}
                  error={errors.exercises?.[index]?.description?.message}
                />
                <div className="grid grid-cols-3 gap-4">
                  <Input
                    label="Sets"
                    type="number"
                    {...register(`exercises.${index}.sets`, { 
                      valueAsNumber: true 
                    })}
                    error={errors.exercises?.[index]?.sets?.message}
                  />
                  <Input
                    label="Reps"
                    type="number"
                    {...register(`exercises.${index}.reps`, { 
                      valueAsNumber: true 
                    })}
                    error={errors.exercises?.[index]?.reps?.message}
                  />
                  <Input
                    label="Rest Time (s)"
                    type="number"
                    {...register(`exercises.${index}.rest_time`, { 
                      valueAsNumber: true 
                    })}
                    error={errors.exercises?.[index]?.rest_time?.message}
                  />
                </div>
              </div>
            ))}
          </div>

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