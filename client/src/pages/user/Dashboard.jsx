import { useQuery } from '@tanstack/react-query';
import Layout from '../../components/Layout';
import { axiosPrivate } from '../../api/axios';
import ProfileForm from './ProfileForm';
import WorkoutPlanView from './WorkoutPlanView';
import NutritionPlanView from './NutritionPlanView';
import { useState } from 'react';

export default function UserDashboard() {
  const [isEditing, setIsEditing] = useState(false);
  const { data: userProfile, isLoading } = useQuery({
    queryKey: ['user-profile'],
    queryFn: async () => {
      const response = await axiosPrivate.get('/user/profile/');
      return response.data;
    }
  });

  const { data: userPlans, isLoading: plansLoading } = useQuery({
    queryKey: ['user-plans'],
    queryFn: async () => {
      const response = await axiosPrivate.get('/user/plans/');
      return response.data;
    }
  });

  if (isLoading || plansLoading) return <div>Cargando...</div>;

  return (
    <Layout>
      <div className="space-y-8">
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold">Mi Perfil</h2>
            <button
              onClick={() => setIsEditing(!isEditing)}
              className="bg-blue-500 text-white px-4 py-2 rounded"
            >
              {isEditing ? 'Cancelar' : 'Editar Perfil'}
            </button>
          </div>
          
          {isEditing ? (
            <ProfileForm
              profile={userProfile}
              onSuccess={() => setIsEditing(false)}
            />
          ) : (
            <div className="space-y-4">
              <div>
                <label className="font-bold">Nombre:</label>
                <p>{userProfile.full_name}</p>
              </div>
              <div>
                <label className="font-bold">Email:</label>
                <p>{userProfile.email}</p>
              </div>
            </div>
          )}
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-2xl font-bold mb-4">Mis Planes de Ejercicio</h2>
          {userPlans?.workout_plans?.length > 0 ? (
            userPlans.workout_plans.map((plan) => (
              <WorkoutPlanView key={plan.id} plan={plan} />
            ))
          ) : (
            <p>No tienes planes de ejercicio asignados</p>
          )}
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-2xl font-bold mb-4">Mis Planes Nutricionales</h2>
          {userPlans?.nutrition_plans?.length > 0 ? (
            userPlans.nutrition_plans.map((plan) => (
              <NutritionPlanView key={plan.id} plan={plan} />
            ))
          ) : (
            <p>No tienes planes nutricionales asignados</p>
          )}
        </div>
      </div>
    </Layout>
  );
}