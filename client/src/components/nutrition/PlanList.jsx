import { useState } from 'react';
import { useNutritionPlans } from '../../hooks/useNutritionPlans';
import { PlanForm } from './PlanForm';
import { Card, Button } from '../ui';

export function PlanList() {
  const { plans, deletePlan } = useNutritionPlans();
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [isFormOpen, setIsFormOpen] = useState(false);

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Nutrition Plans</h1>
        <Button onClick={() => setIsFormOpen(true)}>Create Plan</Button>
      </div>

      <div className="grid gap-4 grid-cols-1 md:grid-cols-2">
        {plans.data?.map(plan => (
          <Card key={plan.id}>
            <div className="space-y-4">
              <div className="flex justify-between">
                <div>
                  <h3 className="font-semibold">{plan.name}</h3>
                  <p className="text-gray-600">{plan.description}</p>
                </div>
                <div className="space-x-2">
                  <button 
                    onClick={() => {
                      setSelectedPlan(plan);
                      setIsFormOpen(true);
                    }}
                    className="text-blue-500"
                  >
                    Edit
                  </button>
                  <button 
                    onClick={() => deletePlan.mutate(plan.id)}
                    className="text-red-500"
                  >
                    Delete
                  </button>
                </div>
              </div>

              <div>
                <h4 className="font-medium mb-2">Meals</h4>
                <ul className="space-y-2">
                  {plan.meals.map((meal, index) => (
                    <li key={index} className="text-sm">
                      <div className="font-medium">{meal.name}</div>
                      <div className="text-gray-600">{meal.description}</div>
                      <div className="text-xs text-gray-500">
                        Calories: {meal.calories} | 
                        Protein: {meal.protein}g | 
                        Carbs: {meal.carbs}g | 
                        Fats: {meal.fats}g
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {isFormOpen && (
        <PlanForm 
          plan={selectedPlan} 
          onClose={() => {
            setIsFormOpen(false);
            setSelectedPlan(null);
          }}
        />
      )}
    </div>
  );
}