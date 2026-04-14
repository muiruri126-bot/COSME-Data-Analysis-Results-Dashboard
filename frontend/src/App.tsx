import { Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './components/AppLayout';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import DashboardPage from './pages/DashboardPage';
import ProcurementPlansPage from './pages/ProcurementPlansPage';
import PlanDetailPage from './pages/PlanDetailPage';
import CreatePlanPage from './pages/CreatePlanPage';
import ApprovalInboxPage from './pages/ApprovalInboxPage';
import PurchaseRequisitionsPage from './pages/PurchaseRequisitionsPage';
import DeliveriesPage from './pages/DeliveriesPage';
import StockAssetsPage from './pages/StockAssetsPage';
import ExchangeRatesPage from './pages/ExchangeRatesPage';
import ReportsPage from './pages/ReportsPage';
import AdminUsersPage from './pages/AdminUsersPage';
import AuditLogPage from './pages/AuditLogPage';
import NotificationsPage from './pages/NotificationsPage';
import { useAuthStore } from './store';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = useAuthStore((s) => s.token);
  return token ? <>{children}</> : <Navigate to="/login" replace />;
}

/** Route guard that checks role access. Redirects to Dashboard if unauthorized. */
function RoleRoute({ roles, children }: { roles: string[]; children: React.ReactNode }) {
  const hasRole = useAuthStore((s) => s.hasRole);
  if (!hasRole(...roles)) {
    return <Navigate to="/" replace />;
  }
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Routes>
                {/* All users */}
                <Route path="/" element={<DashboardPage />} />
                <Route path="/plans" element={<ProcurementPlansPage />} />
                <Route path="/plans/new" element={<RoleRoute roles={['Requester', 'Admin']}><CreatePlanPage /></RoleRoute>} />
                <Route path="/plans/:id" element={<PlanDetailPage />} />
                <Route path="/notifications" element={<NotificationsPage />} />
                <Route path="/reports" element={<ReportsPage />} />

                {/* Managers, Finance, Admin */}
                <Route path="/approvals" element={<RoleRoute roles={['Manager', 'Finance', 'Admin']}><ApprovalInboxPage /></RoleRoute>} />

                {/* Supply Chain, Admin */}
                <Route path="/purchase-requisitions" element={<RoleRoute roles={['Supply Chain', 'Admin']}><PurchaseRequisitionsPage /></RoleRoute>} />

                {/* Supply Chain, Stores, Admin */}
                <Route path="/deliveries" element={<RoleRoute roles={['Supply Chain', 'Stores', 'Admin']}><DeliveriesPage /></RoleRoute>} />

                {/* Stores, Admin */}
                <Route path="/stock-assets" element={<RoleRoute roles={['Stores', 'Admin']}><StockAssetsPage /></RoleRoute>} />

                {/* Finance, Admin */}
                <Route path="/exchange-rates" element={<RoleRoute roles={['Finance', 'Admin']}><ExchangeRatesPage /></RoleRoute>} />

                {/* Admin only */}
                <Route path="/admin/users" element={<RoleRoute roles={['Admin']}><AdminUsersPage /></RoleRoute>} />
                <Route path="/admin/audit-log" element={<RoleRoute roles={['Admin']}><AuditLogPage /></RoleRoute>} />
              </Routes>
            </AppLayout>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}
