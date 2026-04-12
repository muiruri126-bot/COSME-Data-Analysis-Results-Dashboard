import { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, Legend } from 'recharts';
import api from '../lib/api';
import type { KPIs } from '../types';

const STATUS_COLORS: Record<string, string> = {
  Pending: '#9CA3AF',
  'In progress': '#3B82F6',
  Complete: '#22C55E',
  Delayed: '#F97316',
  Cancelled: '#4B5563',
};

export default function DashboardPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/dashboard/executive')
      .then((r) => setData(r.data))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-8 text-center text-gray-500">Loading dashboard…</div>;
  if (!data) return <div className="p-8 text-center text-red-500">Failed to load dashboard</div>;

  const kpis: KPIs = data.kpis;
  const pieData = Object.entries(kpis.tasks_by_status).map(([name, value]) => ({ name, value }));

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Executive Dashboard</h1>

      {/* KPI cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <KPICard label="Total Tasks" value={kpis.total_tasks} />
        <KPICard label="Complete" value={kpis.complete} color="text-green-600" />
        <KPICard label="In Progress" value={kpis.in_progress} color="text-blue-600" />
        <KPICard label="Delayed" value={kpis.delayed} color="text-orange-600" />
        <KPICard label="% Complete" value={`${kpis.percent_complete}%`} color="text-primary-600" />
        <KPICard label="On-Time Rate" value={`${kpis.on_time_rate}%`} color="text-teal-600" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Status pie chart */}
        <div className="rounded-lg border bg-white p-4 shadow-sm">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Tasks by Status</h2>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
                {pieData.map((entry) => (
                  <Cell key={entry.name} fill={STATUS_COLORS[entry.name] || '#ccc'} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Workload bar chart */}
        <div className="rounded-lg border bg-white p-4 shadow-sm">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Workload by Person</h2>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={data.workload} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis type="category" dataKey="name" width={100} tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="Complete" stackId="a" fill="#22C55E" />
              <Bar dataKey="In progress" stackId="a" fill="#3B82F6" />
              <Bar dataKey="Delayed" stackId="a" fill="#F97316" />
              <Bar dataKey="Pending" stackId="a" fill="#9CA3AF" />
              <Legend />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Delayed ageing */}
      <div className="rounded-lg border bg-white p-4 shadow-sm">
        <h2 className="text-sm font-semibold text-gray-700 mb-4">Delayed Task Ageing</h2>
        <div className="grid grid-cols-4 gap-4 text-center">
          {Object.entries(data.delayed_ageing as Record<string, number>).map(([bucket, count]) => (
            <div key={bucket} className="p-3 rounded-lg bg-orange-50">
              <p className="text-2xl font-bold text-orange-600">{count}</p>
              <p className="text-xs text-gray-500">{bucket} days overdue</p>
            </div>
          ))}
        </div>
      </div>

      {/* Top delayed tasks */}
      {data.top_delayed.length > 0 && (
        <div className="rounded-lg border bg-white p-4 shadow-sm">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Top Delayed Tasks</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase">
                  <th className="px-3 py-2">Task</th>
                  <th className="px-3 py-2">Activity</th>
                  <th className="px-3 py-2">Due Date</th>
                  <th className="px-3 py-2">Days Overdue</th>
                  <th className="px-3 py-2">Responsible</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {data.top_delayed.map((t: any) => (
                  <tr key={t.id} className="hover:bg-gray-50">
                    <td className="px-3 py-2">{t.name}</td>
                    <td className="px-3 py-2 font-mono text-xs">{t.activity_code}</td>
                    <td className="px-3 py-2">{t.end_date}</td>
                    <td className="px-3 py-2 text-orange-600 font-medium">{t.days_overdue}</td>
                    <td className="px-3 py-2">{t.responsible || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

function KPICard({ label, value, color = 'text-gray-900' }: { label: string; value: string | number; color?: string }) {
  return (
    <div className="card flex flex-col items-center justify-center text-center">
      <p className={`text-3xl font-bold ${color}`}>{value}</p>
      <p className="text-xs text-gray-500 mt-1.5 uppercase tracking-wide font-medium">{label}</p>
    </div>
  );
}
