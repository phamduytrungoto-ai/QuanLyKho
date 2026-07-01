import { useEffect, useState } from 'react';
import { Card, Table, Button, Space, Tag, Modal, Form, Input, Select, Typography, App, Row, Col, Tree } from 'antd';
import { PlusOutlined, EditOutlined, EnvironmentOutlined, ReloadOutlined } from '@ant-design/icons';
import { warehousesApi } from '../api';
import { WAREHOUSE_TYPES } from '../utils/constants';
import type { Warehouse, Location } from '../types';

const { Title, Text } = Typography;

export default function WarehousesPage() {
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [locModalOpen, setLocModalOpen] = useState(false);
  const [editing, setEditing] = useState<Warehouse | null>(null);
  const [selectedWh, setSelectedWh] = useState<Warehouse | null>(null);
  const [form] = Form.useForm();
  const [locForm] = Form.useForm();
  const { message: msg } = App.useApp();

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await warehousesApi.list();
      setWarehouses(res.items.filter((w: any) => w.is_active));
    } catch { msg.error('Lỗi tải dữ liệu'); }
    finally { setLoading(false); }
  };

  const handleSubmitWh = async (values: any) => {
    try {
      if (editing) {
        await warehousesApi.update(editing.id, values);
        msg.success('Cập nhật kho thành công');
      } else {
        await warehousesApi.create(values);
        msg.success('Thêm kho thành công');
      }
      setModalOpen(false); form.resetFields(); setEditing(null);
      loadData();
    } catch (error: any) { msg.error(error.response?.data?.detail || 'Lỗi'); }
  };

  const handleSubmitLoc = async (values: any) => {
    if (!selectedWh) return;
    try {
      await warehousesApi.createLocation(selectedWh.id, {
        ...values,
        warehouse_id: selectedWh.id,
        code: `${selectedWh.code}-${values.rack || ''}-${values.level || ''}-${values.bin || ''}`,
      });
      msg.success('Thêm vị trí thành công');
      setLocModalOpen(false); locForm.resetFields();
      loadData();
    } catch (error: any) { msg.error(error.response?.data?.detail || 'Lỗi'); }
  };

  const buildLocationTree = (locations: Location[]) => {
    const racks: Record<string, Record<string, Location[]>> = {};
    locations.forEach((loc) => {
      const rack = loc.rack || 'Khác';
      const level = loc.level || '1';
      if (!racks[rack]) racks[rack] = {};
      if (!racks[rack][level]) racks[rack][level] = [];
      racks[rack][level].push(loc);
    });

    return Object.entries(racks).map(([rack, levels]) => ({
      title: `📦 Kệ ${rack}`,
      key: `rack-${rack}`,
      children: Object.entries(levels).map(([level, bins]) => ({
        title: `📂 Tầng ${level}`,
        key: `level-${rack}-${level}`,
        children: bins.map((bin) => ({
          title: `📍 Ô ${bin.bin || bin.code} ${!bin.is_active ? '(Ngừng)' : ''}`,
          key: `bin-${bin.id}`,
          isLeaf: true,
        })),
      })),
    }));
  };

  const columns = [
    { title: 'Mã', dataIndex: 'code', key: 'code', width: 80,
      render: (code: string) => <Text strong style={{ color: 'var(--primary)' }}>{code}</Text> },
    { title: 'Tên kho', dataIndex: 'name', key: 'name', width: 200 },
    { title: 'Tên EN', dataIndex: 'name_en', key: 'name_en', width: 180 },
    { title: 'Loại', dataIndex: 'warehouse_type', key: 'type', width: 130,
      render: (type: string) => {
        const t = WAREHOUSE_TYPES.find((w) => w.value === type);
        return <Tag>{t?.label || type}</Tag>;
      },
    },
    { title: 'Quản lý', dataIndex: 'manager', key: 'manager', width: 130 },
    { title: 'Số vị trí', key: 'loc_count', width: 90, align: 'center' as const,
      render: (_: any, r: Warehouse) => <Tag color="blue">{r.locations?.length || 0}</Tag> },
    { title: 'Thao tác', key: 'actions', width: 160,
      render: (_: any, record: Warehouse) => (
        <Space>
          <Button size="small" icon={<EditOutlined />}
            onClick={() => { setEditing(record); form.setFieldsValue(record); setModalOpen(true); }}>Sửa</Button>
          <Button size="small" icon={<PlusOutlined />} type="dashed"
            onClick={() => { setSelectedWh(record); setLocModalOpen(true); }}>Thêm vị trí</Button>
        </Space>
      ),
    },
  ];

  return (
    <div className="page-container">
      <div className="page-header">
        <Title level={3} style={{ margin: 0 }}>🏢 Kho & Vị trí</Title>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={loadData}>Tải lại</Button>
          <Button type="primary" icon={<PlusOutlined />}
            onClick={() => { setEditing(null); form.resetFields(); setModalOpen(true); }}>
            Thêm kho
          </Button>
        </Space>
      </div>

      <Card className="data-table-card">
        <Table
          columns={columns}
          dataSource={warehouses}
          rowKey="id"
          loading={loading}
          pagination={false}
          size="middle"
          expandable={{
            expandedRowRender: (record) => (
              <div style={{ padding: '8px 0' }}>
                <Text strong style={{ marginBottom: 8, display: 'block' }}>
                  <EnvironmentOutlined /> Cấu trúc vị trí ({record.locations?.length || 0} vị trí)
                </Text>
                {record.locations?.length > 0 ? (
                  <Tree
                    treeData={buildLocationTree(record.locations)}
                    defaultExpandAll
                    showLine
                    style={{ background: 'transparent' }}
                  />
                ) : (
                  <Text type="secondary">Chưa có vị trí</Text>
                )}
              </div>
            ),
          }}
        />
      </Card>

      {/* Warehouse Modal */}
      <Modal title={editing ? '✏️ Sửa kho' : '➕ Thêm kho mới'}
        open={modalOpen} onCancel={() => { setModalOpen(false); setEditing(null); }}
        onOk={() => form.submit()} okText={editing ? 'Cập nhật' : 'Thêm'} cancelText="Hủy" width={500}>
        <Form form={form} layout="vertical" onFinish={handleSubmitWh}>
          <Form.Item name="code" label="Mã kho" rules={[{ required: true }]}>
            <Input placeholder="VD: WH01" disabled={!!editing} />
          </Form.Item>
          <Form.Item name="name" label="Tên kho" rules={[{ required: true }]}>
            <Input placeholder="VD: Kho linh kiện" />
          </Form.Item>
          <Form.Item name="name_en" label="Tên EN">
            <Input placeholder="English name" />
          </Form.Item>
          <Form.Item name="warehouse_type" label="Loại kho" rules={[{ required: true }]}>
            <Select options={WAREHOUSE_TYPES} placeholder="Chọn loại" />
          </Form.Item>
          <Form.Item name="manager" label="Quản lý">
            <Input placeholder="Tên người quản lý" />
          </Form.Item>
          <Form.Item name="description" label="Mô tả">
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>

      {/* Location Modal */}
      <Modal title={`➕ Thêm vị trí vào ${selectedWh?.name || ''}`}
        open={locModalOpen} onCancel={() => setLocModalOpen(false)}
        onOk={() => locForm.submit()} okText="Thêm" cancelText="Hủy" width={400}>
        <Form form={locForm} layout="vertical" onFinish={handleSubmitLoc}>
          <Row gutter={12}>
            <Col span={8}>
              <Form.Item name="rack" label="Kệ" rules={[{ required: true }]}>
                <Input placeholder="A" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="level" label="Tầng" rules={[{ required: true }]}>
                <Input placeholder="1" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="bin" label="Ô" rules={[{ required: true }]}>
                <Input placeholder="01" />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="description" label="Mô tả">
            <Input placeholder="Mô tả vị trí" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
