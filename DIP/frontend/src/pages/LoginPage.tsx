import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import api from '../lib/api';
import { useAuthStore } from '../store/auth';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { setTokens, setUser } = useAuthStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const { data } = await api.post('/auth/login', { email, password });
      setTokens(data.access_token, data.refresh_token);
      setUser(data.user);
      toast.success(`Welcome, ${data.user.full_name}`);
      navigate('/');
    } catch (err: any) {
      toast.error(err.response?.data?.error || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col bg-gray-100">
      {/* Top header bar */}
      <header className="bg-gradient-to-r from-[#003366] via-[#004e9a] to-[#0074e4] shadow-md">
        <div className="max-w-7xl mx-auto px-6 py-3 flex items-center gap-3">
          <img src="/logo.svg" alt="Plan International" className="h-9" />
          <div className="text-white leading-tight">
            <span className="text-lg font-bold tracking-tight">COSME DIP</span>
            <span className="block text-[11px] font-medium uppercase tracking-wider text-blue-200">Tracker</span>
          </div>
        </div>
      </header>

      {/* Centered card */}
      <main className="flex flex-1 items-center justify-center p-6">
        <div className="w-full max-w-md rounded-xl border border-gray-200 bg-white p-8 shadow-lg space-y-6">
          <div className="text-center">
            <img src="/logo.svg" alt="Plan International" className="h-16 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-gray-900">COSME DIP Tracker</h1>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <label className="block">
              <span className="text-sm font-medium text-gray-700">Email</span>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 block w-full rounded-lg border-gray-300 bg-gray-50 px-4 py-2.5 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                placeholder="you@plan-international.org"
              />
            </label>

            <label className="block">
              <span className="text-sm font-medium text-gray-700">Password</span>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 block w-full rounded-lg border-gray-300 bg-gray-50 px-4 py-2.5 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              />
            </label>

            <button type="submit" disabled={loading} className="btn-primary w-full justify-center py-2.5 text-base">
              {loading ? 'Signing in…' : '➜ Login'}
            </button>

            <div className="text-center space-y-2 text-sm">
              <p className="text-gray-600">
                Don't have an account?{' '}
                <Link to="/register" className="font-medium text-primary-600 hover:text-primary-700">
                  Register here
                </Link>
              </p>
              <Link to="/forgot-password" className="font-medium text-primary-600 hover:text-primary-700">
                Forgot your password?
              </Link>
            </div>
          </form>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-gray-50 py-4 text-center">
        <img src="/logo.svg" alt="Plan International" className="h-8 mx-auto mb-1 opacity-60" />
        <p className="text-xs text-gray-400">&copy; 2026 Plan International Kenya &mdash; COSME DIP Tracker</p>
      </footer>
    </div>
  );
}
