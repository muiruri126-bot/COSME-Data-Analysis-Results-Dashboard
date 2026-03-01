/* ═══════════════════════════════════════════════════════════
   Loans & Repayment — placeholder (Phase 2)
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

export default function LoansRepayment(_props: Props) {
  return (
    <div style={{ textAlign: 'center', padding: '80px 24px' }}>
      <div style={{ fontSize: 48, marginBottom: 16 }}>🏦</div>
      <h1 style={{ fontSize: 22, fontWeight: 700, color: COLORS.text, marginBottom: 8 }}>
        Loans & Repayment
      </h1>
      <p style={{ color: COLORS.textLight, maxWidth: 480, margin: '0 auto' }}>
        This view will include loan disbursement trends, repayment rates, ROI analysis,
        loan purpose breakdown, and outstanding loan tracking. Coming soon in Phase 2.
      </p>
    </div>
  );
}
