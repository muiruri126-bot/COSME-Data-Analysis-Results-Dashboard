import { useState, useEffect } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import {
  Bars3Icon,
  XMarkIcon,
  HomeIcon,
  TableCellsIcon,
  ChartBarIcon,
  DocumentChartBarIcon,
  UserGroupIcon,
  BellIcon,
  ArrowLeftStartOnRectangleIcon,
} from '@heroicons/react/24/outline';
import { useAuthStore } from '../store/auth';
import api from '../lib/api';

const navItems = [
  { to: '/framework', label: 'Implementation Plan', icon: TableCellsIcon },
  { to: '/gantt', label: 'Gantt Chart', icon: ChartBarIcon },
  { to: '/dashboard', label: 'Dashboard', icon: HomeIcon },
  { to: '/reports', label: 'Reports', icon: DocumentChartBarIcon },
  { to: '/admin/users', label: 'Admin', icon: UserGroupIcon, roles: ['Admin'] },
];

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [unread, setUnread] = useState(0);
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const navigate = useNavigate();

  useEffect(() => {
    api.get('/notifications').then((r) => setUnread(r.data.unread_count)).catch(() => {});
    const interval = setInterval(() => {
      api.get('/notifications').then((r) => setUnread(r.data.unread_count)).catch(() => {});
    }, 60_000);
    return () => clearInterval(interval);
  }, []);

  const handleLogout = () => {
    api.post('/auth/logout').catch(() => {});
    logout();
    navigate('/login');
  };

  const userRoles = user?.roles ?? [];

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-gradient-to-b from-[#003366] via-[#004e9a] to-[#0074e4] text-white shadow-xl transform transition-transform lg:relative lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex h-16 items-center justify-between px-4 border-b border-white/20">
          <div className="flex items-center gap-2">
            <img src="/logo.svg" alt="Plan International" className="h-8 w-8" />
            <span className="text-lg font-bold text-white tracking-tight">COSME DIP</span>
          </div>
          <button className="lg:hidden text-white/60 hover:text-white" onClick={() => setSidebarOpen(false)}>
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>
        <nav className="mt-4 space-y-1 px-3">
          {navItems
            .filter((item) => !item.roles || item.roles.some((r) => userRoles.includes(r)))
            .map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={() => setSidebarOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-white/20 text-white'
                      : 'text-blue-100 hover:bg-white/10 hover:text-white'
                  }`
                }
              >
                <item.icon className="h-5 w-5" />
                {item.label}
              </NavLink>
            ))}
        </nav>
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-white/20">
          <p className="text-xs text-blue-200/70 text-center">COSME Detailed Implementation Plan</p>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top bar */}
        <header className="flex h-16 items-center justify-between border-b border-gray-200 bg-white px-6 shadow-sm">
          <button className="lg:hidden" onClick={() => setSidebarOpen(true)}>
            <Bars3Icon className="h-6 w-6 text-gray-600" />
          </button>

          <div className="flex items-center gap-5 ml-auto">
            <button className="relative p-1.5 rounded-lg hover:bg-gray-100 transition" title="Notifications">
              <BellIcon className="h-5 w-5 text-gray-500" />
              {unread > 0 && (
                <span className="absolute -top-0.5 -right-0.5 h-4 min-w-4 rounded-full bg-red-500 text-[10px] text-white flex items-center justify-center px-1 font-medium">
                  {unread > 9 ? '9+' : unread}
                </span>
              )}
            </button>

            <div className="h-8 w-px bg-gray-200" />

            <div className="flex items-center gap-3">
              <div className="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 font-semibold text-sm">
                {user?.full_name?.charAt(0) ?? 'U'}
              </div>
              <div className="text-sm hidden sm:block">
                <p className="font-semibold text-gray-800">{user?.full_name}</p>
                <p className="text-xs text-gray-500">{userRoles.join(', ')}</p>
              </div>
            </div>

            <button onClick={handleLogout} className="p-1.5 rounded-lg text-gray-400 hover:text-red-600 hover:bg-red-50 transition" title="Logout">
              <ArrowLeftStartOnRectangleIcon className="h-5 w-5" />
            </button>
          </div>
        </header>

        <main className="flex-1 overflow-auto p-5 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
