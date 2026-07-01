import { useEffect, useState } from 'react';
import {
  Card, Table, Button, Space, Input, Select, Tag, Modal, Form, Drawer,
  Descriptions, Typography, App, Row, Col, InputNumber, Tooltip,
} from 'antd';
import {
  PlusOutlined, SearchOutlined, EditOutlined, DeleteOutlined,
  EyeOutlined, ReloadOutlined, FilterOutlined,
} from '@ant-design/icons';
import { materialsApi } from '../api';
import { MATERIAL_TYPES, STATUS_COLORS, STATUS_LABELS, formatCurrency } from '../utils/constants';
import type { Material, MaterialCategory, Unit, Supplier, PaginatedResponse } from '../types';

const { Title, Text } = Typography;

export default function MaterialsPage() {
  const [data, setData] = useState<PaginatedResponse<Material>>({ items: [], total: 0, page: 1, page_size: 20 });
  const [categories, setCategories] = useState<MaterialCategory[]>([]);
  const [units, setUnits] = useState<Unit[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [detailOpen, setDetailOpen] = useState(false);
  const [editing, setEditing] = useState<Material | null>(null);
  const [selected, setSelected] = useState<Material | null>(null);
  const [filters, setFilters] = useState({ search: '', material_type: '', category_id: undefined as number | undefined });
  const [form] = Form.useForm();
  const { message: msg } = App.useApp();

  useEffect(() => {
    loadData();
    loadLookups();
  }, []);

  const loadLookups = async () => {
    try {
      const [cats, us, sups] = await Promise.all([
        materialsApi.listCategories(),
        materialsApi.listUnits(),
        materialsApi.listSuppliers(),
      ]);
      setCategories(cats);
      setUnits(us);
      setSuppliers(sups);
    } catch { /* ignore */ }
  };

  const loadData = async (page = 1) => {
    setLoading(true);
    try {
      const result = await materialsApi.list({
        page,
        page_size: 20,
        search: filters.search || undefined,
        material_type: filters.material_type || undefined,
        category_id: filters.category_id,
      });
      setData(result);
    } catch (error) {
      msg.error('Không thể tải danh sách vật tư');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (values: any) => {
    try {
      if (editing) {
        await materialsApi.update(editing.id, values);
        msg.success('Cập nhật vật tư thành công');
      } else {
        await materialsApi.create(values);
        msg.success('Thêm vật tư thành công');
      }
      setModalOpen(false);
      form.resetFields();
      setEditing(null);
      loadData();
    } catch (error: any) {
      msg.error(error.response?.data?.detail || 'Lỗi khi lưu vật tư');
    }
  };

  const handleDelete = async (id: number) => {
    Modal.confirm({
      title: 'Xác nhận xóa',
      content: 'Bạn có chắc chắn muốn xóa vật tư này?',
      okText: 'Xóa',
      okType: 'danger',
      cancelText: 'Hủy',
      onOk: async () => {
        await materialsApi.delete(id);
        msg.success('Đã xóa vật tư');
        loadData();
      },
    });
  };

  const openEdit = (material: Material) => {
    setEditing(material);
    form.setFieldsValue(material);
    setModalOpen(true);
  };

  const openCreate = () => {
    setEditing(null);
    form.resetFields();
    setModalOpen(true);
  };

  const columns = [
    { title: 'Mã', dataIndex: 'code', key: 'code', width: 100, fixed: 'left' as const,
      render: (code: string) => <Text strong style={{ color: 'var(--primary)' }}>{code}</Text>,
    },
    { title: 'Tên vật tư', dataIndex: 'name', key: 'name', width: 220, ellipsis: true },
    {
      title: 'Loại', dataIndex: 'material_type', key: 'type', width: 110,
      render: (type: string) => {
        const t = MATERIAL_TYPES.find((m) => m.value === type);
        return <Tag color={t?.color}>{t?.label || type}</Tag>;
      },
    },
    {
      title: 'Danh mục', key: 'category', width: 130,
      render: (_: any, r: Material) => r.category?.name || '-',
    },
    { title: 'Model', dataIndex: 'model', key: 'model', width: 120, ellipsis: true },
    { title: 'NSX', dataIndex: 'manufacturer', key: 'mfg', width: 120, ellipsis: true },
    {
      title: 'Đơn giá', dataIndex: 'price', key: 'price', width: 130, align: 'right' as const,
      render: (price: number) => price ? formatCurrency(price) : '-',
    },
    {
      title: 'ĐVT', key: 'unit', width: 60,
      render: (_: any, r: Material) => r.unit?.code || '-',
    },
    {
      title: 'Trạng thái', dataIndex: 'status', key: 'status', width: 100,
      render: (status: string) => <Tag color={STATUS_COLORS[status]}>{STATUS_LABELS[status] || status}</Tag>,
    },
    {
      title: 'Thao tác', key: 'actions', width: 130, fixed: 'right' as const,
      render: (_: any, record: Material) => (
        <Space size="small">
          <Tooltip title="Chi tiết">
            <Button type="text" size="small" icon={<EyeOutlined />}
              onClick={() => { setSelected(record); setDetailOpen(true); }} />
          </Tooltip>
          <Tooltip title="Sửa">
            <Button type="text" size="small" icon={<EditOutlined />}
              onClick={() => openEdit(record)} />
          </Tooltip>
          <Tooltip title="Xóa">
            <Button type="text" size="small" danger icon={<DeleteOutlined />}
              onClick={() => handleDelete(record.id)} />
          </Tooltip>
        </Space>
      ),
    },
  ];

  return (
    <div className="page-container">
      <div className="page-header">
        <Title level={3} style={{ margin: 0 }}>📦 Danh mục Vật tư</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
          Thêm vật tư
        </Button>
      </div>

      {/* Filter Bar */}
      <div className="filter-bar">
        <Input
          placeholder="Tìm mã, tên, barcode..."
          prefix={<SearchOutlined />}
          style={{ width: 260 }}
          value={filters.search}
          onChange={(e) => setFilters((f) => ({ ...f, search: e.target.value }))}
          onPressEnter={() => loadData()}
          allowClear
        />
        <Select
          placeholder="Loại vật tư"
          style={{ width: 150 }}
          allowClear
          value={filters.material_type || undefined}
          onChange={(val) => setFilters((f) => ({ ...f, material_type: val || '' }))}
          options={MATERIAL_TYPES}
        />
        <Select
          placeholder="Danh mục"
          style={{ width: 160 }}
          allowClear
          value={filters.category_id}
          onChange={(val) => setFilters((f) => ({ ...f, category_id: val }))}
          options={categories.map((c) => ({ value: c.id, label: c.name }))}
        />
        <Button icon={<FilterOutlined />} onClick={() => loadData()}>Lọc</Button>
        <Button icon={<ReloadOutlined />} onClick={() => { setFilters({ search: '', material_type: '', category_id: undefined }); loadData(); }}>
          Reset
        </Button>
      </div>

      {/* Data Table */}
      <Card className="data-table-card">
        <Table
          columns={columns}
          dataSource={data.items}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1200 }}
          pagination={{
            current: data.page,
            pageSize: data.page_size,
            total: data.total,
            showTotal: (total) => `Tổng: ${total} vật tư`,
            showSizeChanger: false,
            onChange: (page) => loadData(page),
          }}
          size="middle"
        />
      </Card>

      {/* Create/Edit Modal */}
      <Modal
        title={editing ? '✏️ Sửa vật tư' : '➕ Thêm vật tư mới'}
        open={modalOpen}
        onCancel={() => { setModalOpen(false); setEditing(null); form.resetFields(); }}
        onOk={() => form.submit()}
        width={720}
        okText={editing ? 'Cập nhật' : 'Thêm mới'}
        cancelText="Hủy"
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="code" label="Mã vật tư" rules={[{ required: true }]}>
                <Input placeholder="VD: SP0001" disabled={!!editing} />
              </Form.Item>
            </Col>
            <Col span={16}>
              <Form.Item name="name" label="Tên vật tư" rules={[{ required: true }]}>
                <Input placeholder="Tên vật tư tiếng Việt" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="name_en" label="Tên tiếng Anh">
                <Input placeholder="English name" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="name_ja" label="Tên tiếng Nhật">
                <Input placeholder="日本語名" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="material_type" label="Loại" rules={[{ required: true }]}>
                <Select options={MATERIAL_TYPES} placeholder="Chọn loại" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="category_id" label="Danh mục">
                <Select options={categories.map((c) => ({ value: c.id, label: c.name }))} placeholder="Chọn" allowClear />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="unit_id" label="Đơn vị">
                <Select options={units.map((u) => ({ value: u.id, label: `${u.code} - ${u.name}` }))} placeholder="Chọn" allowClear />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="barcode" label="Barcode">
                <Input placeholder="Mã barcode" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="model" label="Model">
                <Input placeholder="Model/Part number" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="manufacturer" label="Nhà sản xuất">
                <Input placeholder="NSX" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="supplier_id" label="Nhà cung cấp">
                <Select options={suppliers.map((s) => ({ value: s.id, label: s.name }))} placeholder="Chọn" allowClear />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="price" label="Đơn giá (VND)">
                <InputNumber style={{ width: '100%' }} min={0} formatter={(v) => `${v}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="moq" label="MOQ">
                <InputNumber style={{ width: '100%' }} min={1} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="lifetime_hours" label="Tuổi thọ (giờ)">
                <InputNumber style={{ width: '100%' }} min={0} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="lead_time_days" label="Lead Time (ngày)">
                <InputNumber style={{ width: '100%' }} min={0} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="consumption_rate" label="Định mức tiêu hao">
                <InputNumber style={{ width: '100%' }} min={0} step={0.01} />
              </Form.Item>
            </Col>
            <Col span={24}>
              <Form.Item name="description" label="Mô tả">
                <Input.TextArea rows={2} placeholder="Mô tả chi tiết..." />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>

      {/* Detail Drawer */}
      <Drawer
        title={`📋 Chi tiết: ${selected?.code}`}
        open={detailOpen}
        onClose={() => { setDetailOpen(false); setSelected(null); }}
        width={500}
      >
        {selected && (
          <Descriptions column={1} bordered size="small">
            <Descriptions.Item label="Mã">{selected.code}</Descriptions.Item>
            <Descriptions.Item label="Barcode">{selected.barcode || '-'}</Descriptions.Item>
            <Descriptions.Item label="Tên">{selected.name}</Descriptions.Item>
            <Descriptions.Item label="Tên EN">{selected.name_en || '-'}</Descriptions.Item>
            <Descriptions.Item label="Tên JA">{selected.name_ja || '-'}</Descriptions.Item>
            <Descriptions.Item label="Loại">
              <Tag color={MATERIAL_TYPES.find((t) => t.value === selected.material_type)?.color}>
                {MATERIAL_TYPES.find((t) => t.value === selected.material_type)?.label}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="Danh mục">{selected.category?.name || '-'}</Descriptions.Item>
            <Descriptions.Item label="ĐVT">{selected.unit?.code || '-'}</Descriptions.Item>
            <Descriptions.Item label="Model">{selected.model || '-'}</Descriptions.Item>
            <Descriptions.Item label="NSX">{selected.manufacturer || '-'}</Descriptions.Item>
            <Descriptions.Item label="NCC">{selected.supplier?.name || '-'}</Descriptions.Item>
            <Descriptions.Item label="Đơn giá">{selected.price ? formatCurrency(selected.price) : '-'}</Descriptions.Item>
            <Descriptions.Item label="MOQ">{selected.moq || '-'}</Descriptions.Item>
            <Descriptions.Item label="Tuổi thọ">{selected.lifetime_hours ? `${selected.lifetime_hours} giờ` : '-'}</Descriptions.Item>
            <Descriptions.Item label="Lead Time">{selected.lead_time_days ? `${selected.lead_time_days} ngày` : '-'}</Descriptions.Item>
            <Descriptions.Item label="Định mức">{selected.consumption_rate ? `${selected.consumption_rate} ${selected.consumption_unit || ''}` : '-'}</Descriptions.Item>
            <Descriptions.Item label="Trạng thái">
              <Tag color={STATUS_COLORS[selected.status]}>{STATUS_LABELS[selected.status] || selected.status}</Tag>
            </Descriptions.Item>
          </Descriptions>
        )}
      </Drawer>
    </div>
  );
}
