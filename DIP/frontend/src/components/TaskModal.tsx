import { useState, useEffect } from 'react';
import type { Task, User } from '../types';

interface Props {
  task: Task | null;
  users: User[];
  onSave: (data: Record<string, any>) => void;
  onClose: () => void;
}

export default function TaskModal({ task, users, onSave, onClose }: Props) {
  const [name, setName] = useState(task?.name ?? '');
  const [planActual, setPlanActual] = useState<string>(task?.plan_actual ?? 'Planned');
  const [startDate, setStartDate] = useState(task?.start_date_iso ?? '');
  const [endDate, setEndDate] = useState(task?.end_date_iso ?? '');
  const [status, setStatus] = useState(task?.status ?? 'Pending');
  const [responsible, setResponsible] = useState(task?.responsible_person ?? '');
  const [evidence, setEvidence] = useState(task?.completion_evidence ?? '');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave({
      name,
      plan_actual: planActual,
      start_date: startDate,
      end_date: endDate,
      status,
      responsible_person: responsible || null,
      completion_evidence: evidence,
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={onClose}>
      <form
        onClick={(e) => e.stopPropagation()}
        onSubmit={handleSubmit}
        className="w-full max-w-lg rounded-xl bg-white p-6 shadow-2xl space-y-5 max-h-[90vh] overflow-y-auto animate-in"
      >
        <h2 className="text-lg font-bold text-gray-900">{task ? 'Edit Task' : 'New Task'}</h2>

        <label className="block">
          <span className="text-sm font-medium text-gray-700">Task Name *</span>
          <input
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
          />
        </label>

        <div className="grid grid-cols-2 gap-4">
          <label className="block">
            <span className="text-sm font-medium text-gray-700">Plan/Actual</span>
            <select
              value={planActual}
              onChange={(e) => setPlanActual(e.target.value)}
              className="mt-1 block w-full rounded-lg border-gray-300"
            >
              <option>Planned</option>
              <option>Actual</option>
            </select>
          </label>

          <label className="block">
            <span className="text-sm font-medium text-gray-700">Status</span>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="mt-1 block w-full rounded-lg border-gray-300"
            >
              {['Pending', 'In progress', 'Complete', 'Delayed', 'Cancelled'].map((s) => (
                <option key={s}>{s}</option>
              ))}
            </select>
          </label>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <label className="block">
            <span className="text-sm font-medium text-gray-700">Start Date *</span>
            <input
              type="date"
              required
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="mt-1 block w-full rounded-lg border-gray-300"
            />
          </label>
          <label className="block">
            <span className="text-sm font-medium text-gray-700">End Date *</span>
            <input
              type="date"
              required
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="mt-1 block w-full rounded-lg border-gray-300"
            />
          </label>
        </div>

        <label className="block">
          <span className="text-sm font-medium text-gray-700">Responsible</span>
          <input
            type="text"
            value={responsible}
            onChange={(e) => setResponsible(e.target.value)}
            className="mt-1 block w-full rounded-lg border-gray-300"
            placeholder="Enter name of responsible person"
          />
        </label>

        {status === 'Complete' && (
          <label className="block">
            <span className="text-sm font-medium text-gray-700">Evidence *</span>
            <textarea
              required
              value={evidence}
              onChange={(e) => setEvidence(e.target.value)}
              rows={2}
              className="mt-1 block w-full rounded-lg border-gray-300"
              placeholder="Link or description of evidence…"
            />
          </label>
        )}

        <div className="flex justify-end gap-3 pt-3 border-t">
          <button
            type="button"
            onClick={onClose}
            className="btn-secondary"
          >
            Cancel
          </button>
          <button
            type="submit"
            className="btn-primary"
          >
            {task ? 'Save Changes' : 'Create Task'}
          </button>
        </div>
      </form>
    </div>
  );
}
