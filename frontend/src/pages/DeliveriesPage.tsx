import { useEffect, useState } from 'react';
import { Table, Button, Typography, message, Modal, Form, InputNumber, Tag, Card, Statistic, Row, Col, DatePicker, Input } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import api from '../api';
import { formatDate } from '../components/StatusTag';
import { useAuthStore } from '../store';

export default function DeliveriesPage() {
  const [overdue, setOverdue] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [deliveryItem, setDeliveryItem] = useState<any>(null);
  const [form] = Form.useForm();
  const [creating, setCreating] = useState(false);
  const hasRole = useAuthStore((s) => s.hasRole);

  useEffect(() => {
    api.get('/reports/overdue-deliveries').then((r) => { setOverdue(r.data); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const openDelivery = (record: any) => {
    setDeliveryItem(record);
    form.resetFields();
  };

  const handleRecordDelivery = async (values: any) => {
    if (!deliveryItem) return;
    setCreating(true);
    try {
      await api.post(`/deliveries/line-item/${deliveryItem.id}`, {
        delivery_date: values.delivery_date.format('YYYY-MM-DD'),
        quantity_delivered: values.quantity_delivered,
        delivery_note_ref: values.delivery_note_ref,
        condition_notes: values.condition_notes,
      });
      message.success('Delivery recorded');
      setDeliveryItem(null);
      form.resetFields();
      // Refresh list
      const { data } = await api.get('/reports/overdue-deliveries');
      setOverdue(data);
    } catch (err: any) {
      const errorMsg = err.response?.data?.error?.message || err.response?.data?.error || 'Failed to record delivery';
      message.error(typeof errorMsg === 'string' ? errorMsg : 'Failed to record delivery');
    } finally { setCreating(false); }
  };

  const columns = [
    { title: 'Ref', dataIndex: 'line_item_ref', width: 140 },
    { title: 'Description', dataIndex: 'item_description', ellipsis: true },
    { title: 'Est. Delivery', dataIndex: 'estimated_delivery_date', width: 120, render: formatDate },
    {
      title: 'Days Overdue',
      dataIndex: 'days_overdue',
      width: 110,
      sorter: (a: any, b: any) => a.days_overdue - b.days_overdue,
      render: (v: number) => <Tag color={v > 14 ? 'red' : v > 7 ? 'orange' : 'gold'}>{v} days</Tag>,
    },
    { title: 'Qty', dataIndex: 'quantity', width: 60 },
    { title: 'Delivered', dataIndex: 'delivered_quantity', width: 80 },
    { title: '%', dataIndex: 'delivery_pct', width: 60, render: (v: number) => `${v}%` },
    { title: 'Cost', dataIndex: 'estimated_total_cost', width: 120, render: (v: number, r: any) => `${r.currency} ${v.toLocaleString()}` },
    { title: 'Location', dataIndex: 'location', width: 120 },
    { title: 'Plan', dataIndex: 'tracking_no', width: 120 },
    {
      title: 'Actions',
      width: 120,
      render: (_: any, r: any) =>
        hasRole('Supply Chain Officer', 'Stores/Inventory Officer', 'System Admin') ? (
          <Button size="small" icon={<PlusOutlined />} onClick={() => openDelivery(r)}>
            Record
          </Button>
        ) : null,
    },
  ];

  return (
    <div>
      <Typography.Title level={4}>Deliveries & Receipts</Typography.Title>

      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={12} sm={6}>
          <Card size="small"><Statistic title="Total Overdue" value={overdue.length} valueStyle={{ color: '#ff4d4f' }} /></Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card size="small"><Statistic title="> 14 days" value={overdue.filter((o) => o.days_overdue > 14).length} valueStyle={{ color: '#ff4d4f' }} /></Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card size="small"><Statistic title="7-14 days" value={overdue.filter((o) => o.days_overdue > 7 && o.days_overdue <= 14).length} valueStyle={{ color: '#fa8c16' }} /></Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card size="small"><Statistic title="< 7 days" value={overdue.filter((o) => o.days_overdue <= 7).length} valueStyle={{ color: '#faad14' }} /></Card>
        </Col>
      </Row>

      <Table
        dataSource={overdue}
        columns={columns}
        rowKey="id"
        loading={loading}
        size="middle"
        scroll={{ x: 1200 }}
        pagination={{ pageSize: 15 }}
      />

      <Modal
        title={`Record Delivery — ${deliveryItem?.line_item_ref || ''}`}
        open={!!deliveryItem}
        onCancel={() => { setDeliveryItem(null); form.resetFields(); }}
        footer={null}
      >
        {deliveryItem && (
          <div style={{ marginBottom: 12, padding: 8, background: '#f5f5f5', borderRadius: 6 }}>
            <Typography.Text strong>{deliveryItem.item_description}</Typography.Text>
            <br />
            <Typography.Text type="secondary">
              Qty: {deliveryItem.quantity} | Delivered so far: {deliveryItem.delivered_quantity} | Remaining: {deliveryItem.quantity - deliveryItem.delivered_quantity}
            </Typography.Text>
          </div>
        )}
        <Form form={form} layout="vertical" onFinish={handleRecordDelivery}>
          <Form.Item name="delivery_date" label="Delivery Date" rules={[{ required: true, message: 'Select delivery date' }]}>
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="quantity_delivered" label="Quantity Delivered" rules={[{ required: true, message: 'Enter quantity' }]}>
            <InputNumber min={0.01} max={deliveryItem ? deliveryItem.quantity - deliveryItem.delivered_quantity : undefined} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="delivery_note_ref" label="Delivery Note Ref">
            <Input />
          </Form.Item>
          <Form.Item name="condition_notes" label="Condition Notes">
            <Input.TextArea rows={2} />
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={creating} block>Record</Button>
        </Form>
      </Modal>
    </div>
  );
}
