/* KpiCard — summary metric card */
import { COLORS } from '../../models/constants';

interface KpiCardProps {
  title: string;
  value: string;
  subtitle?: string;
  icon?: string;
  color?: string;
  tooltip?: string;
}

export default function KpiCard({ title, value, subtitle, icon, color, tooltip }: KpiCardProps) {
  return (
    <div
      style={{
        background: COLORS.cardBg,
        borderRadius: 12,
        padding: '20px 24px',
        boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
        borderLeft: `4px solid ${color || COLORS.primary}`,
        flex: '1 1 200px',
        minWidth: 200,
      }}
      title={tooltip}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
        {icon && <span style={{ fontSize: 20 }}>{icon}</span>}
        <span style={{ fontSize: 13, color: COLORS.textLight, fontWeight: 500 }}>{title}</span>
      </div>
      <div style={{ fontSize: 28, fontWeight: 700, color: color || COLORS.text }}>{value}</div>
      {subtitle && (
        <div style={{ fontSize: 12, color: COLORS.textLight, marginTop: 4 }}>{subtitle}</div>
      )}
    </div>
  );
}
