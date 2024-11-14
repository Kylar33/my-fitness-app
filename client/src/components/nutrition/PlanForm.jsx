import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNutritionPlans } from '../../hooks/useNutritionPlans';
import { Input, Button } from '../ui';

const mealSchema = z.object({
  name: z.string().min(1),
  description: z.string().optional(),
  calories: z.number().min(0),
  protein: z.number().min(0),
  carbs: z.number().min(0),
  fats: z.number().min(0),
  time_of_day: z.string()
});

const planSchema = z.object({
  name: z.string().min(1),
  description: z.string().optional(),
  meals: z.array(mealSchema).min(1)
});

export function PlanForm({ plan, onClose }) {
  const { createPlan, updatePlan } = useNutritionPlans();
  const { register, control, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(planSchema),
    defaultValues: plan || {
      meals: [{ name: '', calories: 0, protein: 0, carbs: 0, fats: 0 }]
    }
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'meals'
  });

  const onSubmit = async (data) => {
    try {
      if (plan) {
        await updatePlan.mutate({ id: plan.id, data });
      } else {
        await createPlan.mutate(data);
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
          {plan ? 'Edit Plan' : 'Create Plan'}
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
              <h3 className="font-medium">Meals</h3>
              <Button 
                type="button"
                onClick={() => append({ 
                  name: '', 
                  calories: 0, 
                  protein: 0, 
                  carbs: 0, 
                  fats: 0 
                })}
              >
                Add Meal
              </Button>
            </div>

            {fields.map((field, index) => (
              <div key={field.id} className="p-4 border rounded-lg space-y-4">
                <div className="flex justify-between">
                  <h4>Meal {index + 1}</h4>
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
                  {...register(`meals.${index}.name`)}
                  error={errors.meals?.[index]?.name?.message}
                />
                <Input
                  label="Description"
                  {...register(`meals.${index}.description`)}
                  error={errors.meals?.[index]?.description?.message}
                />
                <Input
                  label="Time of Day"
                  {...register(`meals.${index}.time_of_day`)}
                  error={errors.meals?.[index]?.time_of_day?.message}
                />
                <div className="grid grid-cols-2 gap-4">
                  <Input
                    label="Calories"
                    type="number"
                    {...register(`meals.${index}.calories`, { 
                      valueAsNumber: true 
                    })}
                    error={errors.meals?.[index]?.calories?.message}
                  />
                  <Input
                    label="Protein (g)"
                    type="number"
                    {...register(`meals.${index}.protein`, { 
                      valueAsNumber: true 
                    })}
                    error={errors.meals?.[index]?.protein?.message}
                  />
                  <Input
                    label="Carbs (g)"
                    type="number"
                    {...register(`meals.${index}.carbs`, { 
                      valueAsNumber: true 
                    })}
                    error={errors.meals?.[index]?.carbs?.message}
                  />
                  <Input
                    label="Fats (g)"
                    type="number"
                    {...register(`meals.${index}.fats`, { 
                      valueAsNumber: true 
                    })}
                    error={errors.meals?.[index]?.fats?.message}
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