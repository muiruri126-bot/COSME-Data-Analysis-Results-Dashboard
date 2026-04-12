import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { PlusIcon, PencilIcon, TrashIcon, PaperClipIcon } from '@heroicons/react/24/outline';
import api from '../lib/api';
import type { Activity, Task, User } from '../types';
import TaskModal from '../components/TaskModal';

const STATUS_BADGE: Record<string, string> = {
  Pending: 'bg-gray-100 text-gray-700',
  'In progress': 'bg-blue-100 text-blue-700',
  Complete: 'bg-green-100 text-green-700',
  Delayed: 'bg-orange-100 text-orange-700',
  Cancelled: 'bg-red-100 text-red-700',
};

export default function ActivityDetailPage() {
  const { activityId } = useParams<{ activityId: string }>();
  const [activity, setActivity] = useState<Activity | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [filter, setFilter] = useState('');

  const loadTasks = useCallback(() => {
    if (!activityId) return;
    const params: Record<string, string> = {};
    if (filter) params.status = filter;
    api.get(`/activities/${activityId}/tasks`, { params }).then((r) => setTasks(r.data.data));
  }, [activityId, filter]);

  useEffect(() => {
    if (!activityId) return;
    api.get(`/activities/${activityId}`).then((r) => setActivity(r.data));
    api.get('/users').then((r) => setUsers(r.data.data));
    loadTasks();
  }, [activityId, loadTasks]);

  const openAdd = () => {
    setEditingTask(null);
    setModalOpen(true);
  };
  const openEdit = (t: Task) => {
    setEditingTask(t);
    setModalOpen(true);
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this task?')) return;
    try {
      await api.delete(`/tasks/${id}`);
      toast.success('Deleted');
      loadTasks();
    } catch {
      toast.error('Failed to delete');
    }
  };

  const handleSave = async (data: Record<string, any>) => {
    try {
      if (editingTask) {
        await api.put(`/tasks/${editingTask.id}`, data);
        toast.success('Task updated');
      } else {
        await api.post(`/activities/${activityId}/tasks`, data);
        toast.success('Task created');
      }
      setModalOpen(false);
      loadTasks();
    } catch (err: any) {
      toast.error(err.response?.data?.error || 'Save failed');
    }
  };

  if (!activity) return <div className="p-8 text-center text-gray-500">Loading…</div>;

  return (
    <div className="space-y-6">
      {/* Activity header */}
      <div className="card">
        <div className="flex items-start justify-between">
          <div>
            <p className="font-mono text-sm text-primary-600 font-semibold">{activity.code}</p>
            <h1 className="text-xl font-bold mt-1 text-gray-900">{activity.description}</h1>
            <div className="flex gap-4 mt-3 text-sm text-gray-500">
              <span>Status: <strong className="text-gray-800">{activity.status}</strong></span>
              {activity.budget_holder && <span>Budget Holder: <strong className="text-gray-800">{activity.budget_holder.name}</strong></span>}
            </div>
          </div>
        </div>
      </div>

      {/* Toolbar */}
      <div className="flex flex-wrap items-center gap-3">
        <button onClick={openAdd} className="btn-primary">
          <PlusIcon className="h-4 w-4" /> Add Task
        </button>
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="rounded-lg border-gray-300 text-sm"
        >
          <option value="">All Statuses</option>
          {['Pending', 'In progress', 'Complete', 'Delayed', 'Cancelled'].map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>

      {/* Task table */}
      <div className="overflow-x-auto rounded-lg border bg-white shadow-sm">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              <th className="px-4 py-3">Task</th>
              <th className="px-4 py-3">Plan/Actual</th>
              <th className="px-4 py-3">Start</th>
              <th className="px-4 py-3">End</th>
              <th className="px-4 py-3">Responsible</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3 w-24">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {tasks.map((t) => (
              <tr key={t.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium">{t.name}</td>
                <td className="px-4 py-3">
                  <span className={`text-xs px-2 py-0.5 rounded ${t.plan_actual === 'Planned' ? 'bg-purple-100 text-purple-700' : 'bg-teal-100 text-teal-700'}`}>
                    {t.plan_actual}
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-600">{t.start_date}</td>
                <td className="px-4 py-3 text-gray-600">{t.end_date}</td>
                <td className="px-4 py-3 text-gray-600">{t.responsible_person || '—'}</td>
                <td className="px-4 py-3">
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${STATUS_BADGE[t.status] || ''}`}>
                    {t.status}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-1">
                    <button onClick={() => openEdit(t)} className="p-1 text-gray-400 hover:text-primary-600" title="Edit">
                      <PencilIcon className="h-4 w-4" />
                    </button>
                    <button onClick={() => handleDelete(t.id)} className="p-1 text-gray-400 hover:text-red-600" title="Delete">
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {tasks.length === 0 && (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-gray-400">
                  No tasks yet. Click "Add Task" to get started.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Modal */}
      {modalOpen && (
        <TaskModal
          task={editingTask}
          users={users}
          onSave={handleSave}
          onClose={() => setModalOpen(false)}
        />
      )}
    </div>
  );
}
