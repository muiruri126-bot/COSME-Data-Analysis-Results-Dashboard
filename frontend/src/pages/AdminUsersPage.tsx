import { useEffect, useState } from 'react';
import { Table, Button, Typography, message, Modal, Form, Input, Select, Switch, Tag, Space } from 'antd';
import { PlusOutlined, EditOutlined } from '@ant-design/icons';
import api from '../api';
import { useAuthStore } from '../store';

export default function AdminUsersPage() {
  const [users, setUsers] = useState<any[]>([]);
  const [roles, setRoles] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState<'create' | 'edit' | null>(null);
  const [editUser, setEditUser] = useState<any>(null);
  const [form] = Form.useForm();
  const [saving, setSaving] = useState(false);

  const fetch = async () => {
    setLoading(true);
    try {
      const [u, r] = await Promise.all([api.get('/admin/users'), api.get('/admin/roles')]);
      setUsers(u.data);
      setRoles(r.data);
    } catch { message.error('Failed to load'); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetch(); }, []);

  const openEdit = (user: any) => {
    setEditUser(user);
    form.setFieldsValue({
      email: user.email,
      full_name: user.fullName,
      is_active: user.isActive,
      role_ids: user.userRoles?.map((r: any) => r.roleId) || [],
    });
    setModal('edit');
  };

  const handleSave = async (values: any) => {
    setSaving(true);
    try {
      if (modal === 'create') {
        await api.post('/admin/users', values);
        message.success('User created');
      } else if (editUser) {
        await api.put(`/admin/users/${editUser.id}`, values);
        message.success('User updated');
      }
      setModal(null);
      setEditUser(null);
      form.resetFields();
      fetch();
    } catch (err: any) {
      message.error(err.response?.data?.error?.message || err.response?.data?.error || 'Failed');
    } finally { setSaving(false); }
  };

  const columns = [
    { title: 'Name', dataIndex: 'fullName', width: 180 },
    { title: 'Email', dataIndex: 'email', width: 220 },
    {
      title: 'Roles',
      dataIndex: 'userRoles',
      render: (r: any[]) => r?.map((role: any) => <Tag key={role.roleId} color="blue">{role.role?.roleName || role.roleId}</Tag>),
    },
    {
      title: 'Active',
      dataIndex: 'isActive',
      width: 80,
      render: (v: boolean) => <Tag color={v ? 'green' : 'red'}>{v ? 'Yes' : 'No'}</Tag>,
    },
    {
      title: 'Actions',
      width: 80,
      render: (_: any, r: any) => (
        <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(r)} />
      ),
    },
  ];

  return (
    <div>
      <Typography.Title level={4}>Users & Roles</Typography.Title>

      <div className="table-actions">
        <Typography.Text type="secondary">{users.length} users</Typography.Text>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => { setModal('create'); form.resetFields(); }}>
          Add User
        </Button>
      </div>

      <Table dataSource={users} columns={columns} rowKey="id" loading={loading} size="middle" pagination={{ pageSize: 20 }} />

      <Modal
        title={modal === 'create' ? 'Create User' : 'Edit User'}
        open={!!modal}
        onCancel={() => { setModal(null); setEditUser(null); form.resetFields(); }}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleSave}>
          <Form.Item name="email" label="Email" rules={[{ required: true, type: 'email' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="full_name" label="Full Name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          {modal === 'create' && (
            <Form.Item name="password" label="Password" rules={[{ required: true, min: 8 }]}>
              <Input.Password />
            </Form.Item>
          )}
          <Form.Item name="role_ids" label="Roles">
            <Select
              mode="multiple"
              options={roles.map((r) => ({ value: r.id, label: r.roleName }))}
            />
          </Form.Item>
          <Form.Item name="is_active" label="Active" valuePropName="checked">
            <Switch />
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={saving} block>
            {modal === 'create' ? 'Create' : 'Save'}
          </Button>
        </Form>
      </Modal>
    </div>
  );
}
