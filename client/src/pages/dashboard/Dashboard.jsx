import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import api, { endpoints } from '../../lib/axios';
import { UserForm } from '../../components/users/UserForm';
import {
 BarChart,
 Bar,
 XAxis,
 YAxis,
 CartesianGrid,
 Tooltip,
 ResponsiveContainer
} from 'recharts';
import { format } from 'date-fns';
import { Users, Dumbbell, Apple } from 'lucide-react';

export function Dashboard() {
  const [showUserForm, setShowUserForm] = useState(false);
 const { data: usersData, error: usersError } = useQuery({
   queryKey: ['users'],
   queryFn: async () => {
    console.log('Token:', localStorage.getItem('token'));
    try {
      const response = await api.get(endpoints.users);
      console.log('Users response:', response);
      return response;
    } catch (error) {
      console.error('Users error:', error);
      throw error;
    }
  } 
 });

 const { data: routinesData } = useQuery({
   queryKey: ['routines'],
   queryFn: () => api.get(endpoints.routines)
 });

 const { data: nutritionData } = useQuery({
   queryKey: ['nutrition-plans'],
   queryFn: () => api.get(endpoints.nutritionPlans)
 });

 const { data: trainersData } = useQuery({
   queryKey: ['trainers'],
   queryFn: () => api.get(endpoints.trainers)
 });

 const stats = {
   users: usersData?.data?.length || 0,
   routines: routinesData?.data?.length || 0,
   plans: nutritionData?.data?.length || 0
 };

 const activityData = usersData?.data?.reduce((acc, user) => {
   const date = format(new Date(user.created_at), 'MMM dd');
   const existingDate = acc.find(item => item.date === date);
   
   if (existingDate) {
     existingDate.users += 1;
   } else {
     acc.push({ date, users: 1 });
   }
   
   return acc;
 }, []) || [];

 useEffect(() => {
  console.log('usersData:', usersData);
  console.log('usersError:', usersError);
}, [usersData, usersError]);

 return (
   <div className="p-6 space-y-6">
     <h1 className="text-2xl font-bold">Dashboard</h1>
     
     <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
       <StatsCard
         title="Total Users"
         value={stats.users}
         icon={<Users className="h-6 w-6 text-blue-500" />}
       />
       <StatsCard
         title="Active Routines"
         value={stats.routines}
         icon={<Dumbbell className="h-6 w-6 text-green-500" />}
       />
       <StatsCard
         title="Nutrition Plans"
         value={stats.plans}
         icon={<Apple className="h-6 w-6 text-red-500" />}
       />
     </div>

     <Card className="p-6">
       <h2 className="text-lg font-semibold mb-4">User Growth</h2>
       <div className="h-[300px]">
         <ResponsiveContainer width="100%" height="100%">
           <BarChart data={activityData}>
             <CartesianGrid strokeDasharray="3 3" />
             <XAxis dataKey="date" />
             <YAxis />
             <Tooltip />
             <Bar dataKey="users" fill="#3b82f6" />
           </BarChart>
         </ResponsiveContainer>
       </div>
     </Card>
     <div className="flex justify-between items-center">
 <h1 className="text-2xl font-bold">Dashboard</h1>
 <Button onClick={() => setShowUserForm(true)}>Add User</Button>
</div>

{showUserForm && (
 <UserForm onClose={() => setShowUserForm(false)} />
)} 
   </div>
 );
}

function StatsCard({ title, value, icon }) {
 return (
   <Card className="p-6">
     <div className="flex items-center justify-between">
       <div>
         <p className="text-sm text-gray-600">{title}</p>
         <p className="text-2xl font-bold mt-1">{value}</p>
       </div>
       {icon}
     </div>
   </Card>
 );
}