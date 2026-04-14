import { useEffect, useState } from 'react';
import { Row, Col, Card, Statistic, Spin, Typography, Table, Tag, Progress, Empty } from 'antd';
import {
  FileTextOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  WarningOutlined,
  DollarOutlined,
  RiseOutlined,
} from '@ant-design/icons';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import api from '../api';
import { formatCurrency, formatDate } from '../components/StatusTag';
import { useAuthStore } from '../store';

const COLORS = ['#003b7c', '#2e7d32', '#ed6c02', '#d32f2f', '#7b1fa2', '#00838f', '#f9a825', '#388e3c', '#616161', '#c2185b'];

export default function DashboardPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const user = useAuthStore((s) => s.user);

  useEffect(() => {
    api.get('/reports/dashboard').then((r) => { setData(r.data); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;
  if (!data) return <Empty description="Unable to load dashboard data" style={{ marginTop: 100 }} />;

  const { summary, approval_ageing, overdue_deliveries, top_10_cost_items } = data;
  const statusData = Object.entries(summary.line_items_by_status || {}).map(([name, val]: any) => ({
    name,
    count: val.count,
    value: val.value_kes + val.value_eur,
  }));

  const totalItems = statusData.reduce((s, d) => s + d.count, 0);
  const approvedCount = (summary.line_items_by_status?.['Approved']?.count || 0) +
    (summary.line_items_by_status?.['PR Raised']?.count || 0) +
    (summary.line_items_by_status?.['Ordered/Contracted']?.count || 0) +
    (summary.line_items_by_status?.['Delivered/Closed']?.count || 0);
  const pendingCount = summary.line_items_by_status?.['Submitted for Approval']?.count || 0;
  const progressPct = totalItems > 0 ? Math.round((approvedCount / totalItems) * 100) : 0;

  return (
    <div>
      {/* Welcome Header */}
      <div style={{ marginBottom: 24 }}>
        <Typography.Title level={4} style={{ margin: 0, color: '#1a1a2e' }}>
          Welcome back, {user?.fullName?.split(' ')[0]}
        </Typography.Title>
        <Typography.Text type="secondary" style={{ fontSize: 13 }}>
          Here&apos;s an overview of your procurement activities
        </Typography.Text>
      </div>

      {/* KPI Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card className="kpi-card kpi-card-total" bordered={false}>
            <Statistic
              title={<span style={{ color: '#003b7c', fontWeight: 500 }}>Total Line Items</span>}
              value={totalItems}
              prefix={<FileTextOutlined style={{ color: '#003b7c' }} />}
              valueStyle={{ color: '#003b7c' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card className="kpi-card kpi-card-approved" bordered={false}>
            <Statistic
              title={<span style={{ color: '#2e7d32', fontWeight: 500 }}>Approved / Progressing</span>}
              value={approvedCount}
              prefix={<CheckCircleOutlined style={{ color: '#2e7d32' }} />}
              valueStyle={{ color: '#2e7d32' }}
              suffix={<span style={{ fontSize: 14, color: '#666' }}>/ {totalItems}</span>}
            />
            <Progress percent={progressPct} showInfo={false} strokeColor="#2e7d32" size="small" style={{ marginTop: 8 }} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card className="kpi-card kpi-card-pending" bordered={false}>
            <Statistic
              title={<span style={{ color: '#e65100', fontWeight: 500 }}>Pending Approval</span>}
              value={pendingCount}
              prefix={<ClockCircleOutlined style={{ color: '#e65100' }} />}
              valueStyle={{ color: '#e65100' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card className="kpi-card kpi-card-overdue" bordered={false}>
            <Statistic
              title={<span style={{ color: '#c62828', fontWeight: 500 }}>Overdue Deliveries</span>}
              value={overdue_deliveries?.length || 0}
              prefix={<WarningOutlined style={{ color: '#c62828' }} />}
              valueStyle={{ color: '#c62828' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Budget */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12}>
          <Card className="kpi-card kpi-card-kes" bordered={false}>
            <Statistic
              title={<span style={{ color: '#6a1b9a', fontWeight: 500 }}>Total Planned (KES)</span>}
              value={summary.total_planned_cost_kes}
              prefix={<DollarOutlined style={{ color: '#6a1b9a' }} />}
              formatter={(v) => formatCurrency(Number(v), 'KES')}
              valueStyle={{ color: '#6a1b9a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12}>
          <Card className="kpi-card kpi-card-eur" bordered={false}>
            <Statistic
              title={<span style={{ color: '#00695c', fontWeight: 500 }}>Total Planned (EUR)</span>}
              value={summary.total_planned_cost_eur}
              prefix={<RiseOutlined style={{ color: '#00695c' }} />}
              formatter={(v) => formatCurrency(Number(v), 'EUR')}
              valueStyle={{ color: '#00695c' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Charts */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={12}>
          <Card title="Items by Status" className="dashboard-card">
            {statusData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie data={statusData} dataKey="count" nameKey="name" cx="50%" cy="50%" outerRadius={100} innerRadius={50} paddingAngle={2}
                    label={(e) => `${e.name}: ${e.count}`}>
                    {statusData.map((_: any, i: number) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Pie>
                  <Tooltip formatter={(v: number, name: string) => [v, name]} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <Empty description="No items yet" style={{ padding: 40 }} />
            )}
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Value by Status (Combined)" className="dashboard-card">
            {statusData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={statusData} barCategoryGap="20%">
                  <XAxis dataKey="name" tick={{ fontSize: 10 }} angle={-20} textAnchor="end" height={60} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip formatter={(v: number) => v.toLocaleString()} />
                  <Legend />
                  <Bar dataKey="value" fill="#003b7c" name="Total Value" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <Empty description="No data" style={{ padding: 40 }} />
            )}
          </Card>
        </Col>
      </Row>

      {/* Approval Ageing & Top Costs */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={12}>
          <Card title="Approval Ageing (> 5 days)" className="dashboard-card">
            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col span={12}><Statistic title="Avg Days in Submitted" value={approval_ageing.avg_days_in_submitted} suffix="days" valueStyle={{ fontSize: 22, color: '#003b7c' }} /></Col>
              <Col span={12}><Statistic title="Avg Days in Returned" value={approval_ageing.avg_days_in_returned} suffix="days" valueStyle={{ fontSize: 22, color: '#ed6c02' }} /></Col>
            </Row>
            <Table
              dataSource={approval_ageing.items_pending_over_5_days || []}
              rowKey="ref"
              size="small"
              pagination={false}
              scroll={{ y: 200 }}
              locale={{ emptyText: <Empty description="No overdue approvals" image={Empty.PRESENTED_IMAGE_SIMPLE} /> }}
              columns={[
                { title: 'Ref', dataIndex: 'ref', width: 140 },
                { title: 'Status', dataIndex: 'status', width: 160, render: (s: string) => <Tag color={s.includes('Submitted') ? 'blue' : 'orange'}>{s}</Tag> },
                { title: 'Days', dataIndex: 'days_pending', width: 60, render: (d: number) => <span style={{ fontWeight: 600, color: d > 10 ? '#d32f2f' : '#ed6c02' }}>{d}</span> },
                { title: 'Approver', dataIndex: 'approver' },
              ]}
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Top 10 Cost Items" className="dashboard-card">
            <Table
              dataSource={top_10_cost_items || []}
              rowKey="ref"
              size="small"
              pagination={false}
              scroll={{ y: 280 }}
              locale={{ emptyText: <Empty description="No items" image={Empty.PRESENTED_IMAGE_SIMPLE} /> }}
              columns={[
                { title: 'Ref', dataIndex: 'ref', width: 140 },
                { title: 'Description', dataIndex: 'description', ellipsis: true },
                { title: 'Est. Cost', dataIndex: 'estimated_total_cost', width: 130, render: (v: number, r: any) => <span style={{ fontWeight: 600 }}>{formatCurrency(v, r.currency)}</span> },
              ]}
            />
          </Card>
        </Col>
      </Row>

      {/* Overdue Deliveries */}
      {overdue_deliveries && overdue_deliveries.length > 0 && (
        <Card title="Overdue Deliveries" className="dashboard-card" style={{ marginBottom: 24 }}>
          <Table
            dataSource={overdue_deliveries}
            rowKey="ref"
            size="small"
            pagination={{ pageSize: 5 }}
            columns={[
              { title: 'Ref', dataIndex: 'ref', width: 140 },
              { title: 'Description', dataIndex: 'item_description', ellipsis: true },
              { title: 'Est. Delivery', dataIndex: 'estimated_delivery_date', width: 120, render: formatDate },
              { title: 'Days Overdue', dataIndex: 'days_overdue', width: 100, render: (v: number) => <Tag color={v > 14 ? 'red' : v > 7 ? 'orange' : 'gold'}>{v} days</Tag> },
              { title: 'Delivered %', dataIndex: 'delivered_pct', width: 110, render: (v: number) => <Progress percent={v} size="small" status={v >= 100 ? 'success' : 'active'} /> },
              { title: 'Location', dataIndex: 'location' },
            ]}
          />
        </Card>
      )}
    </div>
  );
}
