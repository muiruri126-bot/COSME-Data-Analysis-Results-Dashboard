import { useEffect, useState } from 'react';
import { Table, Button, Typography, message, Modal, Form, Input, Select, Space, DatePicker } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import api from '../api';
import { formatDate, formatCurrency } from '../components/StatusTag';
import { useAuthStore } from '../store';

export default function PurchaseRequisitionsPage() {
  const [prs, setPrs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [createOpen, setCreateOpen] = useState(false);
  const [form] = Form.useForm();
  const [creating, setCreating] = useState(false);
  const [approvedItems, setApprovedItems] = useState<any[]>([]);
  const [itemsLoading, setItemsLoading] = useState(false);
  const hasRole = useAuthStore((s) => s.hasRole);

  const fetchPRs = async (p = 1) => {
    setLoading(true);
    try {
      const { data } = await api.get('/purchase-requisitions', { params: { page: p, limit: 15 } });
      setPrs(data.data);
      setTotal(data.pagination.total);
    } catch { message.error('Failed to load PRs'); }
    finally { setLoading(false); }
  };

  const fetchApprovedItems = async () => {
    setItemsLoading(true);
    try {
      const { data } = await api.get('/line-items/approved/available');
      setApprovedItems(data);
    } catch { message.error('Failed to load approved line items'); }
    finally { setItemsLoading(false); }
  };

  useEffect(() => { fetchPRs(page); }, [page]);

  const handleOpenCreate = () => {
    setCreateOpen(true);
    fetchApprovedItems();
  };

  const handleCreate = async (values: any) => {
    setCreating(true);
    try {
      await api.post('/purchase-requisitions', {
        pr_number: values.pr_number,
        submitted_date: values.submitted_date?.format?.('YYYY-MM-DD') || values.submitted_date,
        line_item_ids: values.line_item_ids,
        notes: values.notes,
      });
      message.success('Purchase Requisition created successfully');
      setCreateOpen(false);
      form.resetFields();
      fetchPRs(1);
    } catch (err: any) {
      const errorMsg = err.response?.data?.error?.message || err.response?.data?.error || 'Failed to create PR';
      message.error(typeof errorMsg === 'string' ? errorMsg : 'Failed to create PR');
    } finally { setCreating(false); }
  };

  const columns = [
    { title: 'PR Number', dataIndex: 'prNumber', width: 130 },
    { title: 'Status', dataIndex: 'status', width: 80 },
    { title: 'Submitted By', dataIndex: ['submitter', 'fullName'], width: 150 },
    { title: 'Date', dataIndex: 'submittedDate', width: 110, render: formatDate },
    {
      title: 'Linked Items',
      dataIndex: 'prLineItems',
      render: (items: any[]) => items?.length || 0,
      width: 100,
    },
    {
      title: 'Total Value',
      dataIndex: 'prLineItems',
      width: 130,
      render: (items: any[]) => {
        const total = items?.reduce((s, i) => s + Number(i.lineItem?.estimatedTotalCost || 0), 0) || 0;
        return formatCurrency(total);
      },
    },
    { title: 'Notes', dataIndex: 'notes', ellipsis: true },
    { title: 'Created', dataIndex: 'createdAt', width: 110, render: formatDate },
  ];

  return (
    <div>
      <Typography.Title level={4}>Purchase Requisitions</Typography.Title>

      <div className="table-actions">
        <span />
        {hasRole('Supply Chain Officer', 'System Admin') && (
          <Button type="primary" icon={<PlusOutlined />} onClick={handleOpenCreate}>
            Raise PR
          </Button>
        )}
      </div>

      <Table
        dataSource={prs}
        columns={columns}
        rowKey="id"
        loading={loading}
        pagination={{ current: page, total, pageSize: 15, onChange: setPage }}
        size="middle"
        scroll={{ x: 900 }}
      />

      <Modal title="Raise Purchase Requisition" open={createOpen} onCancel={() => setCreateOpen(false)} footer={null} width={640}>
        <Form form={form} layout="vertical" onFinish={handleCreate}>
          <Form.Item name="pr_number" label="PR Number" rules={[{ required: true, message: 'Please enter a PR number' }]}>
            <Input placeholder="PR-2025-001" />
          </Form.Item>
          <Form.Item name="submitted_date" label="Submitted Date" rules={[{ required: true, message: 'Please select a date' }]}>
            <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
          </Form.Item>
          <Form.Item name="line_item_ids" label="Approved Line Items" rules={[{ required: true, message: 'Please select at least one approved line item' }]}>
            <Select
              mode="multiple"
              placeholder="Search and select approved line items"
              loading={itemsLoading}
              showSearch
              optionFilterProp="label"
              options={approvedItems.map((item: any) => ({
                value: item.id,
                label: `${item.lineItemRef} — ${item.itemDescription} (${item.currencyCode} ${Number(item.estimatedTotalCost || 0).toLocaleString()})`,
              }))}
              notFoundContent={itemsLoading ? 'Loading...' : 'No approved line items available'}
            />
          </Form.Item>
          <Form.Item name="notes" label="Notes">
            <Input.TextArea rows={2} />
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={creating} block>Create PR</Button>
        </Form>
      </Modal>
    </div>
  );
}
