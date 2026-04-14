import { useState, useEffect, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu, Avatar, Dropdown, Typography, Badge, Breadcrumb } from 'antd';
import api from '../api';
import {
  DashboardOutlined,
  FileTextOutlined,
  CheckCircleOutlined,
  ShoppingCartOutlined,
  TruckOutlined,
  InboxOutlined,
  SwapOutlined,
  BarChartOutlined,
  UserOutlined,
  AuditOutlined,
  LogoutOutlined,
  SettingOutlined,
  BellOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons';
import { useAuthStore } from '../store';

const { Header, Sider, Content } = Layout;

const BREADCRUMB_MAP: Record<string, string> = {
  '/': 'Dashboard',
  '/plans': 'Procurement Plans',
  '/plans/new': 'New Plan',
  '/approvals': 'Approval Inbox',
  '/purchase-requisitions': 'Purchase Requisitions',
  '/deliveries': 'Deliveries',
  '/stock-assets': 'Stock & Assets',
  '/exchange-rates': 'Exchange Rates',
  '/reports': 'Reports',
  '/notifications': 'Notifications',
  '/admin/users': 'Users & Roles',
  '/admin/audit-log': 'Audit Log',
};

// Role-based access per the user guide navigation table
// Empty array = all authenticated users
const ALL_MENU_ITEMS: Array<{
  key: string;
  icon: React.ReactNode;
  label: string;
  roles?: string[];            // roles allowed; omit = all users
  children?: Array<{ key: string; icon: React.ReactNode; label: string; roles?: string[] }>;
}> = [
  { key: '/', icon: <DashboardOutlined />, label: 'Dashboard' },
  { key: '/plans', icon: <FileTextOutlined />, label: 'Procurement Plans' },
  { key: '/approvals', icon: <CheckCircleOutlined />, label: 'Approval Inbox', roles: ['Manager', 'Finance', 'Admin'] },
  { key: '/purchase-requisitions', icon: <ShoppingCartOutlined />, label: 'Purchase Requisitions', roles: ['Supply Chain', 'Admin'] },
  { key: '/deliveries', icon: <TruckOutlined />, label: 'Deliveries', roles: ['Supply Chain', 'Stores', 'Admin'] },
  { key: '/stock-assets', icon: <InboxOutlined />, label: 'Stock & Assets', roles: ['Stores', 'Admin'] },
  { key: '/exchange-rates', icon: <SwapOutlined />, label: 'Exchange Rates', roles: ['Finance', 'Admin'] },
  { key: '/reports', icon: <BarChartOutlined />, label: 'Reports' },
  { key: '/notifications', icon: <BellOutlined />, label: 'Notifications' },
  {
    key: 'admin',
    icon: <SettingOutlined />,
    label: 'Admin',
    roles: ['Admin'],
    children: [
      { key: '/admin/users', icon: <UserOutlined />, label: 'Users & Roles', roles: ['Admin'] },
      { key: '/admin/audit-log', icon: <AuditOutlined />, label: 'Audit Log', roles: ['Admin'] },
    ],
  },
];

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const [collapsed, setCollapsed] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout, hasRole, token } = useAuthStore();

  const fetchUnread = useCallback(async () => {
    try {
      const { data } = await api.get('/notifications/unread-count');
      setUnreadCount(data.count);
    } catch { /* ignore */ }
  }, []);

  useEffect(() => {
    if (!token) return;
    fetchUnread();
    const interval = setInterval(fetchUnread, 30000); // poll every 30s
    return () => clearInterval(interval);
  }, [token, fetchUnread]);

  // Filter menu items based on user roles
  const menuItems = ALL_MENU_ITEMS.filter((item) => {
    if (!item.roles) return true; // No role restriction = all users
    return hasRole(...item.roles);
  }).map((item) => {
    if (item.children) {
      return {
        ...item,
        children: item.children.filter((child) => {
          if (!child.roles) return true;
          return hasRole(...child.roles);
        }),
      };
    }
    return item;
  }).filter((item) => !item.children || item.children.length > 0);

  const selectedKeys = [location.pathname];
  const openKeys = location.pathname.startsWith('/admin') ? ['admin'] : [];

  const breadcrumbTitle = BREADCRUMB_MAP[location.pathname]
    || (location.pathname.startsWith('/plans/') ? 'Plan Details' : 'Page');

  const userMenu = {
    items: [
      { key: 'name', label: <span style={{ fontWeight: 600 }}>{user?.fullName}</span>, disabled: true },
      { key: 'roles', label: <span style={{ color: '#888', fontSize: 12 }}>{user?.roles.map((r) => r.roleName).join(', ')}</span>, disabled: true },
      { type: 'divider' as const },
      { key: 'logout', icon: <LogoutOutlined />, label: 'Sign Out', danger: true },
    ],
    onClick: ({ key }: { key: string }) => {
      if (key === 'logout') {
        logout();
        navigate('/login');
      }
    },
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        trigger={null}
        width={250}
        style={{
          background: 'linear-gradient(180deg, #001529 0%, #002140 50%, #001529 100%)',
          borderRight: '1px solid rgba(255,255,255,0.04)',
        }}
      >
        <div className="sidebar-logo">
          <img
            src="/plan-logo-white.svg"
            alt="Plan International"
            style={{ height: 32, flexShrink: 0 }}
          />
          {!collapsed && (
            <div style={{ display: 'flex', flexDirection: 'column', lineHeight: 1.2 }}>
              <span style={{ color: '#fff', fontSize: 14, fontWeight: 700, letterSpacing: 0.5 }}>COSME</span>
              <span style={{ color: 'rgba(255,255,255,0.6)', fontSize: 10, fontWeight: 500, letterSpacing: 1 }}>PROCUREMENT</span>
            </div>
          )}
        </div>
        <Menu
          theme="dark"
          selectedKeys={selectedKeys}
          defaultOpenKeys={openKeys}
          mode="inline"
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          style={{ background: 'transparent', borderRight: 'none' }}
        />
      </Sider>
      <Layout>
        <Header className="app-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <span
              onClick={() => setCollapsed(!collapsed)}
              style={{ cursor: 'pointer', fontSize: 18, color: '#555', padding: 4 }}
            >
              {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            </span>
            <Breadcrumb
              items={[
                { title: 'COSME' },
                { title: breadcrumbTitle },
              ]}
            />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <Badge count={unreadCount} size="small" offset={[-2, 2]} overflowCount={99}>
              <BellOutlined style={{ fontSize: 18, color: '#666', cursor: 'pointer' }} onClick={() => navigate('/notifications')} />
            </Badge>
            <Dropdown menu={userMenu} placement="bottomRight">
              <div className="app-header-user">
                <Avatar
                  size={34}
                  style={{ background: 'linear-gradient(135deg, #003b7c, #0066cc)', fontWeight: 600 }}
                >
                  {user?.fullName?.split(' ').map(n => n[0]).join('').slice(0, 2)}
                </Avatar>
                <div style={{ lineHeight: 1.3 }}>
                  <div className="app-header-user-name">{user?.fullName}</div>
                  <div className="app-header-user-role">{user?.roles[0]?.roleName}</div>
                </div>
              </div>
            </Dropdown>
          </div>
        </Header>
        <Content style={{ margin: 0, padding: 24, background: '#f0f2f5', overflow: 'auto', flex: 1 }}>
          {children}
        </Content>
        <div className="app-footer">
          <img src="/plan-logo.svg" alt="Plan International" style={{ height: 28, opacity: 0.5 }} />
          <span>© {new Date().getFullYear()} Plan International Kenya — COSME Procurement Tracker</span>
        </div>
      </Layout>
    </Layout>
  );
}
