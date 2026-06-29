import { useEffect, useState } from 'react';
import {
  Card, Table, Button, Space, Tag, Modal, Form, Input, Select, DatePicker,
  InputNumber, Typography, App, Row, Col, Divider, Popconfirm,
} from 'antd';
import { PlusOutlined, CheckCircleOutlined, CloseCircleOutlined, EyeOutlined, ReloadOutlined, SearchOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import { receiptsApi, materialsApi, warehousesApi } from '../../api';
import { RECEIPT_TYPES, STATUS_COLORS, STATUS_LABELS, formatCurrency } from '../../utils/constants';
import type { Receipt, Material, Warehouse, Location, PaginatedResponse } from '../../types';

const { Title, Text } = Typography;

export default function ReceiptsPage() {
  const [data, setData] = useState<PaginatedResponse<Receipt>>({ items: [], total: 0, page: 1, page_size: 20 });
  const [materials, setMaterials] = useState<Material[]>([]);
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [suppliers, setSuppliers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [form] = Form.useForm();
  const { message: msg, modal } = App.useApp();

  useEffect(() => { loadData(); loadLookups(); }, []);

  const loadLookups = async () => {
    try {
      const [mats, whs, sups] = await Promise.all([
        materialsApi.list({ page: 1, page_size: 200 }),
        warehousesApi.list(),
        materialsApi.listSuppliers(),
      ]);
      setMaterials(mats.items);
      setWarehouses(whs);
      setSuppliers(sups);
      if (whs.length > 0) {
        const locs = await warehousesApi.listLocations(whs[0].id);
        setLocations(locs);
      }
    } catch {}
  };

  const loadData = async (page = 1) => {
    setLoading(true);
    try {
      setData(await receiptsApi.list({ page, page_size: 20, search: search || undefined }));
    } catch { msg.error('Lỗi tải phiếu nhập'); }
    finally { setLoading(false); }
  };

  const handleSubmit = async (values: any) => {
    try {
      const payload = {
        receipt_date: values.receipt_date.format('YYYY-MM-DD'),
        receipt_type: values.receipt_type,
        supplier_id: values.supplier_id,
        po_number: values.po_number,
        invoice_number: values.invoice_number,
        note: values.note,
        items: values.items.map((item: any) => ({
          material_id: item.material_id,
          location_id: item.location_id,
          quantity: item.quantity,
          unit_price: item.unit_price,
          lot_number: item.lot_number,
        })),
      };
      await receiptsApi.create(payload);
      msg.success('Tạo phiếu nhập thành công');
      setModalOpen(false); form.resetFields(); loadData();
    } catch (error: any) { msg.error(error.response?.data?.detail || 'Lỗi tạo phiếu'); }
  };

  const handleApprove = async (id: number) => {
    try {
      await receiptsApi.approve(id);
      msg.success('Đã duyệt phiếu nhập và cập nhật tồn kho');
      loadData();
    } catch (error: any) { msg.error(error.response?.data?.detail || 'Lỗi duyệt'); }
  };

  const handleCancel = async (id: number) => {
    try {
      await receiptsApi.cancel(id);
      msg.success('Đã hủy phiếu nhập');
      loadData();
    } catch (error: any) { msg.error(error.response?.data?.detail || 'Lỗi hủy'); }
  };

  const columns = [
    { title: 'Số phiếu', dataIndex: 'receipt_number', key: 'number', width: 150,
      render: (v: string) => <Text strong style={{ color: 'var(--primary)' }}>{v}</Text> },
    { title: 'Ngày', dataIndex: 'receipt_date', key: 'date', width: 100 },
    { title: 'Loại', dataIndex: 'receipt_type', key: 'type', width: 130,
      render: (t: string) => <Tag>{RECEIPT_TYPES.find((r) => r.value === t)?.label || t}</Tag> },
    { title: 'Tổng tiền', dataIndex: 'total_amount', key: 'amount', width: 140, align: 'right' as const,
      render: (v: number) => v ? formatCurrency(v) : '-' },
    { title: 'SL dòng', key: 'items', width: 70, align: 'center' as const,
      render: (_: any, r: Receipt) => r.items?.length || 0 },
    { title: 'Trạng thái', dataIndex: 'status', key: 'status', width: 110,
      render: (s: string) => <Tag color={STATUS_COLORS[s]}>{STATUS_LABELS[s] || s}</Tag> },
    { title: 'Thao tác', key: 'actions', width: 180,
      render: (_: any, record: Receipt) => (
        <Space size="small">
          {record.status === 'draft' && (
            <>
              <Popconfirm title="Duyệt phiếu nhập?" description="Tồn kho sẽ được cập nhật" onConfirm={() => handleApprove(record.id)} okText="Duyệt" cancelText="Hủy">
                <Button size="small" type="primary" icon={<CheckCircleOutlined />}>Duyệt</Button>
              </Popconfirm>
              <Popconfirm title="Hủy phiếu?" onConfirm={() => handleCancel(record.id)} okText="Hủy phiếu" cancelText="Không">
                <Button size="small" danger icon={<CloseCircleOutlined />}>Hủy</Button>
              </Popconfirm>
            </>
          )}
          {record.status === 'approved' && <Tag color="success">✅ Đã duyệt</Tag>}
        </Space>
      ),
    },
  ];

  return (
    <div className="page-container">
      <div className="page-header">
        <Title level={3} style={{ margin: 0 }}>📥 Nhập kho</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => {
          form.resetFields();
          form.setFieldsValue({ receipt_date: dayjs(), receipt_type: 'purchase', items: [{}] });
          setModalOpen(true);
        }}>Tạo phiếu nhập</Button>
      </div>

      <div className="filter-bar">
        <Input placeholder="Tìm số phiếu, PO..." prefix={<SearchOutlined />} style={{ width: 260 }}
          value={search} onChange={(e) => setSearch(e.target.value)} onPressEnter={() => loadData()} allowClear />
        <Button icon={<ReloadOutlined />} onClick={() => { setSearch(''); loadData(); }}>Tải lại</Button>
      </div>

      <Card className="data-table-card">
        <Table columns={columns} dataSource={data.items} rowKey="id" loading={loading}
          scroll={{ x: 900 }} size="middle"
          pagination={{ current: data.page, pageSize: data.page_size, total: data.total,
            showTotal: (t) => `Tổng: ${t} phiếu`, onChange: (p) => loadData(p) }} />
      </Card>

      {/* Create Receipt Modal */}
      <Modal title="➕ Tạo phiếu nhập kho" open={modalOpen}
        onCancel={() => setModalOpen(false)} onOk={() => form.submit()}
        width={800} okText="Tạo phiếu" cancelText="Hủy">
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="receipt_date" label="Ngày nhập" rules={[{ required: true }]}>
                <DatePicker style={{ width: '100%' }} format="YYYY-MM-DD" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="receipt_type" label="Loại nhập" rules={[{ required: true }]}>
                <Select options={RECEIPT_TYPES} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="supplier_id" label="Nhà cung cấp">
                <Select options={suppliers.map((s: any) => ({ value: s.id, label: s.name }))} allowClear placeholder="Chọn NCC" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="po_number" label="Số PO">
                <Input placeholder="PO number" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="invoice_number" label="Số Invoice">
                <Input placeholder="Invoice number" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="note" label="Ghi chú">
                <Input placeholder="Ghi chú" />
              </Form.Item>
            </Col>
          </Row>

          <Divider>Chi tiết vật tư</Divider>

          <Form.List name="items">
            {(fields, { add, remove }) => (
              <>
                {fields.map(({ key, name, ...rest }) => (
                  <Row gutter={8} key={key} style={{ marginBottom: 8 }}>
                    <Col span={7}>
                      <Form.Item {...rest} name={[name, 'material_id']} rules={[{ required: true, message: 'Chọn VT' }]}>
                        <Select placeholder="Vật tư" showSearch optionFilterProp="label"
                          options={materials.map((m) => ({ value: m.id, label: `${m.code} - ${m.name}` }))} />
                      </Form.Item>
                    </Col>
                    <Col span={5}>
                      <Form.Item {...rest} name={[name, 'location_id']}>
                        <Select placeholder="Vị trí" showSearch optionFilterProp="label"
                          options={locations.map((l) => ({ value: l.id, label: l.code }))} />
                      </Form.Item>
                    </Col>
                    <Col span={3}>
                      <Form.Item {...rest} name={[name, 'quantity']} rules={[{ required: true, message: 'SL' }]}>
                        <InputNumber placeholder="SL" min={0.01} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                    <Col span={4}>
                      <Form.Item {...rest} name={[name, 'unit_price']}>
                        <InputNumber placeholder="Đơn giá" min={0} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                    <Col span={3}>
                      <Form.Item {...rest} name={[name, 'lot_number']}>
                        <Input placeholder="Lot" />
                      </Form.Item>
                    </Col>
                    <Col span={2}>
                      <Button danger onClick={() => remove(name)} block>Xóa</Button>
                    </Col>
                  </Row>
                ))}
                <Button type="dashed" onClick={() => add()} block icon={<PlusOutlined />}>
                  Thêm dòng vật tư
                </Button>
              </>
            )}
          </Form.List>
        </Form>
      </Modal>
    </div>
  );
}
