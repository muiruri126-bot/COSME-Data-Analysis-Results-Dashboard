import { useState, useEffect } from 'react';
import { ArrowDownTrayIcon } from '@heroicons/react/24/outline';
import api from '../lib/api';

type ReportType = 'activity-progress' | 'output-completion' | 'variance' | 'workload';

export default function ReportsPage() {
  const [reportType, setReportType] = useState<ReportType>('activity-progress');
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const loadReport = async (type: ReportType) => {
    setReportType(type);
    setLoading(true);
    try {
      const { data: res } = await api.get(`/reports/${type}`);
      setData(res.data);
    } catch {
      setData([]);
    } finally {
      setLoading(false);
    }
  };

  const exportExcel = async () => {
    try {
      const response = await api.get('/reports/dip-export?format=excel', { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'COSME_DIP_Export.xlsx');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch {
      // Fallback to direct URL
      window.open('/api/v1/reports/dip-export?format=excel', '_blank');
    }
  };

  // Auto-load first report on mount
  useEffect(() => { loadReport('activity-progress'); }, []);

  const tabs: { key: ReportType; label: string }[] = [
    { key: 'activity-progress', label: 'Activity Progress' },
    { key: 'output-completion', label: 'Output Completion' },
    { key: 'variance', label: 'Variance' },
    { key: 'workload', label: 'Workload' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Reports</h1>
        <button
          onClick={exportExcel}
          className="flex items-center gap-1 rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white shadow hover:bg-green-700"
        >
          <ArrowDownTrayIcon className="h-4 w-4" /> Export Full DIP
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => loadReport(t.key)}
            className={`pb-2 px-3 text-sm font-medium border-b-2 transition ${
              reportType === t.key
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {loading && <p className="text-gray-500">Loading…</p>}

      {!loading && data.length > 0 && (
        <div className="overflow-x-auto rounded-lg border bg-white shadow-sm">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {Object.keys(data[0]).map((k) => (
                  <th key={k} className="px-3 py-2 whitespace-nowrap">
                    {k.replace(/_/g, ' ')}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y">
              {data.map((row, idx) => (
                <tr key={idx} className="hover:bg-gray-50">
                  {Object.values(row).map((v, ci) => (
                    <td key={ci} className="px-3 py-2 whitespace-nowrap">
                      {v === null ? '—' : String(v)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {!loading && data.length === 0 && reportType && (
        <p className="text-gray-400 text-sm">No data available for this report.</p>
      )}
    </div>
  );
}
