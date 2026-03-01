/* GroupedBarChart — horizontal or vertical grouped bars */
import {
  ResponsiveContainer, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
} from 'recharts';
import { COLORS, CHART_COLORS } from '../../models/constants';

interface GroupedBarChartProps {
  data: Record<string, string | number>[];
  title: string;
  bars: { dataKey: string; name: string; color?: string }[];
  xKey?: string;
  height?: number;
  formatter?: (v: number) => string;
  layout?: 'vertical' | 'horizontal';
}

export default function GroupedBarChart({
  data, title, bars, xKey = 'name',
  height = 300, formatter, layout = 'horizontal',
}: GroupedBarChartProps) {
  const fmt = formatter || ((v: number) => v.toLocaleString());

  return (
    <div style={{
      background: COLORS.cardBg, borderRadius: 12, padding: 20,
      boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
    }}>
      <h3 style={{ fontSize: 15, fontWeight: 600, color: COLORS.text, margin: '0 0 16px' }}>
        {title}
      </h3>
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={data} layout={layout === 'vertical' ? 'vertical' : 'horizontal'}
          margin={{ top: 5, right: 20, bottom: 5, left: layout === 'vertical' ? 80 : 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
          {layout === 'vertical' ? (
            <>
              <XAxis type="number" tick={{ fontSize: 12 }} />
              <YAxis type="category" dataKey={xKey} tick={{ fontSize: 12 }} width={100} />
            </>
          ) : (
            <>
              <XAxis dataKey={xKey} tick={{ fontSize: 13 }} />
              <YAxis tick={{ fontSize: 12 }} />
            </>
          )}
          <Tooltip formatter={(v: number) => fmt(v)} />
          <Legend />
          {bars.map((b, i) => (
            <Bar
              key={b.dataKey} dataKey={b.dataKey} name={b.name}
              fill={b.color || CHART_COLORS[i % CHART_COLORS.length]}
              radius={layout === 'vertical' ? [0, 4, 4, 0] : [4, 4, 0, 0]}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
