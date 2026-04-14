import { useEffect, useState } from 'react';
import { Table, Button, Typography, message, Modal, Form, Input, InputNumber, Card, Row, Col, Statistic } from 'antd';
import { PlusOutlined, SwapOutlined } from '@ant-design/icons';
import api from '../api';
import { useAuthStore } from '../store';

export default function ExchangeRatesPage() {
  const [rates, setRates] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [convertOpen, setConvertOpen] = useState(false);
  const [convertResult, setConvertResult] = useState<any>(null);
  const [form] = Form.useForm();
  const [convertForm] = Form.useForm();
  const hasRole = useAuthStore((s) => s.hasRole);

  useEffect(() => {
    api.get('/exchange-rates').then((r) => { setRates(r.data); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const handleCreate = async (values: any) => {
    try {
      await api.post('/exchange-rates', values);
      message.success('Exchange rate added');
      setCreateOpen(false);
      form.resetFields();
      const { data } = await api.get('/exchange-rates');
      setRates(data);
    } catch (err: any) { message.error(err.response?.data?.error?.message || err.response?.data?.error || 'Failed'); }
  };

  const handleConvert = async (values: any) => {
    try {
      const { data } = await api.get('/exchange-rates/convert', { params: values });
      setConvertResult(data);
    } catch (err: any) { message.error(err.response?.data?.error?.message || err.response?.data?.error || 'Conversion failed'); }
  };

  const columns = [
    { title: 'From', dataIndex: 'fromCurrency', width: 80 },
    { title: 'To', dataIndex: 'toCurrency', width: 80 },
    { title: 'Rate', dataIndex: 'rate', width: 120, render: (v: any) => Number(v).toFixed(6) },
    { title: 'Effective Date', dataIndex: 'effectiveDate', width: 120, render: (v: string) => new Date(v).toLocaleDateString() },
    { title: 'Added By', dataIndex: ['creator', 'fullName'], width: 150 },
  ];

  return (
    <div>
      <Typography.Title level={4}>Exchange Rates</Typography.Title>

      <div className="table-actions">
        <Button icon={<SwapOutlined />} onClick={() => setConvertOpen(true)}>
          Currency Converter
        </Button>
        {hasRole('System Admin', 'Finance/Grants') && (
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setCreateOpen(true)}>
            Add Rate
          </Button>
        )}
      </div>

      <Table
        dataSource={rates}
        columns={columns}
        rowKey="id"
        loading={loading}
        size="middle"
        pagination={{ pageSize: 20 }}
      />

      <Modal title="Add Exchange Rate" open={createOpen} onCancel={() => setCreateOpen(false)} footer={null}>
        <Form form={form} layout="vertical" onFinish={handleCreate}>
          <Form.Item name="from_currency" label="From Currency" rules={[{ required: true }]}>
            <Input placeholder="KES" />
          </Form.Item>
          <Form.Item name="to_currency" label="To Currency" rules={[{ required: true }]}>
            <Input placeholder="EUR" />
          </Form.Item>
          <Form.Item name="rate" label="Rate" rules={[{ required: true }]}>
            <InputNumber min={0.000001} step={0.0001} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="effective_date" label="Effective Date" rules={[{ required: true }]}>
            <Input type="date" />
          </Form.Item>
          <Button type="primary" htmlType="submit" block>Add</Button>
        </Form>
      </Modal>

      <Modal title="Currency Converter" open={convertOpen} onCancel={() => { setConvertOpen(false); setConvertResult(null); }} footer={null}>
        <Form form={convertForm} layout="vertical" onFinish={handleConvert}>
          <Row gutter={8}>
            <Col span={8}><Form.Item name="from" rules={[{ required: true }]}><Input placeholder="KES" /></Form.Item></Col>
            <Col span={8}><Form.Item name="to" rules={[{ required: true }]}><Input placeholder="EUR" /></Form.Item></Col>
            <Col span={8}><Form.Item name="amount" rules={[{ required: true }]}><InputNumber style={{ width: '100%' }} placeholder="Amount" /></Form.Item></Col>
          </Row>
          <Button type="primary" htmlType="submit" block>Convert</Button>
        </Form>
        {convertResult && (
          <Card size="small" style={{ marginTop: 16 }}>
            <Statistic title={`${convertResult.original_amount} ${convertResult.from_currency}`}
              value={convertResult.converted_amount}
              suffix={convertResult.to_currency}
              precision={2} />
            <Typography.Text type="secondary">Rate: {convertResult.rate_used} (Effective: {new Date(convertResult.effective_date).toLocaleDateString()})</Typography.Text>
          </Card>
        )}
      </Modal>
    </div>
  );
}
