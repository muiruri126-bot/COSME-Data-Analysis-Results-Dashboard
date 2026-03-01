/* ═══════════════════════════════════════════════════════════
   useFilters — manages county + quarter filter state.
   ═══════════════════════════════════════════════════════════ */

import { useState, useCallback } from 'react';
import type { County, Quarter } from '../models/types';

export interface Filters {
  county: County;
  quarter: Quarter;
}

export function useFilters(initialCounty: County = 'All', initialQuarter: Quarter = 'Q4') {
  const [county, setCounty] = useState<County>(initialCounty);
  const [quarter, setQuarter] = useState<Quarter>(initialQuarter);

  const resetFilters = useCallback(() => {
    setCounty('All');
    setQuarter('Q4');
  }, []);

  return {
    county,
    quarter,
    setCounty,
    setQuarter,
    resetFilters,
    filters: { county, quarter } as Filters,
  };
}
