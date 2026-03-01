/* FilterBar — county and quarter selectors */
import type { County, Quarter } from '../../models/types';
import { COUNTIES, QUARTERS } from '../../models/types';
import { COLORS, QUARTER_LABELS } from '../../models/constants';

interface FilterBarProps {
  county: County;
  quarter: Quarter;
  onCountyChange: (c: County) => void;
  onQuarterChange: (q: Quarter) => void;
}

const selectStyle: React.CSSProperties = {
  padding: '8px 16px',
  borderRadius: 8,
  border: `1px solid ${COLORS.neutral}`,
  fontSize: 14,
  fontWeight: 500,
  color: COLORS.text,
  background: COLORS.cardBg,
  cursor: 'pointer',
  outline: 'none',
};

export default function FilterBar({ county, quarter, onCountyChange, onQuarterChange }: FilterBarProps) {
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 16,
      padding: '12px 0', flexWrap: 'wrap',
    }}>
      <label style={{ fontSize: 13, fontWeight: 600, color: COLORS.textLight }}>
        County:
        <select
          value={county}
          onChange={e => onCountyChange(e.target.value as County)}
          style={{ ...selectStyle, marginLeft: 8 }}
        >
          {COUNTIES.map(c => (
            <option key={c} value={c}>{c === 'All' ? 'All Counties' : c}</option>
          ))}
        </select>
      </label>

      <label style={{ fontSize: 13, fontWeight: 600, color: COLORS.textLight }}>
        Quarter:
        <select
          value={quarter}
          onChange={e => onQuarterChange(e.target.value as Quarter)}
          style={{ ...selectStyle, marginLeft: 8 }}
        >
          {QUARTERS.map(q => (
            <option key={q} value={q}>{QUARTER_LABELS[q]}</option>
          ))}
        </select>
      </label>
    </div>
  );
}
