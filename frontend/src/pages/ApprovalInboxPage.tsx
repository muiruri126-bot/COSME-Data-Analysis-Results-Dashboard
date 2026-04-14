import { useEffect, useState } from 'react';
import { Table, Button, Space, Typography, Tag, Modal, Input, message } from 'antd';
import { CheckOutlined, RollbackOutlined, StopOutlined } from '@ant-design/icons';
import api from '../api';
import { StatusTag, formatCurrency, formatDate } from '../components/StatusTag';
import { useAuthStore } from '../store';

export default function ApprovalInboxPage() {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<string[]>([]);
  const [actionModal, setActionModal] = useState<{ type: string; itemId: string } | null>(null);
  const [comment, setComment] = useState('');
  const [actionLoading, setActionLoading] = useState(false);
  const hasRole = useAuthStore((s) => s.hasRole);

  const fetchItems = async () => {
    setLoading(true);
    try {
      const { data } = await api.get('/reports/approval-ageing');
      setItems(data);
    } catch {
      message.error('Failed to load approval items');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchItems(); }, []);

  const handleAction = async () => {
    if (!actionModal) return;
    setActionLoading(true);
    try {
      const { type, itemId } = actionModal;
      const body = type === 'cancel' ? { reason: comment } : { comment };
      await api.post(`/approvals/${itemId}/${type}`, body);
      message.success(`Item ${type}d`);
      setActionModal(null);
      setComment('');
      fetchItems();
    } catch (err: any) {
      const errorMsg = err.response?.data?.error?.message || err.response?.data?.error || 'Action failed';
      message.error(typeof errorMsg === 'string' ? errorMsg : 'Action failed');
    } finally {
      setActionLoading(false);
    }
  };

  const handleBulkApprove = async () => {
    if (selected.length === 0) { message.info('Select items first'); return; }
    try {
      const { data } = await api.post('/approvals/bulk-approve', { line_item_ids: selected, comment: 'Bulk approved from inbox' });
      message.success(`${data.approved?.length || 0} approved, ${data.errors?.length || 0} errors`);
      setSelected([]);
      fetchItems();
    } catch (err: any) {
      const errorMsg = err.response?.data?.error?.message || err.response?.data?.error || 'Bulk approve failed';
      message.error(typeof errorMsg === 'string' ? errorMsg : 'Bulk approve failed');
    }
  };

  const columns = [
    { title: 'Line Item Ref', dataIndex: 'line_item_ref', width: 140 },
    { title: 'Description', dataIndex: 'item_description', ellipsis: true },
    { title: 'Status', dataIndex: 'status', width: 170, render: (s: string) => <StatusTag status={s} /> },
    { title: 'Est. Cost', dataIndex: 'estimated_total_cost', width: 130, render: (v: number, r: any) => formatCurrency(v, r.currency_code) },
    {
      title: 'Days in Status',
      dataIndex: 'days_in_status',
      width: 110,
      sorter: (a: any, b: any) => a.days_in_status - b.days_in_status,
      render: (v: number) => <Tag color={v > 5 ? 'red' : v > 3 ? 'orange' : 'green'}>{v} days</Tag>,
    },
    { title: 'Tracking No', dataIndex: 'tracking_no', width: 120 },
    { title: 'Project', dataIndex: 'project_name', ellipsis: true },
    { title: 'Approver', dataIndex: 'approver', width: 130 },
    { title: 'Location', dataIndex: 'location', width: 120 },
    {
      title: 'Actions',
      width: 140,
      render: (_: any, r: any) => (
        <Space size="small">
          {r.status === 'Submitted for Approval' && hasRole('Project/Department Manager', 'System Admin') && (
            <>
              <Button size="small" type="primary" icon={<CheckOutlined />}
                onClick={() => setActionModal({ type: 'approve', itemId: r.id })} />
              <Button size="small" icon={<RollbackOutlined />}
                onClick={() => setActionModal({ type: 'return', itemId: r.id })} />
            </>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Typography.Title level={4}>Approval Inbox</Typography.Title>

      <div className="table-actions">
        <Typography.Text type="secondary">{items.length} items pending action</Typography.Text>
        {hasRole('Project/Department Manager', 'System Admin') && selected.length > 0 && (
          <Button type="primary" onClick={handleBulkApprove}>
            Bulk Approve ({selected.length})
          </Button>
        )}
      </div>

      <Table
        dataSource={items}
        columns={columns}
        rowKey="id"
        loading={loading}
        rowSelection={{
          selectedRowKeys: selected,
          onChange: (keys) => setSelected(keys as string[]),
        }}
        size="middle"
        scroll={{ x: 1300 }}
        pagination={{ pageSize: 20, showTotal: (t) => `${t} items` }}
      />

      <Modal
        title={actionModal?.type === 'approve' ? 'Approve Item' : 'Return Item'}
        open={!!actionModal}
        onOk={handleAction}
        onCancel={() => { setActionModal(null); setComment(''); }}
        confirmLoading={actionLoading}
      >
        <Input.TextArea rows={3} value={comment} onChange={(e) => setComment(e.target.value)}
          placeholder="Comment..." />
      </Modal>
    </div>
  );
}
