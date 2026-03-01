/* ═══════════════════════════════════════════════════════════
   Data Service — loads and filters VSLA indicator data.

   CURRENT: Reads from a static JSON file (public/data/vsla-indicators.json).
   FUTURE:  Swap the fetch() call below for a REST API, database query,
            or SharePoint list call. The interface stays the same.
   ═══════════════════════════════════════════════════════════ */

import type {
  VslaDataset,
  County,
  Quarter,
  CountyQuarterRow,
  CountySumAvgRow,
  BandDistribution,
} from '../models/types';

let _cache: VslaDataset | null = null;

/**
 * Load the full VSLA dataset.
 *
 * TODO: To switch to an API, replace the fetch URL below:
 *   const res = await fetch('https://your-api.example.com/api/vsla-indicators');
 *
 * TODO: To switch to a SharePoint list:
 *   import { sp } from '@pnp/sp';
 *   const items = await sp.web.lists.getByTitle('VSLAIndicators').items.getAll();
 *   return transformSharePointItems(items);
 */
export async function loadVslaData(): Promise<VslaDataset> {
  if (_cache) return _cache;

  const res = await fetch('./data/vsla-indicators.json');
  if (!res.ok) throw new Error(`Failed to load VSLA data: ${res.statusText}`);
  _cache = (await res.json()) as VslaDataset;
  return _cache;
}

// ─── Filter helpers ──────────────────────────────────────────

/** Filter a CountyQuarterRow[] to a single county */
export function filterCountyRows(rows: CountyQuarterRow[], county: County): CountyQuarterRow[] {
  if (county === 'All') return rows;
  return rows.filter(r => r.county === county || r.county === 'All');
}

/** Get a single value for a county + quarter from CountyQuarterRow[] */
export function getCountyQuarterValue(
  rows: CountyQuarterRow[],
  county: County,
  quarter: Quarter
): number {
  const target = county === 'All' ? 'All' : county;
  const row = rows.find(r => r.county === target);
  return row ? row[quarter] : 0;
}

/** Get Sum or Average for a county + quarter from CountySumAvgRow[] */
export function getSumAvg(
  rows: CountySumAvgRow[],
  county: County,
  quarter: Quarter,
  field: 'sum' | 'average' = 'sum'
): number {
  const target = county === 'All' ? 'All' : county;
  const row = rows.find(r => r.county === target);
  return row ? row[quarter][field] : 0;
}

/** Get a band value for the selected quarter */
export function getBandForQuarter(
  bands: BandDistribution[],
  quarter: Quarter
): { band: string; value: number }[] {
  return bands.map(b => ({ band: b.band, value: b[quarter] }));
}

/** Get trend data: returns { quarter, value }[] for a county across Q2-Q4 */
export function getTrend(
  rows: CountyQuarterRow[],
  county: County
): { quarter: string; value: number }[] {
  const target = county === 'All' ? 'All' : county;
  const row = rows.find(r => r.county === target);
  if (!row) return [];
  return [
    { quarter: 'Q2', value: row.Q2 },
    { quarter: 'Q3', value: row.Q3 },
    { quarter: 'Q4', value: row.Q4 },
  ];
}

/** Get trend data from SumAvg rows */
export function getSumAvgTrend(
  rows: CountySumAvgRow[],
  county: County,
  field: 'sum' | 'average' = 'sum'
): { quarter: string; value: number }[] {
  const target = county === 'All' ? 'All' : county;
  const row = rows.find(r => r.county === target);
  if (!row) return [];
  return [
    { quarter: 'Q2', value: row.Q2[field] },
    { quarter: 'Q3', value: row.Q3[field] },
    { quarter: 'Q4', value: row.Q4[field] },
  ];
}

/** Get comparative data (Kilifi vs Kwale) for a given quarter */
export function getComparativeData(
  rows: CountyQuarterRow[],
  quarter: Quarter
): { county: string; value: number }[] {
  return rows
    .filter(r => r.county !== 'All')
    .map(r => ({ county: r.county, value: r[quarter] }));
}
