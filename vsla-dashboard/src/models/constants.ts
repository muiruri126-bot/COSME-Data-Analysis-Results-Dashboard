/* ═══════════════════════════════════════════════════════════
   Constants — colours, labels, config
   ═══════════════════════════════════════════════════════════ */

/** COSME-inspired colour palette */
export const COLORS = {
  primary: '#1B5E20',       // dark green (COSME brand)
  primaryLight: '#4CAF50',  // green
  secondary: '#0D47A1',     // blue
  secondaryLight: '#42A5F5',
  accent: '#FF9800',        // orange
  danger: '#E53935',        // red
  neutral: '#78909C',       // blue-grey
  background: '#F5F7FA',
  cardBg: '#FFFFFF',
  text: '#263238',
  textLight: '#607D8B',
  border: '#E0E0E0',
  kilifi: '#1B5E20',        // green for Kilifi
  kwale: '#0D47A1',         // blue for Kwale
  all: '#FF9800',           // orange for All
} as const;

/** Recharts colour sequences for bar/pie charts */
export const CHART_COLORS = [
  '#1B5E20', '#0D47A1', '#FF9800', '#E53935',
  '#7B1FA2', '#00838F', '#F57F17', '#AD1457',
];

/** County colours for consistent legend */
export const COUNTY_COLORS: Record<string, string> = {
  Kilifi: COLORS.kilifi,
  Kwale: COLORS.kwale,
  All: COLORS.all,
};

/** Readable quarter labels */
export const QUARTER_LABELS: Record<string, string> = {
  Q2: 'Q2 2025',
  Q3: 'Q3 2025',
  Q4: 'Q4 2025',
};

/** Format KES values */
export function formatKES(value: number): string {
  if (Math.abs(value) >= 1_000_000) return `KES ${(value / 1_000_000).toFixed(1)}M`;
  if (Math.abs(value) >= 1_000) return `KES ${(value / 1_000).toFixed(0)}K`;
  return `KES ${value.toLocaleString()}`;
}

/** Format percentage (0–1 → "94%") */
export function formatPct(value: number): string {
  return `${(value * 100).toFixed(0)}%`;
}

/** Format number with commas */
export function formatNum(value: number): string {
  return value.toLocaleString();
}
