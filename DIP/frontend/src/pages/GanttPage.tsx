import { useState, useEffect } from 'react';
import api from '../lib/api';
import type { IntermediateOutcome, GanttBar } from '../types';

const STATUS_COLORS: Record<string, string> = {
  Pending: '#9CA3AF',
  'In progress': '#3B82F6',
  Complete: '#22C55E',
  Delayed: '#F97316',
  Cancelled: '#4B5563',
};

export default function GanttPage() {
  const [level, setLevel] = useState('intermediate-outcome');
  const [intOutcomes, setIntOutcomes] = useState<IntermediateOutcome[]>([]);
  const [selectedId, setSelectedId] = useState('');
  const [ganttData, setGanttData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.get('/intermediate-outcomes').then((r) => setIntOutcomes(r.data.data));
  }, []);

  const loadGantt = async () => {
    if (!selectedId) return;
    setLoading(true);
    try {
      const { data } = await api.get(`/gantt/by-${level}/${selectedId}`);
      setGanttData(data);
    } catch {
      setGanttData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedId) loadGantt();
  }, [selectedId, level]);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Gantt Chart</h1>

      <div className="flex flex-wrap items-end gap-4">
        <label className="block">
          <span className="text-sm font-medium text-gray-700">View Level</span>
          <select
            value={level}
            onChange={(e) => { setLevel(e.target.value); setSelectedId(''); setGanttData(null); }}
            className="mt-1 block w-48 rounded-lg border-gray-300"
          >
            <option value="intermediate-outcome">Intermediate Outcome</option>
            <option value="activity">Activity</option>
          </select>
        </label>

        {level === 'intermediate-outcome' && (
          <label className="block">
            <span className="text-sm font-medium text-gray-700">Select</span>
            <select
              value={selectedId}
              onChange={(e) => setSelectedId(e.target.value)}
              className="mt-1 block w-80 rounded-lg border-gray-300"
            >
              <option value="">-- Choose --</option>
              {intOutcomes.map((io) => (
                <option key={io.id} value={io.id}>
                  {io.code}: {io.description.substring(0, 60)}
                </option>
              ))}
            </select>
          </label>
        )}
      </div>

      {loading && <p className="text-gray-500">Loading…</p>}

      {ganttData && (
        <div className="space-y-4">
          {/* Summary card */}
          <div className="rounded-lg border bg-white p-4 shadow-sm">
            <div className="flex items-center gap-6">
              <div>
                <p className="text-xs text-gray-500">Level</p>
                <p className="font-medium">{ganttData.level}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Code</p>
                <p className="font-medium">{ganttData.code ?? ganttData.name}</p>
              </div>
              {ganttData.rollup && (
                <>
                  <div>
                    <p className="text-xs text-gray-500">Progress</p>
                    <p className="font-medium text-primary-600">{ganttData.rollup.progress}%</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Tasks</p>
                    <p className="font-medium">{ganttData.rollup.complete_tasks}/{ganttData.rollup.total_tasks}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Date Range</p>
                    <p className="font-medium text-sm">{ganttData.rollup.start_date} → {ganttData.rollup.end_date}</p>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Bars visualization */}
          {ganttData.bars && ganttData.bars.length > 0 && (
            <GanttBars bars={ganttData.bars} />
          )}

          {/* Groups (nested levels) */}
          {ganttData.groups && ganttData.groups.map((g: any, idx: number) => (
            <div key={idx} className="rounded-lg border bg-white p-4 shadow-sm">
              <h3 className="text-sm font-semibold text-gray-800 mb-2">
                {g.code}: {g.description?.substring(0, 80)}
              </h3>
              {g.rollup && (
                <div className="flex gap-4 text-xs text-gray-500 mb-3">
                  <span>Progress: <strong className="text-gray-800">{g.rollup.progress}%</strong></span>
                  <span>Tasks: {g.rollup.complete_tasks}/{g.rollup.total_tasks}</span>
                </div>
              )}
              {g.bars && <GanttBars bars={g.bars} />}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function GanttBars({ bars }: { bars: GanttBar[] }) {
  if (!bars.length) return null;

  // Compute time range
  const starts = bars.map((b) => new Date(b.start_date).getTime());
  const ends = bars.map((b) => new Date(b.end_date).getTime());
  const minTime = Math.min(...starts);
  const maxTime = Math.max(...ends);
  const range = maxTime - minTime || 1;

  return (
    <div className="space-y-1.5">
      {bars.map((bar) => {
        const left = ((new Date(bar.start_date).getTime() - minTime) / range) * 100;
        const width = Math.max(((new Date(bar.end_date).getTime() - new Date(bar.start_date).getTime()) / range) * 100, 2);

        return (
          <div key={bar.id} className="flex items-center gap-2">
            <div className="w-40 truncate text-xs text-gray-600 shrink-0" title={bar.label}>
              {bar.label}
            </div>
            <div className="relative flex-1 h-6 bg-gray-100 rounded">
              <div
                className="absolute h-full rounded text-[10px] text-white flex items-center px-1 overflow-hidden"
                style={{
                  left: `${left}%`,
                  width: `${width}%`,
                  backgroundColor: bar.color,
                }}
                title={`${bar.start_date} → ${bar.end_date} | ${bar.status} | ${bar.plan_actual}`}
              >
                {width > 8 && <span>{bar.duration_days}d</span>}
              </div>
            </div>
            <div className="w-16 text-xs text-gray-500 shrink-0">{bar.status}</div>
          </div>
        );
      })}
      {/* Legend */}
      <div className="flex gap-3 pt-2">
        {Object.entries(STATUS_COLORS).map(([status, color]) => (
          <div key={status} className="flex items-center gap-1 text-xs text-gray-500">
            <div className="w-3 h-3 rounded" style={{ backgroundColor: color }} />
            {status}
          </div>
        ))}
      </div>
    </div>
  );
}
