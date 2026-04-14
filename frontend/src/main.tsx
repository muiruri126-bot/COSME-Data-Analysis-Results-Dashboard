import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#003b7c',
          colorSuccess: '#2e7d32',
          colorWarning: '#ed6c02',
          colorError: '#d32f2f',
          colorInfo: '#0288d1',
          borderRadius: 8,
          fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
          fontSize: 14,
          colorBgContainer: '#ffffff',
          colorBgLayout: '#f0f2f5',
          boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
        },
        components: {
          Card: {
            borderRadiusLG: 12,
            boxShadowTertiary: '0 1px 4px rgba(0,0,0,0.06)',
          },
          Table: {
            borderRadiusLG: 10,
            headerBg: '#fafafa',
            headerColor: '#1a1a2e',
          },
          Button: {
            borderRadius: 8,
            controlHeight: 36,
          },
          Menu: {
            darkItemBg: 'transparent',
            darkSubMenuItemBg: 'rgba(0,0,0,0.15)',
            darkItemSelectedBg: 'rgba(255,255,255,0.12)',
            darkItemHoverBg: 'rgba(255,255,255,0.08)',
          },
          Tag: {
            borderRadiusSM: 6,
          },
          Statistic: {
            titleFontSize: 13,
            contentFontSize: 28,
          },
        },
      }}
    >
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </ConfigProvider>
  </React.StrictMode>
);
