import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Form, Input, Button, Card, Typography, message } from 'antd';
import { UserAddOutlined } from '@ant-design/icons';
import api from '../api';
import { useAuthStore } from '../store';

export default function RegisterPage() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const login = useAuthStore((s) => s.login);

  const onFinish = async (values: {
    full_name: string;
    email: string;
    password: string;
    confirm_password: string;
  }) => {
    setLoading(true);
    try {
      const { data } = await api.post('/auth/register', values);
      login(data.token, data.user);
      message.success(`Welcome, ${data.user.fullName}! Your account has been created.`);
      navigate('/');
    } catch (err: any) {
      message.error(
        err.response?.data?.error?.message ||
        err.response?.data?.error ||
        'Registration failed',
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-topbar">
        <img src="/plan-logo-white.svg" alt="Plan International" className="login-topbar-logo" />
        <div className="login-topbar-text">
          <span className="login-topbar-title">COSME PROCUREMENT</span>
          <span className="login-topbar-subtitle">TRACKER</span>
        </div>
      </div>

      <div className="login-body">
        <Card className="login-card" bordered={false}>
          <div style={{ textAlign: 'center', marginBottom: 24 }}>
            <img src="/plan-logo.svg" alt="Plan International" style={{ height: 52, marginBottom: 16 }} />
            <Typography.Title level={4} style={{ margin: 0, fontWeight: 700, color: '#1a1a2e' }}>
              Create Account
            </Typography.Title>
            <Typography.Text type="secondary" style={{ fontSize: 13 }}>
              COSME Procurement Tracker
            </Typography.Text>
          </div>

          <Form onFinish={onFinish} layout="vertical" size="large">
            <Form.Item
              label="Full Name"
              name="full_name"
              rules={[{ required: true, message: 'Enter your full name' }]}
            >
              <Input placeholder="Enter your full name" />
            </Form.Item>
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
              rules={[
                { required: true, message: 'Enter a password' },
                { min: 8, message: 'Password must be at least 8 characters' },
              ]}
            >
              <Input.Password placeholder="Enter your password" />
            </Form.Item>
            <Form.Item
              label="Confirm Password"
              name="confirm_password"
              dependencies={['password']}
              rules={[
                { required: true, message: 'Confirm your password' },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue('password') === value) return Promise.resolve();
                    return Promise.reject(new Error('Passwords do not match'));
                  },
                }),
              ]}
            >
              <Input.Password placeholder="Confirm your password" />
            </Form.Item>
            <Form.Item style={{ marginBottom: 16 }}>
              <Button
                type="primary" htmlType="submit" loading={loading} block
                icon={<UserAddOutlined />}
                className="login-btn"
              >
                Create Account
              </Button>
            </Form.Item>
          </Form>

          <div style={{ textAlign: 'center' }}>
            <Typography.Text style={{ fontSize: 13 }}>
              Already have an account?{' '}
              <Link to="/login" style={{ fontWeight: 600, color: '#c41e3a' }}>Sign In</Link>
            </Typography.Text>
          </div>
        </Card>
      </div>

      <div className="login-footer">
        <img src="/plan-logo.svg" alt="Plan International" style={{ height: 32, opacity: 0.6 }} />
        <Typography.Text type="secondary" style={{ fontSize: 12 }}>
          © {new Date().getFullYear()} Plan International Kenya — COSME Procurement Tracker
        </Typography.Text>
      </div>
    </div>
  );
}
