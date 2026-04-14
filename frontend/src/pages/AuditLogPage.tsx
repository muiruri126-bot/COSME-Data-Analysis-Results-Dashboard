import { useEffect, useState } from 'react';
import { Table, Typography, message, Input, Select, Space, DatePicker } from 'antd';
import api from '../api';
import { formatDate } from '../components/StatusTag';

export default function AuditLogPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState<Record<string, string>>({});

  const fetch = async (p = 1) => {
    setLoading(true);
    try {
      const { data } = await api.get('/admin/audit-log', { params: { page: p, limit: 30, ...filters } });
      setLogs(data.data);
      setTotal(data.pagination.total);
    } catch { message.error('Failed to load audit log'); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetch(page); }, [page, filters]);

  const columns = [
    { title: 'Timestamp', dataIndex: 'performedAt', width: 160, render: (v: string) => new Date(v).toLocaleString() },
    { title: 'User', dataIndex: ['performer', 'fullName'], width: 150 },
    { title: 'Action', dataIndex: 'action', width: 100 },
    { title: 'Entity', dataIndex: 'entityType', width: 120 },
    { title: 'Entity ID', dataIndex: 'entityId', width: 130, ellipsis: true },
    { title: 'Field', dataIndex: 'fieldName', width: 100 },
    { title: 'Old Value', dataIndex: 'oldValue', width: 140, ellipsis: true },
    { title: 'New Value', dataIndex: 'newValue', width: 140, ellipsis: true },
    { title: 'IP', dataIndex: 'ipAddress', width: 120 },
  ];

  return (
    <div>
      <Typography.Title level={4}>Audit Log</Typography.Title>

      <Space style={{ marginBottom: 16 }} wrap>
        <Select
          placeholder="Entity Type"
          allowClear
          style={{ width: 160 }}
          onChange={(v) => setFilters((f) => ({ ...f, entity_type: v || '' }))}
          options={[
            { value: 'line_item', label: 'Line Item' },
            { value: 'procurement_plan', label: 'Plan' },
            { value: 'purchase_requisition', label: 'PR' },
            { value: 'delivery', label: 'Delivery' },
            { value: 'user', label: 'User' },
          ]}
        />
        <Select
          placeholder="Action"
          allowClear
          style={{ width: 140 }}
          onChange={(v) => setFilters((f) => ({ ...f, action: v || '' }))}
          options={[
            { value: 'CREATE' },
            { value: 'UPDATE' },
            { value: 'DELETE' },
            { value: 'STATUS_CHANGE' },
            { value: 'APPROVAL' },
            { value: 'IMPORT' },
          ]}
        />
        <Input.Search
          placeholder="Entity ID..."
          allowClear
          style={{ width: 250 }}
          onSearch={(v) => setFilters((f) => ({ ...f, entity_id: v }))}
        />
      </Space>

      <Table
        dataSource={logs}
        columns={columns}
        rowKey="id"
        loading={loading}
        size="small"
        scroll={{ x: 1300 }}
        pagination={{
          current: page,
          total,
          pageSize: 30,
          onChange: setPage,
          showTotal: (t) => `${t} entries`,
        }}
      />
    </div>
  );
}
