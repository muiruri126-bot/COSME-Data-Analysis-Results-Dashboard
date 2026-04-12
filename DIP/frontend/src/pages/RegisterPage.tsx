import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import api from '../lib/api';
import { useAuthStore } from '../store/auth';

export default function RegisterPage() {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { setTokens, setUser } = useAuthStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }
    setLoading(true);
    try {
      const { data } = await api.post('/auth/register', {
        full_name: fullName,
        email,
        phone: phone || undefined,
        password,
      });
      setTokens(data.access_token, data.refresh_token);
      setUser(data.user);
      toast.success('Account created successfully!');
      navigate('/');
    } catch (err: any) {
      toast.error(err.response?.data?.error || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen">
      {/* Left branding panel */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-[#003366] via-[#004e9a] to-[#0074e4] flex-col items-center justify-center p-12 text-white">
        <div className="max-w-md text-center">
          <img src="/logo.svg" alt="Plan International" className="h-20 mx-auto mb-6 drop-shadow-lg" />
          <h2 className="text-3xl font-bold mb-4">COSME DIP Tracker</h2>
          <p className="text-blue-200 leading-relaxed">
            Plan International Kenya &bull; COSME Project
          </p>
        </div>
      </div>

      {/* Right registration form */}
      <div className="flex w-full lg:w-1/2 items-center justify-center p-8 bg-gray-50">
        <form onSubmit={handleSubmit} className="w-full max-w-md space-y-5">
          <div className="lg:hidden text-center mb-4">
            <img src="/logo.svg" alt="Plan International" className="h-14 mx-auto mb-3" />
            <h1 className="text-2xl font-bold text-gray-900">COSME DIP Tracker</h1>
          </div>
          <div className="lg:block hidden">
            <h1 className="text-2xl font-bold text-gray-900">Create Account</h1>
            <p className="text-sm text-gray-500 mt-1">Register to access the DIP Tracker</p>
          </div>

          <label className="block">
            <span className="text-sm font-medium text-gray-700">Full Name *</span>
            <input
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="mt-1 block w-full"
              placeholder="e.g. Jane Doe"
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium text-gray-700">Email *</span>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 block w-full"
              placeholder="you@plan-international.org"
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium text-gray-700">Phone</span>
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="mt-1 block w-full"
              placeholder="+254 7XX XXX XXX"
            />
          </label>

          <div className="grid grid-cols-2 gap-4">
            <label className="block">
              <span className="text-sm font-medium text-gray-700">Password *</span>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 block w-full"
                minLength={6}
              />
            </label>
            <label className="block">
              <span className="text-sm font-medium text-gray-700">Confirm *</span>
              <input
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="mt-1 block w-full"
                minLength={6}
              />
            </label>
          </div>

          <button type="submit" disabled={loading} className="btn-primary w-full justify-center">
            {loading ? 'Creating…' : 'Create Account'}
          </button>

          <p className="text-center text-sm text-gray-500">
            Already have an account?{' '}
            <Link to="/login" className="font-medium text-primary-600 hover:text-primary-700">
              Login here
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}
