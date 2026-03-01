/* ═══════════════════════════════════════════════════════════
   useIndicators — loads the VSLA dataset and exposes it.
   ═══════════════════════════════════════════════════════════ */

import { useState, useEffect } from 'react';
import type { VslaDataset } from '../models/types';
import { loadVslaData } from '../services/dataService';

export function useIndicators() {
  const [data, setData] = useState<VslaDataset | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadVslaData()
      .then(d => { setData(d); setLoading(false); })
      .catch(e => { setError(e.message); setLoading(false); });
  }, []);

  return { data, loading, error };
}
