/* ═══════════════════════════════════════════════════════════
   App — root component with routing & shared state
   ═══════════════════════════════════════════════════════════ */
import { Routes, Route } from 'react-router-dom';
import Header from './components/Layout/Header';
import { useIndicators } from './hooks/useIndicators';
import { useFilters } from './hooks/useFilters';
import { COLORS } from './models/constants';

import OverviewDashboard from './pages/OverviewDashboard';
import MembershipRetention from './pages/MembershipRetention';
import SavingsSocialFund from './pages/SavingsSocialFund';
import LoansRepayment from './pages/LoansRepayment';
import CountyComparison from './pages/CountyComparison';

export default function App() {
  const { data, loading, error } = useIndicators();
  const { county, quarter, setCounty, setQuarter } = useFilters();

  if (loading) {
    return (
      <div style={{
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        justifyContent: 'center', height: '100vh', gap: 16,
      }}>
        <div style={{
          width: 48, height: 48, border: `4px solid ${COLORS.border}`,
          borderTopColor: COLORS.primary, borderRadius: '50%',
          animation: 'spin 0.8s linear infinite',
        }} />
        <p style={{ color: COLORS.textLight, fontSize: 14 }}>Loading VSLA data…</p>
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div style={{
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        justifyContent: 'center', height: '100vh', gap: 12,
        color: COLORS.text, padding: 24, textAlign: 'center',
      }}>
        <div style={{ fontSize: 48 }}>⚠️</div>
        <h2 style={{ fontWeight: 600 }}>Failed to load data</h2>
        <p style={{ color: COLORS.textLight, maxWidth: 400 }}>{error ?? 'Unknown error'}</p>
        <button
          onClick={() => window.location.reload()}
          style={{
            marginTop: 8, padding: '8px 20px', background: COLORS.primary,
            color: '#fff', borderRadius: 6, fontWeight: 500,
          }}
        >
          Retry
        </button>
      </div>
    );
  }

  const pageProps = {
    data, county, quarter,
    onCountyChange: setCounty,
    onQuarterChange: setQuarter,
  };

  return (
    <>
      <Header />
      <main className="page-container">
        <Routes>
          <Route path="/" element={<OverviewDashboard {...pageProps} />} />
          <Route path="/membership" element={<MembershipRetention {...pageProps} />} />
          <Route path="/savings" element={<SavingsSocialFund {...pageProps} />} />
          <Route path="/loans" element={<LoansRepayment {...pageProps} />} />
          <Route path="/compare" element={<CountyComparison {...pageProps} />} />
        </Routes>
      </main>
    </>
  );
}
