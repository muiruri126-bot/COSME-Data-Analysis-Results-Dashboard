import { useState } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import api from '../lib/api';

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') || '';
  const navigate = useNavigate();

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }
    if (!token) {
      toast.error('Invalid reset link — no token provided');
      return;
    }
    setLoading(true);
    try {
      await api.post('/auth/reset-password', { token, password });
      setSuccess(true);
      toast.success('Password reset successfully!');
    } catch (err: any) {
      toast.error(err.response?.data?.error || 'Failed to reset password');
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

      {/* Right form */}
      <div className="flex w-full lg:w-1/2 items-center justify-center p-8 bg-gray-50">
        <div className="w-full max-w-md space-y-6">
          <div className="lg:hidden text-center mb-4">
            <img src="/logo.svg" alt="Plan International" className="h-14 mx-auto mb-3" />
            <h1 className="text-2xl font-bold text-gray-900">COSME DIP Tracker</h1>
          </div>

          {!success ? (
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Reset Password</h1>
                <p className="text-sm text-gray-500 mt-1">Enter your new password below.</p>
              </div>

              <label className="block">
                <span className="text-sm font-medium text-gray-700">New Password *</span>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="mt-1 block w-full"
                  minLength={6}
                  placeholder="At least 6 characters"
                />
              </label>

              <label className="block">
                <span className="text-sm font-medium text-gray-700">Confirm Password *</span>
                <input
                  type="password"
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="mt-1 block w-full"
                  minLength={6}
                />
              </label>

              <button type="submit" disabled={loading} className="btn-primary w-full justify-center">
                {loading ? 'Resetting…' : 'Reset Password'}
              </button>

              <p className="text-center text-sm text-gray-500">
                <Link to="/login" className="font-medium text-primary-600 hover:text-primary-700">
                  Back to Login
                </Link>
              </p>
            </form>
          ) : (
            <div className="text-center space-y-4">
              <div className="h-16 w-16 rounded-full bg-green-100 flex items-center justify-center mx-auto">
                <svg className="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h2 className="text-xl font-bold text-gray-900">Password Reset Complete</h2>
              <p className="text-sm text-gray-500">
                Your password has been updated. You can now sign in with your new password.
              </p>
              <Link to="/login" className="btn-primary inline-flex justify-center">
                Go to Login
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
