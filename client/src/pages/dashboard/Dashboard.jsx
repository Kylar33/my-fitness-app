import { useQuery } from '@tanstack/react-query';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';
import api from '../../lib/axios';
import { Card } from '../../components/ui/Card';

function Dashboard() {
  const { data: stats } = useQuery(['dashboard-stats'], () =>
    api.get('/stats').then(res => res.data)
  );

  const { data: recentActivity } = useQuery(['recent-activity'], () =>
    api.get('/activity').then(res => res.data)
  );

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <div className="text-sm text-gray-600">Total Users</div>
          <div className="text-2xl font-bold">{stats?.totalUsers}</div>
        </Card>
        <Card>
          <div className="text-sm text-gray-600">Active Routines</div>
          <div className="text-2xl font-bold">{stats?.activeRoutines}</div>
        </Card>
        <Card>
          <div className="text-sm text-gray-600">Nutrition Plans</div>
          <div className="text-2xl font-bold">{stats?.nutritionPlans}</div>
        </Card>
      </div>

      <Card>
        <h2 className="text-lg font-semibold mb-4">User Activity</h2>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={stats?.activityData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card>
        <h2 className="text-lg font-semibold mb-4">Recent Activity</h2>
        <div className="space-y-2">
          {recentActivity?.map((activity, index) => (
            <div key={index} className="flex justify-between items-center">
              <div>
                <div className="font-medium">{activity.description}</div>
                <div className="text-sm text-gray-600">{activity.user}</div>
              </div>
              <div className="text-sm text-gray-500">
                {formatRelative(new Date(activity.date), new Date())}
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

export default Dashboard;