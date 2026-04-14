import { useEffect, useState } from 'react';
import { Table, Button, Typography, message, Modal, Form, Input, InputNumber, Select, Space } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import api from '../api';
import { useAuthStore } from '../store';

export default function StockAssetsPage() {
  const [assets, setAssets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [modal, setModal] = useState(false);
  const [form] = Form.useForm();
  const [saving, setSaving] = useState(false);
  const [locations, setLocations] = useState<any[]>([]);
  const [lineItemOptions, setLineItemOptions] = useState<any[]>([]);
  const hasRole = useAuthStore((s) => s.hasRole);

  const fetchAssets = async (p = 1) => {
    setLoading(true);
    try {
      const { data } = await api.get('/stock-assets', { params: { page: p, limit: 15 } });
      setAssets(data.data);
      setTotal(data.pagination.total);
    } catch { message.error('Failed to load assets'); }
    finally { setLoading(false); }
  };

  useEffect(() => {
    fetchAssets(page);
    api.get('/admin/locations').then((r) => setLocations(r.data)).catch(() => {});
    api.get('/line-items/approved/available').then((r) => setLineItemOptions(r.data)).catch(() => {});
  }, []);

  useEffect(() => { fetchAssets(page); }, [page]);

  const handleCreate = async (values: any) => {
    setSaving(true);
    try {
      await api.post('/stock-assets', values);
      message.success('Asset created');
      setModal(false);
      form.resetFields();
      fetchAssets(1);
    } catch (err: any) {
      const errorMsg = err.response?.data?.error?.message || err.response?.data?.error || 'Failed';
      message.error(typeof errorMsg === 'string' ? errorMsg : 'Failed');
    } finally { setSaving(false); }
  };

  const columns = [
    { title: 'Description', dataIndex: 'itemDescription', ellipsis: true },
    { title: 'Type', dataIndex: 'itemType', width: 80 },
    { title: 'Qty on Hand', dataIndex: 'quantityOnHand', width: 100, render: (v: any) => Number(v) },
    { title: 'Location', dataIndex: ['location', 'locationName'], width: 130 },
    { title: 'Asset Tag', dataIndex: 'assetTag', width: 120 },
    { title: 'Line Item Ref', dataIndex: ['lineItem', 'lineItemRef'], width: 140 },
    { title: 'Updated By', dataIndex: ['updatedByUser', 'fullName'], width: 130 },
    { title: 'Last Checked', dataIndex: 'lastCheckedDate', width: 110, render: (v: any) => v ? new Date(v).toLocaleDateString() : '—' },
  ];

  return (
    <div>
      <Typography.Title level={4}>Stock & Asset Register</Typography.Title>

      <div className="table-actions">
        <span />
        {hasRole('Stores/Inventory Officer', 'System Admin') && (
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setModal(true)}>Add Record</Button>
        )}
      </div>

      <Table
        dataSource={assets}
        columns={columns}
        rowKey="id"
        loading={loading}
        pagination={{ current: page, total, pageSize: 15, onChange: setPage }}
        size="middle"
      />

      <Modal title="Add Stock/Asset" open={modal} onCancel={() => setModal(false)} footer={null}>
        <Form form={form} layout="vertical" onFinish={handleCreate}>
          <Form.Item name="item_description" label="Description" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="item_type" label="Type" rules={[{ required: true }]}>
            <Select options={[{ value: 'Stock', label: 'Stock' }, { value: 'Asset', label: 'Asset' }, { value: 'Service', label: 'Service' }]} />
          </Form.Item>
          <Form.Item name="quantity_on_hand" label="Quantity on Hand">
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="location_id" label="Location">
            <Select
              showSearch
              optionFilterProp="label"
              allowClear
              placeholder="Select location"
              options={locations.map((l: any) => ({ value: l.id, label: l.locationName }))}
            />
          </Form.Item>
          <Form.Item name="asset_tag" label="Asset Tag">
            <Input />
          </Form.Item>
          <Form.Item name="line_item_id" label="Linked Line Item">
            <Select
              showSearch
              optionFilterProp="label"
              allowClear
              placeholder="Search by ref or description"
              options={lineItemOptions.map((li: any) => ({
                value: li.id,
                label: `${li.lineItemRef} — ${li.itemDescription}`,
              }))}
            />
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={saving} block>Create</Button>
        </Form>
      </Modal>
    </div>
  );
}
