import { useQuery } from '@tanstack/react-query';
import { axiosPrivate } from '../api/axios';

export default function TrainerStats() {
  const { data: stats } = useQuery({
    queryKey: ['trainer-stats'],
    queryFn: async () => {
      const response = await axiosPrivate.get('/trainer/dashboard/stats');
      return response.data;
    }
  });

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium mb-2">Usuarios Activos</h3>
        <p className="text-3xl font-bold">{stats?.activeUsers || 0}</p>
      </div>
      
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium mb-2">Planes Asignados</h3>
        <p className="text-3xl font-bold">{stats?.assignedPlans || 0}</p>
      </div>
      
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium mb-2">Tasa de Completado</h3>
        <p className="text-3xl font-bold">{stats?.completionRate || 0}%</p>
      </div>
    </div>
  );
}