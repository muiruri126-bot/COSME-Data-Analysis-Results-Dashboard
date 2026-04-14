import { useEffect, useState } from 'react';
import { Card, Row, Col, Typography, Table, Spin, Tag, Select, Space, Statistic } from 'antd';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, PieChart, Pie, Cell } from 'recharts';
import api from '../api';
import { formatCurrency, formatDate } from '../components/StatusTag';

const COLORS = ['#1890ff', '#52c41a', '#fa8c16', '#ff4d4f', '#722ed1', '#13c2c2', '#faad14', '#389e0d', '#595959', '#eb2f96'];

export default function ReportsPage() {
  const [pipeline, setPipeline] = useState<any>(null);
  const [stockAvoided, setStockAvoided] = useState<any>(null);
  const [ageing, setAgeing] = useState<any[]>([]);
  const [overdue, setOverdue] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get('/reports/pipeline'),
      api.get('/reports/stock-avoided'),
      api.get('/reports/approval-ageing'),
      api.get('/reports/overdue-deliveries'),
    ]).then(([p, s, a, o]) => {
      setPipeline(p.data);
      setStockAvoided(s.data);
      setAgeing(a.data);
      setOverdue(o.data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

  const pipelineData = pipeline ? Object.entries(pipeline).map(([name, val]: any) => ({
    name,
    count: val.count,
    value_kes: Math.round(val.value_kes),
    value_eur: Math.round(val.value_eur),
  })) : [];

  return (
    <div>
      <Typography.Title level={4}>Reports & Analytics</Typography.Title>

      {/* Pipeline */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={12}>
          <Card title="Procurement Pipeline (Count by Status)">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={pipelineData}>
                <XAxis dataKey="name" tick={{ fontSize: 9 }} angle={-15} textAnchor="end" height={60} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#1890ff" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Pipeline Value (KES + EUR)">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={pipelineData}>
                <XAxis dataKey="name" tick={{ fontSize: 9 }} angle={-15} textAnchor="end" height={60} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="value_kes" fill="#1890ff" name="KES" stackId="a" />
                <Bar dataKey="value_eur" fill="#52c41a" name="EUR" stackId="a" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Stock Avoided */}
      {stockAvoided && (
        <Card title="Stock Avoidance Report" style={{ marginBottom: 24 }}>
          <Row gutter={16}>
            <Col span={6}><Statistic title="Items Avoided" value={stockAvoided.count} /></Col>
            <Col span={9}><Statistic title="Value Avoided (KES)" value={stockAvoided.total_value_kes} prefix="KES " /></Col>
            <Col span={9}><Statistic title="Value Avoided (EUR)" value={stockAvoided.total_value_eur} prefix="EUR " /></Col>
          </Row>
          {stockAvoided.items?.length > 0 && (
            <Table
              dataSource={stockAvoided.items}
              rowKey="line_item_ref"
              size="small"
              pagination={false}
              style={{ marginTop: 16 }}
              columns={[
                { title: 'Ref', dataIndex: 'line_item_ref', width: 140 },
                { title: 'Description', dataIndex: 'item_description', ellipsis: true },
                { title: 'Qty Planned', dataIndex: 'quantity', width: 90 },
                { title: 'Stock Available', dataIndex: 'quantity_available', width: 110 },
                { title: 'Est. Cost', dataIndex: 'estimated_total_cost', width: 120, render: (v: number, r: any) => `${r.currency} ${v.toLocaleString()}` },
                { title: 'Location', dataIndex: 'location', width: 120 },
              ]}
            />
          )}
        </Card>
      )}

      {/* Approval Ageing */}
      <Card title="Approval Ageing Detail" style={{ marginBottom: 24 }}>
        <Table
          dataSource={ageing}
          rowKey="line_item_ref"
          size="small"
          scroll={{ x: 1100 }}
          pagination={{ pageSize: 10 }}
          columns={[
            { title: 'Ref', dataIndex: 'line_item_ref', width: 140 },
            { title: 'Description', dataIndex: 'item_description', ellipsis: true },
            { title: 'Status', dataIndex: 'status', width: 160 },
            { title: 'Days', dataIndex: 'days_in_status', width: 60, sorter: (a: any, b: any) => a.days_in_status - b.days_in_status, render: (v: number) => <Tag color={v > 5 ? 'red' : 'green'}>{v}</Tag> },
            { title: 'Cost', dataIndex: 'estimated_total_cost', width: 120, render: (v: number, r: any) => `${r.currency_code} ${v.toLocaleString()}` },
            { title: 'Plan', dataIndex: 'tracking_no', width: 120 },
            { title: 'Project', dataIndex: 'project_name', ellipsis: true },
            { title: 'Approver', dataIndex: 'approver', width: 130 },
          ]}
        />
      </Card>

      {/* Overdue Deliveries */}
      <Card title="Overdue Deliveries">
        <Table
          dataSource={overdue}
          rowKey="line_item_ref"
          size="small"
          scroll={{ x: 1100 }}
          pagination={{ pageSize: 10 }}
          columns={[
            { title: 'Ref', dataIndex: 'line_item_ref', width: 140 },
            { title: 'Description', dataIndex: 'item_description', ellipsis: true },
            { title: 'Est. Delivery', dataIndex: 'estimated_delivery_date', width: 110, render: formatDate },
            { title: 'Overdue', dataIndex: 'days_overdue', width: 80, render: (v: number) => <Tag color="red">{v}d</Tag> },
            { title: 'Qty', dataIndex: 'quantity', width: 60 },
            { title: 'Delivered', dataIndex: 'delivered_quantity', width: 80 },
            { title: '%', dataIndex: 'delivery_pct', width: 50, render: (v: number) => `${v}%` },
            { title: 'Plan', dataIndex: 'tracking_no', width: 120 },
            { title: 'Location', dataIndex: 'location', width: 120 },
          ]}
        />
      </Card>
    </div>
  );
}
