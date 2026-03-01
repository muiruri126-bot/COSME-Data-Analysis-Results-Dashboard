/* ═══════════════════════════════════════════════════════════
   Membership & Retention — placeholder (Phase 2)
   ═══════════════════════════════════════════════════════════ */
import type { VslaDataset, County, Quarter } from '../models/types';
import { COLORS } from '../models/constants';

interface Props {
  data: VslaDataset;
  county: County;
  quarter: Quarter;
  onCountyChange: (c: County) => void;
  onQuarterChange: (q: Quarter) => void;
}

export default function MembershipRetention(_props: Props) {
  return (
    <div style={{ textAlign: 'center', padding: '80px 24px' }}>
      <div style={{ fontSize: 48, marginBottom: 16 }}>👥</div>
      <h1 style={{ fontSize: 22, fontWeight: 700, color: COLORS.text, marginBottom: 8 }}>
        Membership & Retention
      </h1>
      <p style={{ color: COLORS.textLight, maxWidth: 480, margin: '0 auto' }}>
        This view will include detailed membership demographics, gender breakdowns,
        meetings attendance, and member retention analysis. Coming soon in Phase 2.
      </p>
    </div>
  );
}
