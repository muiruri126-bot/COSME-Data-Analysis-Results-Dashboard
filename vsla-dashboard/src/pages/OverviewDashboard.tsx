/* ═══════════════════════════════════════════════════════════
   Overview Dashboard — KPIs, trend charts, distribution charts
   ═══════════════════════════════════════════════════════════ */
import type { VslaDataset, County, Quarter } from '../models/types';
import { COLORS, formatKES, formatPct, formatNum } from '../models/constants';
import {
  getCountyQuarterValue, getSumAvg, getSumAvgTrend,
  getTrend, getBandForQuarter,
} from '../services/dataService';

import KpiCard from '../components/Cards/KpiCard';
import FilterBar from '../components/Layout/FilterBar';
import TrendLineChart from '../components/Charts/TrendLineChart';
import DonutChart from '../components/Charts/DonutChart';
import GroupedBarChart from '../components/Charts/GroupedBarChart';

interface Props {
  data: VslaDataset;
  county: County;
  quarter: Quarter;
  onCountyChange: (c: County) => void;
  onQuarterChange: (q: Quarter) => void;
}

export default function OverviewDashboard({ data, county, quarter, onCountyChange, onQuarterChange }: Props) {
  /* ─── Compute KPI values ─── */
  const vslasAssessed = getCountyQuarterValue(data.vslasAssessed, county, quarter);
  const totalMembers = getSumAvg(data.membership.all, county, quarter, 'sum');
  const femaleMembers = getSumAvg(data.membership.female, county, quarter, 'sum');
  const pctWomen = totalMembers > 0 ? femaleMembers / totalMembers : 0;
  const meetingFreq = getCountyQuarterValue(data.meetings.frequency, county, quarter);
  const attendance = getCountyQuarterValue(data.meetings.attendance, county, quarter);
  const totalSavings = getSumAvg(data.savings.value, county, quarter, 'sum');
  const loansDisbursed = getSumAvg(data.loans.disbursed.value, county, quarter, 'sum');
  const loansRepaid = getSumAvg(data.loans.repaid.value, county, quarter, 'sum');
  const behaviourRow = data.loans.behaviour.find(b =>
    b.county === (county === 'All' ? 'All' : county)
  );
  const avgROI = behaviourRow ? behaviourRow.avgROI[quarter] : 0;

  /* ─── Trend data ─── */
  const membersTrend = getSumAvgTrend(data.membership.all, county, 'sum');
  const savingsTrend = getSumAvgTrend(data.savings.value, county, 'sum');

  // Loans: disbursed vs repaid combined
  const disbursedTrend = getSumAvgTrend(data.loans.disbursed.value, county, 'sum');
  const repaidTrend = getSumAvgTrend(data.loans.repaid.value, county, 'sum');
  const loanComboData = disbursedTrend.map((d, i) => ({
    quarter: d.quarter,
    value: d.value,
    value2: repaidTrend[i]?.value ?? 0,
  }));

  // Social fund % trend
  const socialFundTrend = getTrend(data.socialFund.percentageWithFund, county);

  /* ─── Band distributions (for selected quarter) ─── */
  const loanUseBands = getBandForQuarter(data.loans.useDistribution, quarter);
  const savingsBands = getBandForQuarter(data.savings.valueBands, quarter);
  const socialFundBands = getBandForQuarter(data.socialFund.valueBands, quarter);

  return (
    <div>
      {/* Page title + outcome */}
      <div style={{ marginBottom: 8 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, color: COLORS.text, margin: '0 0 4px' }}>
          VSLA Functionality Overview
        </h1>
        <p style={{ fontSize: 13, color: COLORS.textLight, margin: 0 }}>
          {data.meta.outcome}
        </p>
      </div>

      <FilterBar county={county} quarter={quarter}
        onCountyChange={onCountyChange} onQuarterChange={onQuarterChange} />

      {/* ─── KPI Cards ─── */}
      <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', margin: '16px 0' }}>
        <KpiCard
          title="VSLAs Assessed" value={formatNum(vslasAssessed)}
          icon="🏘️" color={COLORS.primary}
          tooltip="Number of VSLAs assessed this quarter"
        />
        <KpiCard
          title="Total Members" value={formatNum(totalMembers)}
          subtitle={`${formatPct(pctWomen)} women`}
          icon="👥" color={COLORS.secondary}
          tooltip="Total people registered in VSLAs (sum across assessed VSLAs)"
        />
        <KpiCard
          title="Meeting Frequency" value={formatPct(meetingFreq)}
          subtitle={`Attendance: ${formatPct(attendance)}`}
          icon="📅" color={COLORS.accent}
          tooltip="% of VSLAs that always meet on schedule / % with high attendance"
        />
        <KpiCard
          title="Total Savings" value={formatKES(totalSavings)}
          icon="💰" color={COLORS.primary}
          tooltip="Total value of VSLA savings (KES) for the selected quarter"
        />
        <KpiCard
          title="Loans Disbursed" value={formatKES(loansDisbursed)}
          subtitle={`Repaid: ${formatKES(loansRepaid)}`}
          icon="📈" color={COLORS.secondary}
          tooltip="Total value of loans disbursed vs repaid (KES)"
        />
        <KpiCard
          title="Average ROI" value={formatPct(avgROI)}
          icon="📊" color={avgROI >= 0.1 ? COLORS.primary : COLORS.danger}
          tooltip="Average interest earned divided by loan value (return on investment)"
        />
      </div>

      {/* ─── Trend Charts ─── */}
      <h2 style={{ fontSize: 17, fontWeight: 600, color: COLORS.text, margin: '24px 0 12px' }}>
        Quarterly Trends
      </h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))', gap: 20 }}>
        <TrendLineChart
          data={membersTrend}
          title="Total VSLA Members (Q2–Q4)"
          name="Members" color={COLORS.secondary}
          formatter={formatNum}
        />
        <TrendLineChart
          data={savingsTrend}
          title="Value of VSLA Savings (KES)"
          name="Savings (KES)" color={COLORS.primary}
          formatter={formatKES}
        />
        <TrendLineChart
          data={loanComboData}
          title="Loans: Disbursed vs Repaid (KES)"
          name="Disbursed" name2="Repaid"
          color={COLORS.secondary} color2={COLORS.primaryLight}
          type="combo"
          formatter={formatKES}
        />
        <TrendLineChart
          data={socialFundTrend}
          title="% of VSLAs with Social Fund"
          name="% with Fund" color={COLORS.accent}
          formatter={v => formatPct(v)}
        />
      </div>

      {/* ─── Distribution Charts ─── */}
      <h2 style={{ fontSize: 17, fontWeight: 600, color: COLORS.text, margin: '24px 0 12px' }}>
        Distribution Analysis ({quarter})
      </h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))', gap: 20 }}>
        <DonutChart
          title="Loan Use Categories"
          data={loanUseBands.map(b => ({ name: b.band, value: b.value }))}
        />
        <GroupedBarChart
          title="VSLAs by Savings Amount Band"
          data={savingsBands.map(b => ({ name: b.band, pct: +(b.value * 100).toFixed(1) }))}
          bars={[{ dataKey: 'pct', name: '% of VSLAs', color: COLORS.primary }]}
          formatter={v => `${v}%`}
        />
        <GroupedBarChart
          title="VSLAs by Social Fund Amount Band"
          data={socialFundBands.map(b => ({ name: b.band, pct: +(b.value * 100).toFixed(1) }))}
          bars={[{ dataKey: 'pct', name: '% of VSLAs', color: COLORS.accent }]}
          formatter={v => `${v}%`}
        />
        <GroupedBarChart
          title="VSLAs by Loan Value Disbursed Band"
          data={getBandForQuarter(data.loans.disbursed.valueBands, quarter).map(b => ({
            name: b.band, pct: +(b.value * 100).toFixed(1),
          }))}
          bars={[{ dataKey: 'pct', name: '% of VSLAs', color: COLORS.secondary }]}
          formatter={v => `${v}%`}
        />
      </div>
    </div>
  );
}
