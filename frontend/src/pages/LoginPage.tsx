import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Form, Input, Button, Card, Typography, message } from 'antd';
import { LoginOutlined } from '@ant-design/icons';
import api from '../api';
import { useAuthStore } from '../store';

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const login = useAuthStore((s) => s.login);

  const onFinish = async (values: { email: string; password: string }) => {
    setLoading(true);
    try {
      const { data } = await api.post('/auth/login', values);
      login(data.token, data.user);
      message.success(`Welcome, ${data.user.fullName}`);
      navigate('/');
    } catch (err: any) {
      message.error(err.response?.data?.error?.message || err.response?.data?.error || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      {/* Top header bar */}
      <div className="login-topbar">
        <img src="/plan-logo-white.svg" alt="Plan International" className="login-topbar-logo" />
        <div className="login-topbar-text">
          <span className="login-topbar-title">COSME PROCUREMENT</span>
          <span className="login-topbar-subtitle">TRACKER</span>
        </div>
      </div>

      {/* Main content */}
      <div className="login-body">
        <Card className="login-card" bordered={false}>
          <div style={{ textAlign: 'center', marginBottom: 24 }}>
            <img src="/plan-logo.svg" alt="Plan International" style={{ height: 52, marginBottom: 16 }} />
            <Typography.Title level={4} style={{ margin: 0, fontWeight: 700, color: '#1a1a2e' }}>
              COSME Procurement Tracker
            </Typography.Title>
          </div>

          <Form onFinish={onFinish} layout="vertical" size="large">
            <Form.Item
              label="Email"
              name="email"
              rules={[{ required: true, type: 'email', message: 'Enter a valid email' }]}
            >
              <Input placeholder="Enter your email" />
            </Form.Item>
            <Form.Item
              label="Password"
              name="password"
              rules={[{ required: true, message: 'Enter your password' }]}
            >
              <Input.Password placeholder="Enter your password" />
            </Form.Item>
            <Form.Item style={{ marginBottom: 16 }}>
              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
                block
                icon={<LoginOutlined />}
                className="login-btn"
              >
                Login
              </Button>
            </Form.Item>
          </Form>

          <div style={{ textAlign: 'center' }}>
            <Typography.Text style={{ fontSize: 13 }}>
              Don&apos;t have an account?{' '}
              <Link to="/register" style={{ fontWeight: 600, color: '#c41e3a' }}>Register here</Link>
            </Typography.Text>
            <br />
            <Link to="/forgot-password" style={{ fontSize: 13, color: '#c41e3a' }}>Forgot your password?</Link>
          </div>
        </Card>
      </div>

      {/* Footer */}
      <div className="login-footer">
        <img src="/plan-logo.svg" alt="Plan International" style={{ height: 32, opacity: 0.6 }} />
        <Typography.Text type="secondary" style={{ fontSize: 12 }}>
          © {new Date().getFullYear()} Plan International Kenya — COSME Procurement Tracker
        </Typography.Text>
      </div>
    </div>
  );
}
