import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { axiosPrivate } from '../api/axios';
import { LineChart, BarChart, XAxis, YAxis, Tooltip, Line, Bar, ResponsiveContainer } from 'recharts';

export function DashboardAnalytics({ userId }) {
  const [periodo, setPeriodo] = useState('mes');
  
  const { data: estadisticas } = useQuery({
    queryKey: ['estadisticas-usuario', userId, periodo],
    queryFn: async () => {
      const response = await axiosPrivate.get(`/user/progress/stats?range=${periodo}`);
      return response.data;
    }
  });

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold">Panel de Rendimiento</h2>
          <select 
            value={periodo} 
            onChange={(e) => setPeriodo(e.target.value)}
            className="border rounded-md p-2"
          >
            <option value="semana">Esta Semana</option>
            <option value="mes">Este Mes</option>
            <option value="año">Este Año</option>
          </select>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <TarjetaEstadistica
            titulo="Entrenamientos Completados"
            valor={estadisticas?.entrenamientosCompletados}
            total={estadisticas?.totalEntrenamientos}
          />
          <TarjetaEstadistica
            titulo="Adherencia Nutricional"
            valor={estadisticas?.adherenciaNutricional}
            unidad="%"
          />
          <TarjetaEstadistica
            titulo="Objetivos Alcanzados"
            valor={estadisticas?.objetivosAlcanzados}
            total={estadisticas?.totalObjetivos}
          />
        </div>

        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-semibold mb-4">Progreso de Peso</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={estadisticas?.progresoSemanal}>
                  <XAxis dataKey="fecha" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="peso" stroke="#2563eb" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-4">Cumplimiento de Ejercicios</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={estadisticas?.cumplimientoEjercicios}>
                  <XAxis dataKey="nombre" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="completado" fill="#2563eb" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-4">Resumen de Objetivos</h2>
        <div className="space-y-4">
          {estadisticas?.objetivos?.map((objetivo) => (
            <div key={objetivo.id} className="bg-gray-50 p-4 rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <h4 className="font-medium">{objetivo.descripcion}</h4>
                <span className={`px-2 py-1 rounded text-sm ${
                  objetivo.completado ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {objetivo.completado ? 'Completado' : 'En Progreso'}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full"
                  style={{ width: `${objetivo.progreso}%` }}
                />
              </div>
              <p className="mt-2 text-sm text-gray-600">{objetivo.notas}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function TarjetaEstadistica({ titulo, valor, total, unidad }) {
  const porcentaje = total ? (valor / total * 100).toFixed(1) : null;

  return (
    <div className="bg-gray-50 p-4 rounded-lg">
      <h3 className="text-sm font-medium text-gray-500">{titulo}</h3>
      <div className="mt-1">
        <p className="text-2xl font-semibold text-gray-900">
          {total ? `${valor}/${total}` : `${valor}${unidad || ''}`}
        </p>
        {porcentaje && (
          <p className="text-sm text-gray-600">{porcentaje}% completado</p>
        )}
      </div>
    </div>
  );
}
