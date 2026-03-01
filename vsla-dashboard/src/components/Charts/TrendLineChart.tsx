/* TrendLineChart — Q2→Q3→Q4 line/bar trend */
import {
  ResponsiveContainer, ComposedChart, Line, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
} from 'recharts';
import { COLORS } from '../../models/constants';

interface TrendLineChartProps {
  data: { quarter: string; value: number; value2?: number }[];
  title: string;
  yLabel?: string;
  color?: string;
  color2?: string;
  name?: string;
  name2?: string;
  type?: 'line' | 'bar' | 'combo';
  formatter?: (v: number) => string;
  height?: number;
}

export default function TrendLineChart({
  data, title, yLabel, color, color2, name, name2,
  type = 'line', formatter, height = 300,
}: TrendLineChartProps) {
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
        <ComposedChart data={data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
          <XAxis dataKey="quarter" tick={{ fontSize: 13 }} />
          <YAxis tick={{ fontSize: 12 }} label={yLabel ? { value: yLabel, angle: -90, position: 'insideLeft', fontSize: 12 } : undefined} />
          <Tooltip formatter={(v: number) => fmt(v)} />
          {(name2 || data.some(d => d.value2 !== undefined)) && <Legend />}

          {type === 'line' || type === 'combo' ? (
            <Line
              type="monotone" dataKey="value" name={name || 'Value'}
              stroke={color || COLORS.primary} strokeWidth={2.5}
              dot={{ r: 5 }} activeDot={{ r: 7 }}
            />
          ) : (
            <Bar dataKey="value" name={name || 'Value'} fill={color || COLORS.primary} radius={[4, 4, 0, 0]} />
          )}

          {data.some(d => d.value2 !== undefined) && (
            type === 'combo' ? (
              <Bar dataKey="value2" name={name2 || 'Value 2'} fill={color2 || COLORS.secondaryLight} radius={[4, 4, 0, 0]} />
            ) : (
              <Line
                type="monotone" dataKey="value2" name={name2 || 'Value 2'}
                stroke={color2 || COLORS.secondary} strokeWidth={2.5}
                dot={{ r: 5 }}
              />
            )
          )}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
