import { useState, useEffect, useCallback } from 'react';
import {
  Card, Table, Button, Tag, Space, Input, Select, Modal, Form,
  message, Tooltip, Progress, Row, Col, Typography, DatePicker, InputNumber,
} from 'antd';
import {
  PlusOutlined, SearchOutlined, EyeOutlined, EditOutlined,
  ToolOutlined, ReloadOutlined, SettingOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { machinesApi, linesApi } from '../api';
import type { Machine, ProductionLine } from '../types';
import {
  MACHINE_STATUS_MAP, MACHINE_TYPES, MACHINE_STATUSES,
  formatNumber, SHIFTS,
} from '../utils/constants';
import dayjs from 'dayjs';

const { Title, Text } = Typography;
const { Option } = Select;

export default function MachinesPage() {
  const navigate = useNavigate();
  const [machines, setMachines] = useState<Machine[]>([]);
  const [lines, setLines] = useState<ProductionLine[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [search, setSearch] = useState('');
  const [filterLine, setFilterLine] = useState<number | undefined>();
  const [filterType, setFilterType] = useState<string | undefined>();
  const [filterStatus, setFilterStatus] = useState<string | undefined>();

  // Modal states
  const [machineModalOpen, setMachineModalOpen] = useState(false);
  const [editingMachine, setEditingMachine] = useState<Machine | null>(null);
  const [machineForm] = Form.useForm();

  const fetchMachines = useCallback(async () => {
    setLoading(true);
    try {
      const res = await machinesApi.list({
        page, page_size: pageSize, search: search || undefined,
        line_id: filterLine, machine_type: filterType, status: filterStatus,
      });
      setMachines(res.items);
      setTotal(res.total);
    } catch { message.error('Lỗi tải danh sách máy'); }
    setLoading(false);
  }, [page, pageSize, search, filterLine, filterType, filterStatus]);

  const fetchLines = useCallback(async () => {
    try { setLines(await linesApi.list()); } catch {}
  }, []);

  useEffect(() => { fetchLines(); }, [fetchLines]);
  useEffect(() => { fetchMachines(); }, [fetchMachines]);

  const handleSaveMachine = async (values: any) => {
    try {
      if (values.install_date) values.install_date = values.install_date.format('YYYY-MM-DD');
      if (values.warranty_expiry) values.warranty_expiry = values.warranty_expiry.format('YYYY-MM-DD');
      if (editingMachine) {
        await machinesApi.update(editingMachine.id, values);
        message.success('Cập nhật máy thành công');
      } else {
        await machinesApi.create(values);
        message.success('Thêm máy thành công');
      }
      setMachineModalOpen(false);
      machineForm.resetFields();
      setEditingMachine(null);
      fetchMachines();
    } catch (err: any) {
      message.error(err?.response?.data?.detail || 'Lỗi lưu máy');
    }
  };

  const openEditMachine = (machine: Machine) => {
    setEditingMachine(machine);
    machineForm.setFieldsValue({
      ...machine,
      install_date: machine.install_date ? dayjs(machine.install_date) : null,
      warranty_expiry: machine.warranty_expiry ? dayjs(machine.warranty_expiry) : null,
    });
    setMachineModalOpen(true);
  };

  const columns = [
    {
      title: 'Mã máy', dataIndex: 'code', key: 'code', width: 110,
      render: (code: string) => <Text strong style={{ color: 'var(--ant-color-primary)' }}>{code}</Text>,
    },
    {
      title: 'Tên máy', dataIndex: 'name', key: 'name', ellipsis: true,
      render: (_: any, record: Machine) => (
        <div>
          <div style={{ fontWeight: 500 }}>{record.name}</div>
          {record.model && <Text type="secondary" style={{ fontSize: 12 }}>{record.manufacturer} - {record.model}</Text>}
        </div>
      ),
    },
    {
      title: 'Line', key: 'line', width: 130,
      render: (_: any, record: Machine) => record.line ? (
        <Tag color="blue">{record.line.name}</Tag>
      ) : <Text type="secondary">—</Text>,
    },
    {
      title: 'Loại', dataIndex: 'machine_type', key: 'machine_type', width: 100,
      render: (type: string) => {
        const found = MACHINE_TYPES.find(t => t.value === type);
        return found ? found.label : type;
      },
    },
    {
      title: 'Trạng thái', dataIndex: 'status', key: 'status', width: 120,
      render: (status: string) => {
        const s = MACHINE_STATUS_MAP[status] || { label: status, color: '#8c8c8c', icon: '⚪' };
        return <Tag color={s.color}>{s.icon} {s.label}</Tag>;
      },
    },
    {
      title: 'Giờ chạy', dataIndex: 'current_running_hours', key: 'hours', width: 100,
      render: (hours: number) => <Text>{formatNumber(hours)}h</Text>,
    },
    {
      title: 'Linh kiện', key: 'parts', width: 100, align: 'center' as const,
      render: (_: any, record: Machine) => (
        <Space>
          <Text>{record.parts_count}</Text>
          {record.critical_parts_count > 0 && (
            <Tooltip title={`${record.critical_parts_count} LK cần thay`}>
              <Tag color="error" style={{ margin: 0 }}>{record.critical_parts_count}⚠</Tag>
            </Tooltip>
          )}
        </Space>
      ),
    },
    {
      title: '', key: 'actions', width: 120,
      render: (_: any, record: Machine) => (
        <Space>
          <Tooltip title="Chi tiết">
            <Button type="primary" ghost size="small" icon={<EyeOutlined />}
              onClick={() => navigate(`/machines/${record.id}`)} />
          </Tooltip>
          <Tooltip title="Sửa">
            <Button size="small" icon={<EditOutlined />} onClick={() => openEditMachine(record)} />
          </Tooltip>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={3} style={{ margin: 0 }}>
          <SettingOutlined style={{ marginRight: 8 }} />Quản lý Máy
        </Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => {
          setEditingMachine(null);
          machineForm.resetFields();
          setMachineModalOpen(true);
        }}>Thêm máy</Button>
      </div>

      {/* Filters */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Row gutter={[12, 12]} align="middle">
          <Col xs={24} sm={8} md={6}>
            <Input placeholder="Tìm mã, tên máy..." prefix={<SearchOutlined />}
              value={search} onChange={e => { setSearch(e.target.value); setPage(1); }}
              allowClear />
          </Col>
          <Col xs={12} sm={6} md={4}>
            <Select placeholder="Line" value={filterLine} onChange={v => { setFilterLine(v); setPage(1); }}
              allowClear style={{ width: '100%' }}>
              {lines.map(l => <Option key={l.id} value={l.id}>{l.name}</Option>)}
            </Select>
          </Col>
          <Col xs={12} sm={5} md={4}>
            <Select placeholder="Loại máy" value={filterType} onChange={v => { setFilterType(v); setPage(1); }}
              allowClear style={{ width: '100%' }}>
              {MACHINE_TYPES.map(t => <Option key={t.value} value={t.value}>{t.label}</Option>)}
            </Select>
          </Col>
          <Col xs={12} sm={5} md={4}>
            <Select placeholder="Trạng thái" value={filterStatus} onChange={v => { setFilterStatus(v); setPage(1); }}
              allowClear style={{ width: '100%' }}>
              {MACHINE_STATUSES.map(s => <Option key={s.value} value={s.value}>{s.icon} {s.label}</Option>)}
            </Select>
          </Col>
          <Col>
            <Button icon={<ReloadOutlined />} onClick={fetchMachines}>Tải lại</Button>
          </Col>
        </Row>
      </Card>

      {/* Machine Table */}
      <Card>
        <Table
          columns={columns}
          dataSource={machines}
          rowKey="id"
          loading={loading}
          size="middle"
          pagination={{
            current: page, pageSize, total, showSizeChanger: true,
            showTotal: (t) => `Tổng ${t} máy`,
            onChange: (p, ps) => { setPage(p); setPageSize(ps); },
          }}
          onRow={(record) => ({
            onDoubleClick: () => navigate(`/machines/${record.id}`),
            style: { cursor: 'pointer' },
          })}
        />
      </Card>

      {/* Machine Create/Edit Modal */}
      <Modal
        title={editingMachine ? 'Sửa thông tin máy' : 'Thêm máy mới'}
        open={machineModalOpen}
        onCancel={() => { setMachineModalOpen(false); setEditingMachine(null); }}
        onOk={() => machineForm.submit()}
        width={700}
        okText="Lưu"
        cancelText="Hủy"
      >
        <Form form={machineForm} layout="vertical" onFinish={handleSaveMachine}>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="code" label="Mã máy" rules={[{ required: true }]}>
                <Input disabled={!!editingMachine} />
              </Form.Item>
            </Col>
            <Col span={16}>
              <Form.Item name="name" label="Tên máy" rules={[{ required: true }]}>
                <Input />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="machine_type" label="Loại máy" rules={[{ required: true }]}>
                <Select>
                  {MACHINE_TYPES.map(t => <Option key={t.value} value={t.value}>{t.label}</Option>)}
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="line_id" label="Line sản xuất">
                <Select allowClear>
                  {lines.map(l => <Option key={l.id} value={l.id}>{l.name}</Option>)}
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="status" label="Trạng thái" initialValue="idle">
                <Select>
                  {MACHINE_STATUSES.map(s => <Option key={s.value} value={s.value}>{s.icon} {s.label}</Option>)}
                </Select>
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}><Form.Item name="model" label="Model"><Input /></Form.Item></Col>
            <Col span={8}><Form.Item name="manufacturer" label="Hãng SX"><Input /></Form.Item></Col>
            <Col span={8}><Form.Item name="serial_number" label="Serial Number"><Input /></Form.Item></Col>
          </Row>
          <Row gutter={16}>
            <Col span={8}><Form.Item name="install_date" label="Ngày lắp đặt"><DatePicker style={{ width: '100%' }} /></Form.Item></Col>
            <Col span={8}><Form.Item name="warranty_expiry" label="Hết bảo hành"><DatePicker style={{ width: '100%' }} /></Form.Item></Col>
            <Col span={8}><Form.Item name="maintenance_interval_hours" label="PM mỗi (giờ)"><InputNumber style={{ width: '100%' }} min={0} /></Form.Item></Col>
          </Row>
          <Form.Item name="location" label="Vị trí"><Input /></Form.Item>
          <Form.Item name="description" label="Mô tả"><Input.TextArea rows={2} /></Form.Item>
          <Form.Item name="name_en" label="Tên tiếng Anh"><Input /></Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
