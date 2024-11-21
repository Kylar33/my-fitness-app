import { useState } from 'react';
import Layout from '../../components/Layout';
import UserList from './UserList';
import UserForm from './UserForm';
import WorkoutPlanList from './WorkoutPlanList';
import NutritionPlanList from './NutritionPlanList';
import WorkoutPlansSection from './WorkoutPlansSection';
import NutritionPlansSection from './NutritionPlansSection';

export default function TrainerDashboard() {
  const [activeTab, setActiveTab] = useState('users');
  const [showForm, setShowForm] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);

  const renderContent = () => {
    if (showForm) {
      switch (activeTab) {
        case 'users':
          return (
            <UserForm
              user={selectedItem}
              onClose={() => {
                setShowForm(false);
                setSelectedItem(null);
              }}
            />
          );
        case 'workouts':
            return <WorkoutPlansSection />;


        case 'nutrition':
          return <NutritionPlansSection />;
      }
    }

    switch (activeTab) {
      case 'users':
        return (
          <UserList
            onEdit={(user) => {
              setSelectedItem(user);
              setShowForm(true);
            }}
          />
        );
      case 'workouts':
        return (
          <WorkoutPlanList
            onEdit={(plan) => {
              setSelectedItem(plan);
              setShowForm(true);
            }}
          />
        );
      case 'nutrition':
        return (
          <NutritionPlanList
            onEdit={(plan) => {
              setSelectedItem(plan);
              setShowForm(true);
            }}
          />
        );
        case 'routines':
          return <RoutineManagement />;
    }
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">Panel de Entrenador</h1>
          <button
            onClick={() => {
              setSelectedItem(null);
              setShowForm(true);
            }}
            className="bg-blue-500 text-white px-4 py-2 rounded"
          >
            Nuevo {activeTab === 'users' ? 'Usuario' : activeTab === 'workouts' ? 'Plan de Ejercicios' : 'Plan Nutricional'}
          </button>
        </div>

        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('users')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'users'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Usuarios
            </button>
            <button
              onClick={() => setActiveTab('workouts')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'workouts'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Planes de Ejercicio
            </button>
            <button
              onClick={() => setActiveTab('nutrition')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'nutrition'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Planes Nutricionales
            </button>
          </nav>
        </div>

        {renderContent()}
      </div>
    </Layout>
  );
}