import { useEffect, useState } from 'react';
import {
  Card, Table, Button, Space, Tag, Modal, Form, Input, Select, DatePicker,
  InputNumber, Typography, App, Row, Col, Divider, Popconfirm,
} from 'antd';
import { PlusOutlined, CheckCircleOutlined, CloseCircleOutlined, SearchOutlined, ReloadOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import { issuesApi, materialsApi, warehousesApi } from '../api';
import { ISSUE_TYPES, SHIFTS, STATUS_COLORS, STATUS_LABELS, formatCurrency } from '../utils/constants';
import type { Issue, Material, Location, PaginatedResponse } from '../types';

const { Title, Text } = Typography;

export default function IssuesPage() {
  const [data, setData] = useState<PaginatedResponse<Issue>>({ items: [], total: 0, page: 1, page_size: 20 });
  const [materials, setMaterials] = useState<Material[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [form] = Form.useForm();
  const { message: msg } = App.useApp();

  useEffect(() => { loadData(); loadLookups(); }, []);

  const loadLookups = async () => {
    try {
      const [mats, whs] = await Promise.all([
        materialsApi.list({ page: 1, page_size: 200 }),
        warehousesApi.list(),
      ]);
      setMaterials(mats.items);
      if (whs.length > 0) {
        const locs = await warehousesApi.listLocations(whs[0].id);
        setLocations(locs);
      }
    } catch {}
  };

  const loadData = async (page = 1) => {
    setLoading(true);
    try {
      setData(await issuesApi.list({ page, page_size: 20, search: search || undefined }));
    } catch { msg.error('Lỗi tải phiếu xuất'); }
    finally { setLoading(false); }
  };

  const handleSubmit = async (values: any) => {
    try {
      const payload = {
        issue_date: values.issue_date.format('YYYY-MM-DD'),
        issue_type: values.issue_type,
        machine: values.machine,
        line: values.line,
        shift: values.shift,
        receiver: values.receiver,
        department: values.department,
        reason: values.reason,
        work_order: values.work_order,
        remark: values.remark,
        items: values.items.map((item: any) => ({
          material_id: item.material_id,
          location_id: item.location_id,
          quantity: item.quantity,
          lot_number: item.lot_number,
        })),
      };
      await issuesApi.create(payload);
      msg.success('Tạo phiếu xuất thành công');
      setModalOpen(false); form.resetFields(); loadData();
    } catch (error: any) { msg.error(error.response?.data?.detail || 'Lỗi tạo phiếu'); }
  };

  const handleApprove = async (id: number) => {
    try {
      await issuesApi.approve(id);
      msg.success('Đã duyệt phiếu xuất và trừ tồn kho');
      loadData();
    } catch (error: any) { msg.error(error.response?.data?.detail || 'Lỗi duyệt'); }
  };

  const handleCancel = async (id: number) => {
    try {
      await issuesApi.cancel(id);
      msg.success('Đã hủy phiếu xuất');
      loadData();
    } catch (error: any) { msg.error(error.response?.data?.detail || 'Lỗi hủy'); }
  };

  const columns = [
    { title: 'Số phiếu', dataIndex: 'issue_number', key: 'number', width: 150,
      render: (v: string) => <Text strong style={{ color: 'var(--primary)' }}>{v}</Text> },
    { title: 'Ngày', dataIndex: 'issue_date', key: 'date', width: 100 },
    { title: 'Loại', dataIndex: 'issue_type', key: 'type', width: 130,
      render: (t: string) => <Tag>{ISSUE_TYPES.find((i) => i.value === t)?.label || t}</Tag> },
    { title: 'Máy', dataIndex: 'machine', key: 'machine', width: 100 },
    { title: 'Line', dataIndex: 'line', key: 'line', width: 80 },
    { title: 'Ca', dataIndex: 'shift', key: 'shift', width: 50 },
    { title: 'Người nhận', dataIndex: 'receiver', key: 'receiver', width: 120, ellipsis: true },
    { title: 'Tổng tiền', dataIndex: 'total_amount', key: 'amount', width: 130, align: 'right' as const,
      render: (v: number) => v ? formatCurrency(v) : '-' },
    { title: 'Trạng thái', dataIndex: 'status', key: 'status', width: 110,
      render: (s: string) => <Tag color={STATUS_COLORS[s]}>{STATUS_LABELS[s] || s}</Tag> },
    { title: 'Thao tác', key: 'actions', width: 180,
      render: (_: any, record: Issue) => (
        <Space size="small">
          {record.status === 'draft' && (
            <>
              <Popconfirm title="Duyệt phiếu xuất?" description="Tồn kho sẽ bị trừ" onConfirm={() => handleApprove(record.id)} okText="Duyệt" cancelText="Hủy">
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
        <Title level={3} style={{ margin: 0 }}>📤 Xuất kho</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => {
          form.resetFields();
          form.setFieldsValue({ issue_date: dayjs(), issue_type: 'production', items: [{}] });
          setModalOpen(true);
        }}>Tạo phiếu xuất</Button>
      </div>

      <div className="filter-bar">
        <Input placeholder="Tìm số phiếu, WO, người nhận..." prefix={<SearchOutlined />} style={{ width: 280 }}
          value={search} onChange={(e) => setSearch(e.target.value)} onPressEnter={() => loadData()} allowClear />
        <Button icon={<ReloadOutlined />} onClick={() => { setSearch(''); loadData(); }}>Tải lại</Button>
      </div>

      <Card className="data-table-card">
        <Table columns={columns} dataSource={data.items} rowKey="id" loading={loading}
          scroll={{ x: 1200 }} size="middle"
          pagination={{ current: data.page, pageSize: data.page_size, total: data.total,
            showTotal: (t) => `Tổng: ${t} phiếu`, onChange: (p) => loadData(p) }} />
      </Card>

      {/* Create Issue Modal */}
      <Modal title="➕ Tạo phiếu xuất kho" open={modalOpen}
        onCancel={() => setModalOpen(false)} onOk={() => form.submit()}
        width={900} okText="Tạo phiếu" cancelText="Hủy">
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Row gutter={16}>
            <Col span={6}>
              <Form.Item name="issue_date" label="Ngày xuất" rules={[{ required: true }]}>
                <DatePicker style={{ width: '100%' }} format="YYYY-MM-DD" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="issue_type" label="Loại xuất" rules={[{ required: true }]}>
                <Select options={ISSUE_TYPES} />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="machine" label="Máy">
                <Input placeholder="VD: AOI-01" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="line" label="Line">
                <Input placeholder="VD: Line 1" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="shift" label="Ca">
                <Select options={SHIFTS} allowClear placeholder="Chọn ca" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="receiver" label="Người nhận">
                <Input placeholder="Tên người nhận" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="department" label="Bộ phận">
                <Input placeholder="Bộ phận" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="work_order" label="Work Order">
                <Input placeholder="WO number" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="reason" label="Lý do xuất">
                <Input placeholder="Lý do" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="remark" label="Ghi chú">
                <Input placeholder="Ghi chú" />
              </Form.Item>
            </Col>
          </Row>

          <Divider>Chi tiết vật tư xuất</Divider>

          <Form.List name="items">
            {(fields, { add, remove }) => (
              <>
                {fields.map(({ key, name, ...rest }) => (
                  <Row gutter={8} key={key} style={{ marginBottom: 8 }}>
                    <Col span={8}>
                      <Form.Item {...rest} name={[name, 'material_id']} rules={[{ required: true, message: 'Chọn VT' }]}>
                        <Select placeholder="Vật tư" showSearch optionFilterProp="label"
                          options={materials.map((m) => ({ value: m.id, label: `${m.code} - ${m.name}` }))} />
                      </Form.Item>
                    </Col>
                    <Col span={6}>
                      <Form.Item {...rest} name={[name, 'location_id']}>
                        <Select placeholder="Vị trí lấy" showSearch optionFilterProp="label"
                          options={locations.map((l) => ({ value: l.id, label: l.code }))} />
                      </Form.Item>
                    </Col>
                    <Col span={4}>
                      <Form.Item {...rest} name={[name, 'quantity']} rules={[{ required: true, message: 'SL' }]}>
                        <InputNumber placeholder="Số lượng" min={0.01} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                    <Col span={4}>
                      <Form.Item {...rest} name={[name, 'lot_number']}>
                        <Input placeholder="Lot number" />
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
