import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { PlusIcon, PencilIcon } from '@heroicons/react/24/outline';
import api from '../lib/api';
import type { User, BudgetHolder } from '../types';

export default function AdminUsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [budgetHolders, setBudgetHolders] = useState<BudgetHolder[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<User | null>(null);

  const load = () => {
    api.get('/admin/users').then((r) => setUsers(r.data.data));
    api.get('/budget-holders').then((r) => setBudgetHolders(r.data.data));
  };

  useEffect(load, []);

  const openAdd = () => { setEditing(null); setModalOpen(true); };
  const openEdit = (u: User) => { setEditing(u); setModalOpen(true); };

  const handleSave = async (data: Record<string, any>) => {
    try {
      if (editing) {
        await api.put(`/admin/users/${editing.id}`, data);
        toast.success('User updated');
      } else {
        await api.post('/admin/users', data);
        toast.success('User created');
      }
      setModalOpen(false);
      load();
    } catch (err: any) {
      toast.error(err.response?.data?.error || 'Save failed');
    }
  };

  const toggleActive = async (u: User) => {
    try {
      if (u.is_active) {
        await api.delete(`/admin/users/${u.id}`);
        toast.success('User deactivated');
      } else {
        await api.put(`/admin/users/${u.id}`, { is_active: true });
        toast.success('User activated');
      }
      load();
    } catch {
      toast.error('Action failed');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">User Management</h1>
        <button
          onClick={openAdd}
          className="btn-primary"
        >
          <PlusIcon className="h-4 w-4" /> Add User
        </button>
      </div>

      <div className="overflow-x-auto rounded-lg border bg-white shadow-sm">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Email</th>
              <th className="px-4 py-3">Roles</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3 w-24">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {users.map((u) => (
              <tr key={u.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium">{u.full_name}</td>
                <td className="px-4 py-3 text-gray-600">{u.email}</td>
                <td className="px-4 py-3">
                  {u.roles.map((r) => (
                    <span key={r} className="mr-1 text-xs bg-primary-100 text-primary-700 px-2 py-0.5 rounded-full">
                      {r}
                    </span>
                  ))}
                </td>
                <td className="px-4 py-3">
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${u.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                    {u.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex gap-1">
                    <button onClick={() => openEdit(u)} className="p-1 text-gray-400 hover:text-primary-600">
                      <PencilIcon className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => toggleActive(u)}
                      className={`text-xs px-2 py-0.5 rounded ${u.is_active ? 'text-red-600 hover:bg-red-50' : 'text-green-600 hover:bg-green-50'}`}
                    >
                      {u.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {modalOpen && (
        <UserModal
          user={editing}
          budgetHolders={budgetHolders}
          onSave={handleSave}
          onClose={() => setModalOpen(false)}
        />
      )}
    </div>
  );
}

function UserModal({
  user,
  budgetHolders,
  onSave,
  onClose,
}: {
  user: User | null;
  budgetHolders: BudgetHolder[];
  onSave: (data: Record<string, any>) => void;
  onClose: () => void;
}) {
  const [fullName, setFullName] = useState(user?.full_name ?? '');
  const [email, setEmail] = useState(user?.email ?? '');
  const [password, setPassword] = useState('');
  const [phone, setPhone] = useState(user?.phone ?? '');
  const [bhId, setBhId] = useState(user?.budget_holder_id ?? '');
  const [roles, setRoles] = useState<string[]>(user?.roles ?? []);

  const allRoles = ['Admin', 'ME_Specialist', 'Budget_Holder', 'Implementer', 'Viewer'];

  const toggleRole = (r: string) => {
    setRoles((prev) => (prev.includes(r) ? prev.filter((x) => x !== r) : [...prev, r]));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const data: Record<string, any> = {
      full_name: fullName,
      email,
      phone: phone || undefined,
      budget_holder_id: bhId || undefined,
      roles,
    };
    if (password) data.password = password;
    onSave(data);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={onClose}>
      <form
        onClick={(e) => e.stopPropagation()}
        onSubmit={handleSubmit}
        className="w-full max-w-md rounded-xl bg-white p-6 shadow-2xl space-y-4"
      >
        <h2 className="text-lg font-bold">{user ? 'Edit User' : 'New User'}</h2>

        <label className="block">
          <span className="text-sm font-medium text-gray-700">Full Name *</span>
          <input required value={fullName} onChange={(e) => setFullName(e.target.value)} className="mt-1 block w-full rounded-lg border-gray-300" />
        </label>

        <label className="block">
          <span className="text-sm font-medium text-gray-700">Email *</span>
          <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} className="mt-1 block w-full rounded-lg border-gray-300" />
        </label>

        <label className="block">
          <span className="text-sm font-medium text-gray-700">Password {user ? '(leave blank to keep)' : '*'}</span>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required={!user} className="mt-1 block w-full rounded-lg border-gray-300" />
        </label>

        <label className="block">
          <span className="text-sm font-medium text-gray-700">Phone</span>
          <input value={phone} onChange={(e) => setPhone(e.target.value)} className="mt-1 block w-full rounded-lg border-gray-300" />
        </label>

        <label className="block">
          <span className="text-sm font-medium text-gray-700">Budget Holder</span>
          <select value={bhId} onChange={(e) => setBhId(e.target.value)} className="mt-1 block w-full rounded-lg border-gray-300">
            <option value="">-- None --</option>
            {budgetHolders.map((bh) => (
              <option key={bh.id} value={bh.id}>{bh.name}</option>
            ))}
          </select>
        </label>

        <div>
          <span className="text-sm font-medium text-gray-700">Roles</span>
          <div className="mt-1 flex flex-wrap gap-2">
            {allRoles.map((r) => (
              <label key={r} className="flex items-center gap-1 text-sm">
                <input type="checkbox" checked={roles.includes(r)} onChange={() => toggleRole(r)} className="rounded" />
                {r}
              </label>
            ))}
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-3 border-t">
          <button type="button" onClick={onClose} className="btn-secondary">Cancel</button>
          <button type="submit" className="btn-primary">{user ? 'Save' : 'Create'}</button>
        </div>
      </form>
    </div>
  );
}
