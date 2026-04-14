import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { List, Badge, Button, Typography, Tag, Space, Empty, Spin, message } from 'antd';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  SendOutlined,
  RollbackOutlined,
  ShoppingCartOutlined,
  TruckOutlined,
  EyeOutlined,
} from '@ant-design/icons';
import api from '../api';

const { Text, Paragraph } = Typography;

const TYPE_CONFIG: Record<string, { color: string; icon: React.ReactNode; label: string }> = {
  SUBMITTED: { color: 'blue', icon: <SendOutlined />, label: 'Submitted' },
  APPROVED: { color: 'green', icon: <CheckCircleOutlined />, label: 'Approved' },
  RETURNED: { color: 'orange', icon: <RollbackOutlined />, label: 'Returned' },
  CANCELLED: { color: 'red', icon: <CloseCircleOutlined />, label: 'Cancelled' },
  PR_RAISED: { color: 'purple', icon: <ShoppingCartOutlined />, label: 'PR Raised' },
  DELIVERED: { color: 'cyan', icon: <TruckOutlined />, label: 'Delivered' },
};

interface Notification {
  id: string;
  type: string;
  title: string;
  message: string;
  line_item_id?: string;
  header_id?: string;
  is_read: boolean;
  created_at: string;
}

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const navigate = useNavigate();

  const fetchNotifications = useCallback(async (p = 1) => {
    setLoading(true);
    try {
      const { data } = await api.get('/notifications', { params: { page: p, limit: 20 } });
      setNotifications(data.data);
      setTotal(data.pagination.total);
    } catch { message.error('Failed to load notifications'); }
    setLoading(false);
  }, []);

  useEffect(() => { fetchNotifications(page); }, [page, fetchNotifications]);

  const markRead = async (id: string) => {
    await api.patch(`/notifications/${id}/read`);
    setNotifications((prev) => prev.map((n) => n.id === id ? { ...n, is_read: true } : n));
  };

  const markAllRead = async () => {
    const { data } = await api.patch('/notifications/read-all');
    message.success(`${data.marked} notifications marked as read`);
    fetchNotifications(page);
  };

  const handleClick = async (n: Notification) => {
    if (!n.is_read) await markRead(n.id);
    if (n.header_id) navigate(`/plans/${n.header_id}`);
  };

  const formatDate = (d: string) => {
    const date = new Date(d);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Typography.Title level={4} style={{ margin: 0 }}>Notifications</Typography.Title>
        <Button size="small" onClick={markAllRead}>Mark all as read</Button>
      </div>

      <Spin spinning={loading}>
        {notifications.length === 0 && !loading ? (
          <Empty description="No notifications" />
        ) : (
          <List
            itemLayout="horizontal"
            dataSource={notifications}
            pagination={{
              current: page,
              total,
              pageSize: 20,
              onChange: setPage,
              showSizeChanger: false,
            }}
            renderItem={(n) => {
              const cfg = TYPE_CONFIG[n.type] || TYPE_CONFIG.SUBMITTED;
              return (
                <List.Item
                  onClick={() => handleClick(n)}
                  style={{
                    cursor: 'pointer',
                    background: n.is_read ? '#fff' : '#f0f5ff',
                    borderRadius: 8,
                    marginBottom: 8,
                    padding: '12px 16px',
                    border: n.is_read ? '1px solid #f0f0f0' : '1px solid #d6e4ff',
                  }}
                  actions={[
                    !n.is_read && (
                      <Button
                        key="read"
                        size="small"
                        type="text"
                        icon={<EyeOutlined />}
                        onClick={(e) => { e.stopPropagation(); markRead(n.id); }}
                      />
                    ),
                  ].filter(Boolean)}
                >
                  <List.Item.Meta
                    avatar={
                      <Badge dot={!n.is_read} offset={[-2, 2]}>
                        <div style={{
                          width: 40, height: 40, borderRadius: 8,
                          background: `${cfg.color}15`, display: 'flex',
                          alignItems: 'center', justifyContent: 'center',
                          fontSize: 18, color: cfg.color,
                        }}>
                          {cfg.icon}
                        </div>
                      </Badge>
                    }
                    title={
                      <Space>
                        <Text strong={!n.is_read}>{n.title}</Text>
                        <Tag color={cfg.color} style={{ fontSize: 11 }}>{cfg.label}</Tag>
                      </Space>
                    }
                    description={
                      <div>
                        <Paragraph
                          style={{ margin: 0, fontSize: 13 }}
                          ellipsis={{ rows: 2 }}
                        >
                          <span dangerouslySetInnerHTML={{ __html: n.message }} />
                        </Paragraph>
                        <Text type="secondary" style={{ fontSize: 12 }}>{formatDate(n.created_at)}</Text>
                      </div>
                    }
                  />
                </List.Item>
              );
            }}
          />
        )}
      </Spin>
    </div>
  );
}
