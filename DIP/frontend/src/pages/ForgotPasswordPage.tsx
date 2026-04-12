import { useState } from 'react';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import api from '../lib/api';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post('/auth/forgot-password', { email });
      setSent(true);
      toast.success('Check your email for a reset link');
    } catch (err: any) {
      toast.error(err.response?.data?.error || 'Something went wrong');
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

          {!sent ? (
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Forgot Password</h1>
                <p className="text-sm text-gray-500 mt-1">
                  Enter the email address associated with your account and we'll send you a link to reset your password.
                </p>
              </div>

              <label className="block">
                <span className="text-sm font-medium text-gray-700">Email Address *</span>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="mt-1 block w-full"
                  placeholder="you@plan-international.org"
                />
              </label>

              <button type="submit" disabled={loading} className="btn-primary w-full justify-center">
                {loading ? 'Sending…' : 'Send Reset Link'}
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
              <h2 className="text-xl font-bold text-gray-900">Check Your Email</h2>
              <p className="text-sm text-gray-500">
                If an account with <strong>{email}</strong> exists, we've sent a password reset link.
                Check your inbox and spam folder.
              </p>
              <Link to="/login" className="btn-primary inline-flex justify-center">
                Back to Login
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
