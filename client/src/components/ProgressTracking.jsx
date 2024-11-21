import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { LineChart, BarChart, Line, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export function ProgressTracking() {
  const [timeRange, setTimeRange] = useState('month');
  
  const { data: progressData } = useQuery({
    queryKey: ['progress-metrics', timeRange],
    queryFn: async () => {
      const response = await axiosPrivate.get('/user/progress/stats', {
        params: { range: timeRange }
      });
      return response.data;
    }
  });

  return (
    <div className="grid gap-6">
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold">Progreso General</h2>
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="border rounded p-2"
          >
            <option value="week">Última Semana</option>
            <option value="month">Último Mes</option>
            <option value="year">Último Año</option>
          </select>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-6">
          <MetricCard 
            title="Peso Actual"
            value={progressData?.currentWeight}
            change={progressData?.weightChange}
            unit="kg"
          />
          <MetricCard
            title="% Grasa Corporal"
            value={progressData?.currentBodyFat}
            change={progressData?.bodyFatChange}
            unit="%"
          />
          <MetricCard
            title="Masa Muscular"
            value={progressData?.currentMuscleMass}
            change={progressData?.muscleMassChange}
            unit="kg"
          />
        </div>

        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={progressData?.history}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line 
                type="monotone" 
                dataKey="weight" 
                stroke="#2563eb" 
                name="Peso"
              />
              <Line 
                type="monotone" 
                dataKey="bodyFat" 
                stroke="#dc2626" 
                name="Grasa Corporal"
              />
              <Line 
                type="monotone" 
                dataKey="muscleMass" 
                stroke="#16a34a" 
                name="Masa Muscular"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Cumplimiento de Ejercicios</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={progressData?.workoutCompletion}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar 
                  dataKey="completed" 
                  fill="#2563eb" 
                  name="Ejercicios Completados"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Adherencia Nutricional</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={progressData?.nutritionAdherence}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar 
                  dataKey="adherence" 
                  fill="#16a34a" 
                  name="% Cumplimiento"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ title, value, change, unit }) {
  return (
    <div className="bg-gray-50 p-4 rounded-lg">
      <h4 className="text-sm font-medium text-gray-500">{title}</h4>
      <div className="mt-2 flex items-baseline">
        <p className="text-2xl font-semibold text-gray-900">
          {value} {unit}
        </p>
        {change && (
          <span className={`ml-2 text-sm ${
            change > 0 ? 'text-green-600' : 'text-red-600'
          }`}>
            {change > 0 ? '+' : ''}{change} {unit}
          </span>
        )}
      </div>
    </div>
  );
}