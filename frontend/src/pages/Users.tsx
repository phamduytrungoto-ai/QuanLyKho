import { useEffect, useState } from 'react';
import { Card, Table, Button, Space, Tag, Modal, Form, Input, Select, Typography, App, Switch } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, UserOutlined, SearchOutlined, ReloadOutlined } from '@ant-design/icons';
import { usersApi } from '../../api';
import { ROLES, ROLE_LABELS } from '../../utils/constants';
import type { User } from '../../types';

const { Title, Text } = Typography;

const ROLE_COLORS: Record<string, string> = {
  admin: 'red',
  director: 'purple',
  manager: 'blue',
  warehouse: 'green',
  production: 'orange',
  engineering: 'cyan',
  maintenance: 'magenta',
  purchasing: 'geekblue',
  qa: 'gold',
};

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<User | null>(null);
  const [search, setSearch] = useState('');
  const [form] = Form.useForm();
  const { message: msg } = App.useApp();

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    setLoading(true);
    try { setUsers(await usersApi.list({ search: search || undefined })); }
    catch { msg.error('Lỗi tải danh sách'); }
    finally { setLoading(false); }
  };

  const handleSubmit = async (values: any) => {
    try {
      if (editing) {
        const { password, ...updateData } = values;
        await usersApi.update(editing.id, updateData);
        msg.success('Cập nhật thành công');
      } else {
        await usersApi.create(values);
        msg.success('Thêm người dùng thành công');
      }
      setModalOpen(false); form.resetFields(); setEditing(null); loadData();
    } catch (error: any) { msg.error(error.response?.data?.detail || 'Lỗi'); }
  };

  const handleDelete = async (id: number) => {
    Modal.confirm({
      title: 'Vô hiệu hóa người dùng?',
      content: 'Người dùng sẽ không thể đăng nhập nữa',
      okText: 'Xác nhận', cancelText: 'Hủy', okType: 'danger',
      onOk: async () => { await usersApi.delete(id); msg.success('Đã vô hiệu hóa'); loadData(); },
    });
  };

  const columns = [
    { title: 'Username', dataIndex: 'username', key: 'username', width: 120,
      render: (v: string) => <Text strong>{v}</Text> },
    { title: 'Họ tên', dataIndex: 'full_name', key: 'name', width: 180 },
    { title: 'Email', dataIndex: 'email', key: 'email', width: 200 },
    { title: 'Vai trò', dataIndex: 'role', key: 'role', width: 120,
      render: (role: string) => <Tag color={ROLE_COLORS[role]}>{ROLE_LABELS[role] || role}</Tag> },
    { title: 'Bộ phận', dataIndex: 'department', key: 'dept', width: 120 },
    { title: 'Trạng thái', dataIndex: 'is_active', key: 'active', width: 100,
      render: (active: boolean) => <Tag color={active ? 'success' : 'default'}>{active ? 'Hoạt động' : 'Ngừng'}</Tag> },
    { title: 'Thao tác', key: 'actions', width: 120,
      render: (_: any, record: User) => (
        <Space>
          <Button size="small" icon={<EditOutlined />}
            onClick={() => { setEditing(record); form.setFieldsValue(record); setModalOpen(true); }} />
          <Button size="small" danger icon={<DeleteOutlined />} onClick={() => handleDelete(record.id)} />
        </Space>
      ),
    },
  ];

  return (
    <div className="page-container">
      <div className="page-header">
        <Title level={3} style={{ margin: 0 }}>👥 Quản lý Người dùng</Title>
        <Button type="primary" icon={<PlusOutlined />}
          onClick={() => { setEditing(null); form.resetFields(); setModalOpen(true); }}>
          Thêm người dùng
        </Button>
      </div>

      <div className="filter-bar">
        <Input placeholder="Tìm username, họ tên..." prefix={<SearchOutlined />} style={{ width: 260 }}
          value={search} onChange={(e) => setSearch(e.target.value)} onPressEnter={() => loadData()} allowClear />
        <Button icon={<ReloadOutlined />} onClick={() => { setSearch(''); loadData(); }}>Tải lại</Button>
      </div>

      <Card className="data-table-card">
        <Table columns={columns} dataSource={users} rowKey="id" loading={loading}
          pagination={{ pageSize: 20, showTotal: (t) => `Tổng: ${t} người dùng` }} size="middle" />
      </Card>

      <Modal title={editing ? '✏️ Sửa người dùng' : '➕ Thêm người dùng mới'}
        open={modalOpen} onCancel={() => { setModalOpen(false); setEditing(null); }}
        onOk={() => form.submit()} okText={editing ? 'Cập nhật' : 'Thêm'} cancelText="Hủy" width={500}>
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="username" label="Username" rules={[{ required: true, min: 3 }]}>
            <Input prefix={<UserOutlined />} disabled={!!editing} placeholder="Tên đăng nhập" />
          </Form.Item>
          {!editing && (
            <Form.Item name="password" label="Mật khẩu" rules={[{ required: true, min: 6 }]}>
              <Input.Password placeholder="Mật khẩu (tối thiểu 6 ký tự)" />
            </Form.Item>
          )}
          <Form.Item name="full_name" label="Họ tên" rules={[{ required: true }]}>
            <Input placeholder="Họ và tên" />
          </Form.Item>
          <Form.Item name="email" label="Email" rules={[{ required: true, type: 'email' }]}>
            <Input placeholder="email@factory.local" />
          </Form.Item>
          <Form.Item name="role" label="Vai trò" rules={[{ required: true }]}>
            <Select options={Object.entries(ROLE_LABELS).map(([val, label]) => ({ value: val, label }))} placeholder="Chọn vai trò" />
          </Form.Item>
          <Form.Item name="department" label="Bộ phận">
            <Input placeholder="Tên bộ phận" />
          </Form.Item>
          <Form.Item name="phone" label="Số điện thoại">
            <Input placeholder="Số điện thoại" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
