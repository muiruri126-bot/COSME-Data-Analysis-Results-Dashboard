/* DonutChart — pie/donut chart for band distributions */
import {
  ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend,
} from 'recharts';
import { COLORS, CHART_COLORS } from '../../models/constants';

interface DonutChartProps {
  data: { name: string; value: number }[];
  title: string;
  height?: number;
  formatter?: (v: number) => string;
  colors?: string[];
}

export default function DonutChart({ data, title, height = 300, formatter, colors }: DonutChartProps) {
  const palette = colors || CHART_COLORS;
  const fmt = formatter || ((v: number) => `${(v * 100).toFixed(0)}%`);

  return (
    <div style={{
      background: COLORS.cardBg, borderRadius: 12, padding: 20,
      boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
    }}>
      <h3 style={{ fontSize: 15, fontWeight: 600, color: COLORS.text, margin: '0 0 16px' }}>
        {title}
      </h3>
      <ResponsiveContainer width="100%" height={height}>
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            cx="50%" cy="50%"
            innerRadius={55} outerRadius={90}
            paddingAngle={2}
            label={({ name, value }) => `${name}: ${fmt(value)}`}
            labelLine
          >
            {data.map((_entry, index) => (
              <Cell key={index} fill={palette[index % palette.length]} />
            ))}
          </Pie>
          <Tooltip formatter={(v: number) => fmt(v)} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
