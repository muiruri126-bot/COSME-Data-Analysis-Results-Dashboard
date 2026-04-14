import { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Form, Input, Button, Card, Typography, message, Steps, Result, Divider,
} from 'antd';
import { KeyOutlined } from '@ant-design/icons';
import api from '../api';

export default function ForgotPasswordPage() {
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState('');
  const [devCode, setDevCode] = useState<string | null>(null);

  const onRequestCode = async (values: { email: string }) => {
    setLoading(true);
    try {
      const { data } = await api.post('/auth/forgot-password', { email: values.email });
      setEmail(values.email);
      if (data._dev_reset_code) setDevCode(data._dev_reset_code);
      message.success('Reset code generated. Check your email (in dev mode, see below).');
      setStep(1);
    } catch (err: any) {
      message.error(err.response?.data?.error?.message || err.response?.data?.error || 'Failed to request reset code');
    } finally {
      setLoading(false);
    }
  };

  const onResetPassword = async (values: { reset_code: string; new_password: string; confirm_password: string }) => {
    setLoading(true);
    try {
      await api.post('/auth/reset-password', { email, reset_code: values.reset_code, new_password: values.new_password, confirm_password: values.confirm_password });
      message.success('Password updated successfully!');
      setStep(2);
    } catch (err: any) {
      message.error(err.response?.data?.error?.message || err.response?.data?.error || 'Password reset failed');
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
        <Card className="login-card" bordered={false} style={{ maxWidth: 460 }}>
          <div style={{ textAlign: 'center', marginBottom: 24 }}>
            <img src="/plan-logo.svg" alt="Plan International" style={{ height: 52, marginBottom: 16 }} />
            <Typography.Title level={4} style={{ margin: 0, fontWeight: 700, color: '#1a1a2e' }}>
              Reset Password
            </Typography.Title>
            <Typography.Text type="secondary" style={{ fontSize: 13 }}>
              COSME Procurement Tracker
            </Typography.Text>
          </div>

          <Steps
            current={step}
            size="small"
            style={{ marginBottom: 16 }}
            items={[{ title: 'Email' }, { title: 'Reset Code' }, { title: 'Done' }]}
          />
          <Divider style={{ margin: '4px 0 16px' }} />

          {step === 0 && (
            <Form onFinish={onRequestCode} layout="vertical" size="large">
              <Typography.Paragraph type="secondary" style={{ fontSize: 13, marginBottom: 16 }}>
                Enter the email address associated with your account. We will generate a reset code.
              </Typography.Paragraph>
              <Form.Item label="Email" name="email" rules={[{ required: true, type: 'email', message: 'Enter a valid email' }]}>
                <Input placeholder="Enter your email" />
              </Form.Item>
              <Form.Item style={{ marginBottom: 16 }}>
                <Button type="primary" htmlType="submit" loading={loading} block className="login-btn">
                  Send Reset Code
                </Button>
              </Form.Item>
            </Form>
          )}

          {step === 1 && (
            <Form onFinish={onResetPassword} layout="vertical" size="large">
              <Typography.Paragraph type="secondary" style={{ fontSize: 13, marginBottom: 8 }}>
                Enter the 6-digit reset code sent to <strong>{email}</strong> and your new password.
              </Typography.Paragraph>
              {devCode && (
                <div style={{ background: '#fffbe6', border: '1px solid #ffe58f', borderRadius: 8, padding: '8px 12px', marginBottom: 16, textAlign: 'center' }}>
                  <Typography.Text style={{ fontSize: 12 }}>
                    <strong>DEV MODE</strong> — Reset code: <code style={{ fontSize: 16, fontWeight: 700, color: '#003b7c' }}>{devCode}</code>
                  </Typography.Text>
                </div>
              )}
              <Form.Item label="Reset Code" name="reset_code" rules={[{ required: true, message: 'Enter the 6-digit code' }, { len: 6, message: 'Code must be 6 digits' }]}>
                <Input prefix={<KeyOutlined />} placeholder="6-digit reset code" maxLength={6} style={{ letterSpacing: 8, textAlign: 'center', fontSize: 18, fontWeight: 600 }} />
              </Form.Item>
              <Form.Item label="New Password" name="new_password" rules={[{ required: true, message: 'Enter a new password' }, { min: 8, message: 'Password must be at least 8 characters' }]}>
                <Input.Password placeholder="New password" />
              </Form.Item>
              <Form.Item label="Confirm Password" name="confirm_password" dependencies={['new_password']} rules={[{ required: true, message: 'Confirm your new password' }, ({ getFieldValue }) => ({ validator(_, value) { if (!value || getFieldValue('new_password') === value) return Promise.resolve(); return Promise.reject(new Error('Passwords do not match')); } })]}>
                <Input.Password placeholder="Confirm new password" />
              </Form.Item>
              <Form.Item style={{ marginBottom: 16 }}>
                <Button type="primary" htmlType="submit" loading={loading} block className="login-btn">
                  Reset Password
                </Button>
              </Form.Item>
              <Button type="link" size="small" onClick={() => { setStep(0); setDevCode(null); }}>
                ← Use a different email
              </Button>
            </Form>
          )}

          {step === 2 && (
            <Result
              status="success"
              title="Password Reset Successfully"
              subTitle="You can now sign in with your new password."
              extra={<Link to="/login"><Button type="primary" size="large" className="login-btn">Go to Sign In</Button></Link>}
            />
          )}

          {step < 2 && (
            <div style={{ textAlign: 'center', marginTop: 8 }}>
              <Typography.Text style={{ fontSize: 13 }}>
                Remember your password?{' '}
                <Link to="/login" style={{ fontWeight: 600, color: '#c41e3a' }}>Sign In</Link>
              </Typography.Text>
            </div>
          )}
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
