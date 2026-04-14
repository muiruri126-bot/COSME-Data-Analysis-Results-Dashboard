import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Card, Descriptions, Table, Button, Space, Typography, Tag, Modal, Input,
  message, Spin, Popconfirm, Tabs, Upload, Tooltip, Row, Col, Statistic,
} from 'antd';
import {
  CheckOutlined, RollbackOutlined, StopOutlined, SendOutlined,
  DownloadOutlined, UploadOutlined, DeleteOutlined, PlusOutlined,
} from '@ant-design/icons';
import api from '../api';
import { StatusTag, formatCurrency, formatDate } from '../components/StatusTag';
import { useAuthStore } from '../store';

export default function PlanDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [plan, setPlan] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [actionModal, setActionModal] = useState<{ type: string; itemId: string } | null>(null);
  const [actionComment, setActionComment] = useState('');
  const [actionLoading, setActionLoading] = useState(false);
  const [comments, setComments] = useState<any[]>([]);
  const [newComment, setNewComment] = useState('');
  const hasRole = useAuthStore((s) => s.hasRole);

  const fetchPlan = async () => {
    try {
      const { data } = await api.get(`/procurement-plans/${id}`);
      setPlan(data);
    } catch {
      message.error('Failed to load plan');
    } finally {
      setLoading(false);
    }
  };

  const fetchComments = async () => {
    try {
      const { data } = await api.get('/comments', { params: { entity_type: 'procurement_plan', entity_id: id } });
      setComments(data);
    } catch { /* ignore */ }
  };

  useEffect(() => { fetchPlan(); fetchComments(); }, [id]);

  const handleApprovalAction = async () => {
    if (!actionModal) return;
    setActionLoading(true);
    try {
      const { type, itemId } = actionModal;
      const endpoint = `/approvals/${itemId}/${type}`;
      const body = type === 'cancel'
        ? { reason: actionComment }
        : { comment: actionComment };
      await api.post(endpoint, body);
      message.success(`Item ${type}d successfully`);
      setActionModal(null);
      setActionComment('');
      fetchPlan();
    } catch (err: any) {
      message.error(err.response?.data?.error?.message || err.response?.data?.error || `Failed to ${actionModal.type}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleSubmit = async (itemId: string) => {
    try {
      await api.post(`/line-items/${itemId}/submit`);
      message.success('Item submitted for approval');
      fetchPlan();
    } catch (err: any) {
      message.error(err.response?.data?.error?.message || err.response?.data?.error || 'Failed to submit');
    }
  };

  const handleBulkSubmit = async () => {
    const draftIds = plan.lineItems
      .filter((li: any) => li.status === 'Draft')
      .map((li: any) => li.id);
    if (draftIds.length === 0) { message.info('No draft items to submit'); return; }
    try {
      const { data } = await api.post('/line-items/bulk-submit', { line_item_ids: draftIds });
      message.success(`${data.submitted?.length || 0} items submitted`);
      fetchPlan();
    } catch (err: any) {
      message.error(err.response?.data?.error?.message || err.response?.data?.error || 'Bulk submit failed');
    }
  };

  const handleBulkApprove = async () => {
    const submittedIds = plan.lineItems
      .filter((li: any) => li.status === 'Submitted for Approval')
      .map((li: any) => li.id);
    if (submittedIds.length === 0) { message.info('No items pending approval'); return; }
    try {
      const { data } = await api.post('/approvals/bulk-approve', { line_item_ids: submittedIds, comment: 'Bulk approved' });
      message.success(`${data.approved?.length || 0} items approved`);
      fetchPlan();
    } catch (err: any) {
      message.error(err.response?.data?.error?.message || err.response?.data?.error || 'Bulk approve failed');
    }
  };

  const handleExport = () => {
    window.open(`/api/v1/import-export/export/${id}`, '_blank');
  };

  const handleAddComment = async () => {
    if (!newComment.trim()) return;
    try {
      await api.post('/comments', { entity_type: 'procurement_plan', entity_id: id, comment_text: newComment });
      setNewComment('');
      fetchComments();
    } catch { message.error('Failed to add comment'); }
  };

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;
  if (!plan) return <Typography.Text>Plan not found.</Typography.Text>;

  const lineItemColumns = [
    { title: '#', key: 'lineNumber', width: 40, render: (_: any, __: any, idx: number) => idx + 1 },
    { title: 'Ref', dataIndex: 'lineItemRef', width: 130 },
    { title: 'Material Group', dataIndex: ['materialGroup', 'groupName'], width: 160, ellipsis: true },
    { title: 'Type', dataIndex: 'itemType', width: 70 },
    { title: 'Description', dataIndex: 'itemDescription', ellipsis: true },
    { title: 'Qty', dataIndex: 'quantity', width: 60, render: (v: any) => Number(v) },
    { title: 'UoM', dataIndex: ['uom', 'uomCode'], width: 60 },
    { title: 'Unit Price', dataIndex: 'estimatedUnitPrice', width: 110, render: (v: any, r: any) => formatCurrency(Number(v), r.currencyCode) },
    { title: 'Total Cost', dataIndex: 'estimatedTotalCost', width: 130, render: (v: any, r: any) => formatCurrency(Number(v), r.currencyCode) },
    { title: 'Location', dataIndex: ['location', 'locationName'], width: 100 },
    { title: 'Month', dataIndex: 'month', width: 55 },
    { title: 'Quarter', dataIndex: 'quarter', width: 65 },
    {
      title: 'Status',
      dataIndex: 'status',
      width: 170,
      render: (s: string) => <StatusTag status={s} />,
    },
    { title: 'Sourcing', dataIndex: ['sourcingMethod', 'methodName'], width: 120, ellipsis: true },
    { title: 'Est. Delivery', dataIndex: 'estimatedDeliveryDate', width: 110, render: (v: any) => v ? formatDate(v) : '-' },
    {
      title: 'Actions',
      width: 180,
      fixed: 'right' as const,
      render: (_: any, r: any) => (
        <Space size="small">
          {r.status === 'Draft' && hasRole('Requester', 'System Admin') && (
            <Tooltip title="Submit for Approval">
              <Button size="small" icon={<SendOutlined />} onClick={() => handleSubmit(r.id)} />
            </Tooltip>
          )}
          {r.status === 'Submitted for Approval' && hasRole('Project/Department Manager') && (
            <>
              <Tooltip title="Approve">
                <Button size="small" type="primary" icon={<CheckOutlined />}
                  onClick={() => setActionModal({ type: 'approve', itemId: r.id })} />
              </Tooltip>
              <Tooltip title="Return">
                <Button size="small" icon={<RollbackOutlined />}
                  onClick={() => setActionModal({ type: 'return', itemId: r.id })} />
              </Tooltip>
            </>
          )}
          {!['Delivered/Closed', 'Cancelled'].includes(r.status) && hasRole('Project/Department Manager', 'System Admin') && (
            <Tooltip title="Cancel">
              <Button size="small" danger icon={<StopOutlined />}
                onClick={() => setActionModal({ type: 'cancel', itemId: r.id })} />
            </Tooltip>
          )}
        </Space>
      ),
    },
  ];

  const statusSummary = plan.line_item_status_summary || {};

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button onClick={() => navigate('/plans')}>Back to Plans</Button>
        <Button icon={<DownloadOutlined />} onClick={handleExport}>Export Excel</Button>
        {hasRole('Requester', 'System Admin') && (
          <Button type="primary" onClick={handleBulkSubmit}>Submit All Drafts</Button>
        )}
        {hasRole('Project/Department Manager') && (
          <Button type="primary" onClick={handleBulkApprove}>Approve All Submitted</Button>
        )}
      </Space>

      <Tabs
        items={[
          {
            key: 'details',
            label: 'Plan Details',
            children: (
              <>
                <Card style={{ marginBottom: 16 }}>
                  <Descriptions bordered column={{ xs: 1, sm: 2, lg: 3 }} size="small">
                    <Descriptions.Item label="Tracking No">{plan.trackingNo}</Descriptions.Item>
                    <Descriptions.Item label="Plan Type">{plan.typeOfProcurementPlan}</Descriptions.Item>
                    <Descriptions.Item label="Financial Year">{plan.financialYear}</Descriptions.Item>
                    <Descriptions.Item label="Global/Regional Hub">{plan.globalRegionalHub}</Descriptions.Item>
                    <Descriptions.Item label="Country Office">{plan.countryOffice}</Descriptions.Item>
                    <Descriptions.Item label="Currency">{plan.currency}</Descriptions.Item>
                    <Descriptions.Item label="Project">{plan.project?.projectName}</Descriptions.Item>
                    <Descriptions.Item label="Project Code">{plan.projectCodeCostCentre}</Descriptions.Item>
                    <Descriptions.Item label="FAD/SPAD">{plan.fadSpadNumber}</Descriptions.Item>
                    <Descriptions.Item label="Donor">{plan.donorName}</Descriptions.Item>
                    <Descriptions.Item label="Funding Source">{plan.fundingSource?.sourceName}</Descriptions.Item>
                    <Descriptions.Item label="Department Manager">{plan.departmentManager?.fullName}</Descriptions.Item>
                    <Descriptions.Item label="Start Date">{formatDate(plan.startDate)}</Descriptions.Item>
                    <Descriptions.Item label="End Date">{formatDate(plan.endDate)}</Descriptions.Item>
                    <Descriptions.Item label="Header Status">
                      <StatusTag status={plan.headerStatus} />
                    </Descriptions.Item>
                    <Descriptions.Item label="Days Remaining">{plan.days_remaining_until_project_end_date}</Descriptions.Item>
                    <Descriptions.Item label="Total Line Items">{plan.total_line_items}</Descriptions.Item>
                    <Descriptions.Item label="Created">{formatDate(plan.createdAt)}</Descriptions.Item>
                  </Descriptions>
                </Card>

                {/* Status Summary */}
                <Row gutter={[8, 8]} style={{ marginBottom: 16 }}>
                  {Object.entries(statusSummary).map(([status, count]: any) => (
                    <Col key={status} xs={12} sm={8} md={6} lg={4}>
                      <Card size="small"><Statistic title={status} value={count} /></Card>
                    </Col>
                  ))}
                </Row>

                <Table
                  dataSource={plan.lineItems || []}
                  columns={lineItemColumns}
                  rowKey="id"
                  size="small"
                  scroll={{ x: 1600 }}
                  pagination={false}
                />
              </>
            ),
          },
          {
            key: 'comments',
            label: `Comments (${comments.length})`,
            children: (
              <Card>
                {comments.map((c) => (
                  <div key={c.id} style={{ marginBottom: 12, padding: 8, background: '#fafafa', borderRadius: 6 }}>
                    <strong>{c.author?.fullName}</strong>
                    <span style={{ marginLeft: 8, color: '#999', fontSize: 12 }}>{formatDate(c.createdAt)}</span>
                    <p style={{ margin: '4px 0 0' }}>{c.commentText}</p>
                  </div>
                ))}
                <Space.Compact style={{ width: '100%', marginTop: 12 }}>
                  <Input value={newComment} onChange={(e) => setNewComment(e.target.value)}
                    placeholder="Add a comment..." onPressEnter={handleAddComment} />
                  <Button type="primary" onClick={handleAddComment}>Post</Button>
                </Space.Compact>
              </Card>
            ),
          },
        ]}
      />

      {/* Approval Action Modal */}
      <Modal
        title={`${actionModal?.type === 'approve' ? 'Approve' : actionModal?.type === 'return' ? 'Return' : 'Cancel'} Line Item`}
        open={!!actionModal}
        onOk={handleApprovalAction}
        onCancel={() => { setActionModal(null); setActionComment(''); }}
        confirmLoading={actionLoading}
        okText={actionModal?.type === 'approve' ? 'Approve' : actionModal?.type === 'return' ? 'Return' : 'Cancel Item'}
        okButtonProps={{ danger: actionModal?.type === 'cancel' }}
      >
        <Input.TextArea
          rows={3}
          value={actionComment}
          onChange={(e) => setActionComment(e.target.value)}
          placeholder={actionModal?.type === 'cancel' ? 'Cancellation reason (required)...' : 'Comment (optional)...'}
        />
      </Modal>
    </div>
  );
}
