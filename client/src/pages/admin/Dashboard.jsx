import { useState } from 'react';
import Layout from '../../components/Layout';
import TrainerManagement from './sections/TrainerManagement';
import UserManagement from './sections/UserManagement';
import WorkoutPlanManagement from './sections/WorkoutPlanManagement';
import NutritionPlanManagement from './sections/NutritionPlanManagement';
import RoutineManagement from './sections/RoutineManagement';
import { ProgressTracking } from '../../components/ProgressTracking';

export default function AdminDashboard() {
  const [activeSection, setActiveSection] = useState('trainers');

  const renderSection = () => {
    switch (activeSection) {
      case 'trainers':
        return <TrainerManagement />;
      case 'users':
        return <UserManagement />;
      case 'workouts':
        return <WorkoutPlanManagement />;
      case 'nutrition':
        return <NutritionPlanManagement />;
      case 'routines':
        return <RoutineManagement />;
      default:
        return <TrainerManagement />;
    }
  };

  return (
    <Layout>
      <div className="min-h-screen bg-gray-100">
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">Panel de Administración</h1>

          <nav className="flex space-x-4 border-b border-gray-200 mb-6">
            <button
              onClick={() => setActiveSection('trainers')}
              className={`pb-4 ${
                activeSection === 'trainers'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Entrenadores
            </button>
            <button
              onClick={() => setActiveSection('users')}
              className={`pb-4 ${
                activeSection === 'users'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Usuarios
            </button>
            <button
              onClick={() => setActiveSection('workouts')}
              className={`pb-4 ${
                activeSection === 'workouts'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Planes de Ejercicio
            </button>
            <button
              onClick={() => setActiveSection('nutrition')}
              className={`pb-4 ${
                activeSection === 'nutrition'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Planes Nutricionales
            </button>
            <button
              onClick={() => setActiveSection('routines')}
              className={`pb-4 ${
                activeSection === 'routines'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Rutinas
            </button>
          </nav>

          {renderSection()}
        </div>
      </div>
    </Layout>
  );
}
