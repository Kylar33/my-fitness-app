import { useUsers } from '../../hooks/useUsers';
import { UserForm } from './UserForm';
import { useState } from 'react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';

export function UserList() {
  const { users, deleteUser } = useUsers();
  const [selectedUser, setSelectedUser] = useState(null);
  const [isFormOpen, setIsFormOpen] = useState(false);

  return (
    <div className="space-y-4">
      <div className="flex justify-between">
        <h1 className="text-2xl font-bold">Users</h1>
        <Button onClick={() => setIsFormOpen(true)}>Add User</Button>
      </div>

      <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
        {users.data?.map(user => (
          <Card key={user.id}>
            <div className="flex justify-between">
              <div>
                <h3 className="font-semibold">{user.first_name} {user.last_name}</h3>
                <p className="text-gray-600">{user.email}</p>
              </div>
              <div className="space-x-2">
                <button 
                  onClick={() => {
                    setSelectedUser(user);
                    setIsFormOpen(true);
                  }}
                  className="text-blue-500"
                >
                  Edit
                </button>
                <button 
                  onClick={() => deleteUser.mutate(user.id)}
                  className="text-red-500"
                >
                  Delete
                </button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {isFormOpen && (
        <UserForm 
          user={selectedUser} 
          onClose={() => {
            setIsFormOpen(false);
            setSelectedUser(null);
          }}
        />
      )}
    </div>
  );
}