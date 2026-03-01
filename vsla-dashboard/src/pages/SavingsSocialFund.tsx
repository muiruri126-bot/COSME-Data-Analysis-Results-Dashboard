/* ═══════════════════════════════════════════════════════════
   Savings & Social Fund View — detailed savings + social fund analysis
   ═══════════════════════════════════════════════════════════ */
import type { VslaDataset, County, Quarter } from '../models/types';
import { COLORS, formatKES, formatPct, formatNum, QUARTER_LABELS } from '../models/constants';
import {
  getSumAvg, getSumAvgTrend, getBandForQuarter,
  getCountyQuarterValue, getTrend,
} from '../services/dataService';

import KpiCard from '../components/Cards/KpiCard';
import FilterBar from '../components/Layout/FilterBar';
import TrendLineChart from '../components/Charts/TrendLineChart';
import DonutChart from '../components/Charts/DonutChart';
import GroupedBarChart from '../components/Charts/GroupedBarChart';
import DataTable from '../components/Tables/DataTable';

interface Props {
  data: VslaDataset;
  county: County;
  quarter: Quarter;
  onCountyChange: (c: County) => void;
  onQuarterChange: (q: Quarter) => void;
}

export default function SavingsSocialFund({ data, county, quarter, onCountyChange, onQuarterChange }: Props) {
  const s = data.savings;
  const sf = data.socialFund;

  /* ─── KPI values ─── */
  const membersSaving = getSumAvg(s.membersSaving, county, quarter, 'sum');
  const avgSaving = getSumAvg(s.membersSaving, county, quarter, 'average');
  const totalSavings = getSumAvg(s.value, county, quarter, 'sum');
  const avgSavings = getSumAvg(s.value, county, quarter, 'average');
  const pctWithFund = getCountyQuarterValue(sf.percentageWithFund, county, quarter);
  const totalFund = getSumAvg(sf.value, county, quarter, 'sum');
  const avgFund = getSumAvg(sf.value, county, quarter, 'average');

  /* ─── Trends ─── */
  const savingsTrend = getSumAvgTrend(s.value, county, 'sum');
  const savingsAvgTrend = getSumAvgTrend(s.value, county, 'average');
  const membersSavingTrend = getSumAvgTrend(s.membersSaving, county, 'sum');
  const socialFundTrend = getSumAvgTrend(sf.value, county, 'sum');
  const pctFundTrend = getTrend(sf.percentageWithFund, county);

  /* ─── Bands ─── */
  const savingsPropBands = getBandForQuarter(s.proportionBands, quarter);
  const savingsValueBands = getBandForQuarter(s.valueBands, quarter);
  const socialFundBands = getBandForQuarter(sf.valueBands, quarter);

  /* ─── Table data: Savings by county and quarter ─── */
  const savingsTableRows = ['Kilifi', 'Kwale', 'All'].map(c => {
    const row = s.value.find(r => r.county === c);
    if (!row) return { county: c, Q2_sum: 0, Q2_avg: 0, Q3_sum: 0, Q3_avg: 0, Q4_sum: 0, Q4_avg: 0 };
    return {
      county: c,
      Q2_sum: formatKES(row.Q2.sum), Q2_avg: formatKES(row.Q2.average),
      Q3_sum: formatKES(row.Q3.sum), Q3_avg: formatKES(row.Q3.average),
      Q4_sum: formatKES(row.Q4.sum), Q4_avg: formatKES(row.Q4.average),
    };
  });

  const fundTableRows = ['Kilifi', 'Kwale', 'All'].map(c => {
    const pctRow = sf.percentageWithFund.find(r => r.county === c);
    const valRow = sf.value.find(r => r.county === c);
    return {
      county: c,
      Q2_pct: pctRow ? formatPct(pctRow.Q2) : '-',
      Q3_pct: pctRow ? formatPct(pctRow.Q3) : '-',
      Q4_pct: pctRow ? formatPct(pctRow.Q4) : '-',
      Q2_val: valRow ? formatKES(valRow.Q2.sum) : '-',
      Q3_val: valRow ? formatKES(valRow.Q3.sum) : '-',
      Q4_val: valRow ? formatKES(valRow.Q4.sum) : '-',
    };
  });

  return (
    <div>
      <h1 style={{ fontSize: 22, fontWeight: 700, color: COLORS.text, margin: '0 0 4px' }}>
        Savings & Social Fund Analysis
      </h1>
      <p style={{ fontSize: 13, color: COLORS.textLight, margin: '0 0 8px' }}>
        Deep dive into VSLA savings patterns and social fund indicators.
      </p>

      <FilterBar county={county} quarter={quarter}
        onCountyChange={onCountyChange} onQuarterChange={onQuarterChange} />

      {/* ─── Section A: SAVINGS KPIs ─── */}
      <h2 style={{ fontSize: 17, fontWeight: 600, color: COLORS.text, margin: '20px 0 12px' }}>
        💰 Savings ({QUARTER_LABELS[quarter]})
      </h2>
      <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginBottom: 20 }}>
        <KpiCard
          title="Members Saving" value={formatNum(membersSaving)}
          subtitle={`Avg per VSLA: ${avgSaving.toFixed(1)}`}
          icon="👤" color={COLORS.primary}
          tooltip="Number of VSLA members effectively saving"
        />
        <KpiCard
          title="Total Savings" value={formatKES(totalSavings)}
          subtitle={`Avg per VSLA: ${formatKES(avgSavings)}`}
          icon="💰" color={COLORS.secondary}
          tooltip="Total value of savings across all assessed VSLAs"
        />
        <KpiCard
          title="High Savers (81-100%)" value={formatPct(savingsPropBands.find(b => b.band === '81-100%')?.value ?? 0)}
          icon="⭐" color={COLORS.primaryLight}
          tooltip="% of VSLAs where 81-100% of members are actively saving"
        />
      </div>

      {/* ─── Savings Trend Charts ─── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))', gap: 20, marginBottom: 24 }}>
        <TrendLineChart
          data={savingsTrend}
          title="Total Savings Value (KES) — Q2→Q4"
          name="Total Savings" color={COLORS.primary}
          formatter={formatKES}
        />
        <TrendLineChart
          data={savingsAvgTrend}
          title="Average Savings per VSLA (KES) — Q2→Q4"
          name="Avg Savings" color={COLORS.secondary}
          formatter={formatKES}
        />
        <TrendLineChart
          data={membersSavingTrend}
          title="Members Effectively Saving — Q2→Q4"
          name="Members" color={COLORS.primaryLight}
          formatter={formatNum}
        />
      </div>

      {/* ─── Savings Distribution Charts ─── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))', gap: 20, marginBottom: 24 }}>
        <DonutChart
          title={`Proportion of Members Saving — ${QUARTER_LABELS[quarter]}`}
          data={savingsPropBands.map(b => ({ name: b.band, value: b.value }))}
        />
        <GroupedBarChart
          title={`VSLAs by Savings Amount Band — ${QUARTER_LABELS[quarter]}`}
          data={savingsValueBands.map(b => ({ name: b.band, pct: +(b.value * 100).toFixed(1) }))}
          bars={[{ dataKey: 'pct', name: '% of VSLAs', color: COLORS.primary }]}
          formatter={v => `${v}%`}
        />
      </div>

      {/* ─── Savings Table ─── */}
      <DataTable
        title="Savings Value by County & Quarter"
        columns={[
          { key: 'county', label: 'County' },
          { key: 'Q2_sum', label: 'Q2 Total', align: 'right' },
          { key: 'Q2_avg', label: 'Q2 Avg', align: 'right' },
          { key: 'Q3_sum', label: 'Q3 Total', align: 'right' },
          { key: 'Q3_avg', label: 'Q3 Avg', align: 'right' },
          { key: 'Q4_sum', label: 'Q4 Total', align: 'right' },
          { key: 'Q4_avg', label: 'Q4 Avg', align: 'right' },
        ]}
        rows={savingsTableRows}
      />

      {/* ═══ Section B: SOCIAL FUND ═══ */}
      <h2 style={{ fontSize: 17, fontWeight: 600, color: COLORS.text, margin: '32px 0 12px' }}>
        🤝 Social Fund ({QUARTER_LABELS[quarter]})
      </h2>
      <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginBottom: 20 }}>
        <KpiCard
          title="VSLAs with Social Fund" value={formatPct(pctWithFund)}
          icon="🛡️" color={COLORS.accent}
          tooltip="Percentage of VSLAs that maintain a social/welfare fund"
        />
        <KpiCard
          title="Total Social Fund" value={formatKES(totalFund)}
          subtitle={`Avg per VSLA: ${formatKES(avgFund)}`}
          icon="💵" color={COLORS.primary}
          tooltip="Total value of social/welfare funds across all assessed VSLAs"
        />
      </div>

      {/* ─── Social Fund Trends ─── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))', gap: 20, marginBottom: 24 }}>
        <TrendLineChart
          data={pctFundTrend}
          title="% VSLAs with Social Fund — Q2→Q4"
          name="% with Fund" color={COLORS.accent}
          formatter={v => formatPct(v)}
        />
        <TrendLineChart
          data={socialFundTrend}
          title="Total Social Fund Value (KES) — Q2→Q4"
          name="Total Fund" color={COLORS.primary}
          formatter={formatKES}
        />
      </div>

      {/* ─── Social Fund Distribution ─── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))', gap: 20, marginBottom: 24 }}>
        <GroupedBarChart
          title={`VSLAs by Social Fund Amount Band — ${QUARTER_LABELS[quarter]}`}
          data={socialFundBands.map(b => ({ name: b.band, pct: +(b.value * 100).toFixed(1) }))}
          bars={[{ dataKey: 'pct', name: '% of VSLAs', color: COLORS.accent }]}
          formatter={v => `${v}%`}
        />
      </div>

      {/* ─── Social Fund Table ─── */}
      <DataTable
        title="Social Fund by County & Quarter"
        columns={[
          { key: 'county', label: 'County' },
          { key: 'Q2_pct', label: 'Q2 % Coverage', align: 'right' },
          { key: 'Q2_val', label: 'Q2 Total Value', align: 'right' },
          { key: 'Q3_pct', label: 'Q3 % Coverage', align: 'right' },
          { key: 'Q3_val', label: 'Q3 Total Value', align: 'right' },
          { key: 'Q4_pct', label: 'Q4 % Coverage', align: 'right' },
          { key: 'Q4_val', label: 'Q4 Total Value', align: 'right' },
        ]}
        rows={fundTableRows}
      />
    </div>
  );
}
