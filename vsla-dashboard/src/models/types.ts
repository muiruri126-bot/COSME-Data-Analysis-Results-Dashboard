/* ═══════════════════════════════════════════════════════════
   VSLA Functionality Dashboard — TypeScript Interfaces
   Matches the structure of vsla-indicators.json
   ═══════════════════════════════════════════════════════════ */

// ─── Enums / Unions ──────────────────────────────────────────
export type County = 'Kilifi' | 'Kwale' | 'All';
export type Quarter = 'Q2' | 'Q3' | 'Q4';
export const QUARTERS: Quarter[] = ['Q2', 'Q3', 'Q4'];
export const COUNTIES: County[] = ['Kilifi', 'Kwale', 'All'];

// ─── Primitives ──────────────────────────────────────────────
export interface SumAvg {
  sum: number;
  average: number;
}

export interface BandDistribution {
  band: string;
  Q2: number;
  Q3: number;
  Q4: number;
}

export interface CountyQuarterRow {
  county: County;
  Q2: number;
  Q3: number;
  Q4: number;
}

export interface CountySumAvgRow {
  county: County;
  Q2: SumAvg;
  Q3: SumAvg;
  Q4: SumAvg;
}

// ─── A. MEMBERSHIP & MEETINGS ────────────────────────────────
export interface Membership {
  female: CountySumAvgRow[];
  male: CountySumAvgRow[];
  all: CountySumAvgRow[];
}

export interface MeetingsAttendance {
  frequency: CountyQuarterRow[];
  attendance: CountyQuarterRow[];
}

// ─── B. SAVINGS ──────────────────────────────────────────────
export interface SavingsData {
  membersSaving: CountySumAvgRow[];
  proportionBands: BandDistribution[];
  value: CountySumAvgRow[];
  valueBands: BandDistribution[];
}

// ─── C. SOCIAL FUND ──────────────────────────────────────────
export interface SocialFundData {
  percentageWithFund: CountyQuarterRow[];
  value: CountySumAvgRow[];
  valueBands: BandDistribution[];
}

// ─── D. LOANS ────────────────────────────────────────────────
export interface LoanGroup {
  count: CountySumAvgRow[];
  countBands: BandDistribution[];
  value: CountySumAvgRow[];
  valueBands: BandDistribution[];
}

export interface InterestData {
  value: CountySumAvgRow[];
  valueBands: BandDistribution[];
}

export interface LoanBehaviour {
  county: County;
  avgProportionRepaid: Record<Quarter, number>;
  avgValueRepaid: Record<Quarter, number>;
  avgROI: Record<Quarter, number>;
}

export interface LoansSection {
  disbursed: LoanGroup;
  repaid: LoanGroup;
  interest: InterestData;
  behaviour: LoanBehaviour[];
  failingToPay: CountyQuarterRow[];
  useDistribution: BandDistribution[];
}

// ─── Top-Level Dataset ───────────────────────────────────────
export interface VslaDataset {
  meta: { title: string; date: string; outcome: string };
  vslasAssessed: CountyQuarterRow[];
  membership: Membership;
  membersLeft: CountyQuarterRow[];
  percentLeftBands: BandDistribution[];
  meetings: MeetingsAttendance;
  savings: SavingsData;
  socialFund: SocialFundData;
  loans: LoansSection;
}
