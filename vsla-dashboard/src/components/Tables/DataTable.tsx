/* DataTable — simple sortable table with copy-to-clipboard */
import { useState } from 'react';
import { COLORS } from '../../models/constants';

interface DataTableProps {
  title: string;
  columns: { key: string; label: string; align?: 'left' | 'right' | 'center' }[];
  rows: Record<string, string | number>[];
}

export default function DataTable({ title, columns, rows }: DataTableProps) {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = () => {
    const header = columns.map(c => c.label).join('\t');
    const body = rows.map(r => columns.map(c => r[c.key] ?? '').join('\t')).join('\n');
    navigator.clipboard.writeText(`${header}\n${body}`).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const downloadCSV = () => {
    const header = columns.map(c => c.label).join(',');
    const body = rows.map(r => columns.map(c => `"${r[c.key] ?? ''}"`).join(',')).join('\n');
    const blob = new Blob([`${header}\n${body}`], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${title.replace(/\s+/g, '_')}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div style={{
      background: COLORS.cardBg, borderRadius: 12, padding: 20,
      boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <h3 style={{ fontSize: 15, fontWeight: 600, color: COLORS.text, margin: 0 }}>{title}</h3>
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={copyToClipboard} style={btnStyle} title="Copy table data for pasting into Excel/Word">
            {copied ? '✓ Copied!' : '📋 Copy'}
          </button>
          <button onClick={downloadCSV} style={btnStyle} title="Download as CSV file">
            ⬇ CSV
          </button>
        </div>
      </div>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
          <thead>
            <tr>
              {columns.map(col => (
                <th key={col.key} style={{
                  padding: '10px 12px', textAlign: col.align || 'left',
                  borderBottom: `2px solid ${COLORS.primary}`,
                  color: COLORS.text, fontWeight: 600, fontSize: 12,
                  whiteSpace: 'nowrap',
                }}>
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={i} style={{ background: i % 2 === 0 ? '#fafbfc' : '#fff' }}>
                {columns.map(col => (
                  <td key={col.key} style={{
                    padding: '8px 12px', textAlign: col.align || 'left',
                    borderBottom: '1px solid #eee', whiteSpace: 'nowrap',
                  }}>
                    {row[col.key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const btnStyle: React.CSSProperties = {
  padding: '6px 12px', borderRadius: 6,
  border: `1px solid ${COLORS.neutral}`, background: '#fff',
  fontSize: 12, fontWeight: 500, cursor: 'pointer',
  color: COLORS.text,
};
