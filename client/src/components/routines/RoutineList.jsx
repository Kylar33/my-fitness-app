import { useRoutines } from '../../hooks/useRoutines';
import { RoutineForm } from './RoutineForm';
import { useState } from 'react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';

export function RoutineList() {
  const { routines, deleteRoutine } = useRoutines();
  const [selectedRoutine, setSelectedRoutine] = useState(null);
  const [isFormOpen, setIsFormOpen] = useState(false);

  return (
    <div className="space-y-4">
      <div className="flex justify-between">
        <h1 className="text-2xl font-bold">Routines</h1>
        <Button onClick={() => setIsFormOpen(true)}>Create Routine</Button>
      </div>

      <div className="grid gap-4 grid-cols-1 md:grid-cols-2">
        {routines.data?.map(routine => (
          <Card key={routine.id}>
            <div className="space-y-4">
              <div className="flex justify-between">
                <div>
                  <h3 className="font-semibold">{routine.name}</h3>
                  <p className="text-gray-600">{routine.description}</p>
                </div>
                <div className="space-x-2">
                  <button 
                    onClick={() => {
                      setSelectedRoutine(routine);
                      setIsFormOpen(true);
                    }}
                    className="text-blue-500"
                  >
                    Edit
                  </button>
                  <button 
                    onClick={() => deleteRoutine.mutate(routine.id)}
                    className="text-red-500"
                  >
                    Delete
                  </button>
                </div>
              </div>

              <div>
                <h4 className="font-medium mb-2">Exercises</h4>
                <ul className="space-y-2">
                  {routine.exercises.map((exercise, index) => (
                    <li key={index} className="text-sm">
                      {exercise.name} - {exercise.sets}x{exercise.reps} 
                      {exercise.rest_time && ` (Rest: ${exercise.rest_time}s)`}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {isFormOpen && (
        <RoutineForm 
          routine={selectedRoutine} 
          onClose={() => {
            setIsFormOpen(false);
            setSelectedRoutine(null);
          }}
        />
      )}
    </div>
  );
}