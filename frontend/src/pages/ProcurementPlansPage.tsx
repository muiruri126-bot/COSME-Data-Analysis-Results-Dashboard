import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Table, Button, Input, Select, Space, Typography, message, Card } from 'antd';
import { PlusOutlined, FileTextOutlined } from '@ant-design/icons';
import api from '../api';
import { StatusTag, formatCurrency, formatDate } from '../components/StatusTag';
import { useAuthStore } from '../store';

export default function ProcurementPlansPage() {
  const [plans, setPlans] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string | undefined>();
  const navigate = useNavigate();
  const hasRole = useAuthStore((s) => s.hasRole);

  const fetchPlans = async (p = 1) => {
    setLoading(true);
    try {
      const params: Record<string, string> = { page: String(p), limit: '15' };
      if (search) params.search = search;
      if (statusFilter) params.status = statusFilter;
      const { data } = await api.get('/procurement-plans', { params });
      setPlans(data.data);
      setTotal(data.pagination.total);
    } catch {
      message.error('Failed to load plans');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchPlans(page); }, [page, statusFilter]);

  const columns = [
    {
      title: 'Tracking No',
      dataIndex: 'trackingNo',
      width: 120,
      render: (v: string, r: any) => (
        <a onClick={() => navigate(`/plans/${r.id}`)} style={{ fontWeight: 600 }}>{v}</a>
      ),
    },
    { title: 'Plan Type', dataIndex: 'typeOfProcurementPlan', width: 100 },
    { title: 'FY', dataIndex: 'financialYear', width: 60 },
    {
      title: 'Project',
      dataIndex: ['project', 'projectName'],
      width: 180,
      ellipsis: true,
    },
    { title: 'Manager', dataIndex: ['departmentManager', 'fullName'], width: 140, ellipsis: true },
    { title: 'Hub', dataIndex: 'globalRegionalHub', width: 160, ellipsis: true },
    { title: 'Country', dataIndex: 'countryOffice', width: 80 },
    { title: 'Currency', dataIndex: 'currency', width: 70 },
    { title: 'Donor', dataIndex: 'donorName', width: 80 },
    { title: 'Items', dataIndex: ['_count', 'lineItems'], width: 60 },
    {
      title: 'Status',
      dataIndex: 'headerStatus',
      width: 100,
      render: (s: string) => <StatusTag status={s} />,
    },
    {
      title: 'Created',
      dataIndex: 'createdAt',
      width: 100,
      render: formatDate,
    },
  ];

  return (
    <div>
      <div className="page-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <FileTextOutlined style={{ fontSize: 22, color: '#003b7c' }} />
          <Typography.Title level={4} style={{ margin: 0 }}>
            Procurement Plans
          </Typography.Title>
          <Typography.Text type="secondary" style={{ fontSize: 13, marginLeft: 4 }}>
            ({total} total)
          </Typography.Text>
        </div>
        {hasRole('Requester', 'System Admin') && (
          <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/plans/new')} size="middle">
            New Plan
          </Button>
        )}
      </div>

      <Card bordered={false} style={{ borderRadius: 12 }}>
        <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8 }}>
          <Space>
            <Input.Search
              placeholder="Search tracking no..."
              onSearch={(v) => { setSearch(v); setPage(1); fetchPlans(1); }}
              style={{ width: 260 }}
              allowClear
            />
            <Select
              placeholder="Filter by status"
              allowClear
              style={{ width: 160 }}
              onChange={(v) => { setStatusFilter(v); setPage(1); }}
              options={[
                { value: 'Draft', label: 'Draft' },
                { value: 'Active', label: 'Active' },
                { value: 'Closed', label: 'Closed' },
              ]}
            />
          </Space>
        </div>

        <Table
          dataSource={plans}
          columns={columns}
          rowKey="id"
          loading={loading}
          pagination={{
            current: page,
            total,
            pageSize: 15,
            onChange: setPage,
            showTotal: (t) => `${t} plans`,
            showSizeChanger: false,
          }}
          size="middle"
          scroll={{ x: 1100 }}
          onRow={(record) => ({
            style: { cursor: 'pointer' },
            onClick: () => navigate(`/plans/${record.id}`),
          })}
        />
      </Card>
    </div>
  );
}
