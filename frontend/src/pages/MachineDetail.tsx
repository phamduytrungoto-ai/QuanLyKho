import { useState, useEffect, useCallback } from 'react';
import {
  Card, Tabs, Descriptions, Table, Button, Tag, Space, Modal, Form, Input, Select,
  message, Tooltip, Progress, Row, Col, Typography, DatePicker, InputNumber, Timeline, Statistic
} from 'antd';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeftOutlined, PlusOutlined, ToolOutlined, FileTextOutlined } from '@ant-design/icons';
import { machinesApi, materialsApi } from '../api';
import type { MachineDetail, MachinePart, MaintenanceLog, MachineRunningHour } from '../types';
import {
  MACHINE_STATUS_MAP, MAINTENANCE_TYPE_MAP, PART_STATUS_MAP, getLifetimeColor, formatNumber
} from '../utils/constants';
import dayjs from 'dayjs';

const { Title, Text } = Typography;

export default function MachineDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const machineId = Number(id);

  const [machine, setMachine] = useState<MachineDetail | null>(null);
  const [parts, setParts] = useState<MachinePart[]>([]);
  const [maintLogs, setMaintLogs] = useState<any[]>([]); // Simplified for timeline
  const [runningHours, setRunningHours] = useState<MachineRunningHour[]>([]);
  const [timeline, setTimeline] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('info');

  const fetchMachineDetail = useCallback(async () => {
    if (!machineId) return;
    setLoading(true);
    try {
      setMachine(await machinesApi.get(machineId));
      setParts(await machinesApi.listParts(machineId));
      setTimeline(await machinesApi.getTimeline(machineId, 50));
      setRunningHours(await machinesApi.listRunningHours(machineId, 30));
    } catch { message.error('Lỗi tải chi tiết máy'); }
    setLoading(false);
  }, [machineId]);

  useEffect(() => { fetchMachineDetail(); }, [fetchMachineDetail]);

  // Modal forms
  const [partModalOpen, setPartModalOpen] = useState(false);
  const [partForm] = Form.useForm();
  
  const [maintModalOpen, setMaintModalOpen] = useState(false);
  const [maintForm] = Form.useForm();
  
  const [hoursModalOpen, setHoursModalOpen] = useState(false);
  const [hoursForm] = Form.useForm();

  // Parts Handlers
  const handleInstallPart = async (values: any) => {
    try {
      if (values.installed_date) values.installed_date = values.installed_date.format('YYYY-MM-DD');
      await machinesApi.installPart(machineId, values);
      message.success('Đã lắp linh kiện mới');
      setPartModalOpen(false);
      partForm.resetFields();
      fetchMachineDetail();
    } catch { message.error('Lỗi lắp linh kiện'); }
  };

  const handleReplacePart = async (partId: number) => {
    try {
      await machinesApi.replacePart(machineId, partId, { note: 'Thay thế định kỳ/hỏng' });
      message.success('Đã ghi nhận thay linh kiện');
      fetchMachineDetail();
    } catch { message.error('Lỗi thay linh kiện'); }
  };

  // Maintenance Handlers
  const handleAddMaintenance = async (values: any) => {
    try {
      if (values.maintenance_date) values.maintenance_date = values.maintenance_date.format('YYYY-MM-DD');
      await machinesApi.createMaintenance(machineId, { ...values, items: [] });
      message.success('Đã thêm log sửa chữa');
      setMaintModalOpen(false);
      maintForm.resetFields();
      fetchMachineDetail();
    } catch { message.error('Lỗi thêm log sửa chữa'); }
  };

  // Running Hours Handlers
  const handleAddHours = async (values: any) => {
    try {
      if (values.record_date) values.record_date = values.record_date.format('YYYY-MM-DD');
      await machinesApi.recordRunningHours(machineId, values);
      message.success('Đã ghi nhận giờ chạy');
      setHoursModalOpen(false);
      hoursForm.resetFields();
      fetchMachineDetail();
    } catch { message.error('Lỗi ghi nhận giờ chạy'); }
  };

  if (!machine) return <Card loading={loading} />;

  const s = MACHINE_STATUS_MAP[machine.status] || { label: machine.status, color: '#8c8c8c', icon: '⚪' };

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/machines')} style={{ marginBottom: 16 }}>
          Quay lại danh sách
        </Button>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <Title level={3} style={{ margin: 0 }}>
              {machine.code} - {machine.name}
            </Title>
            <Space style={{ marginTop: 8 }}>
              <Tag color={s.color} style={{ fontSize: 14, padding: '4px 8px' }}>{s.icon} {s.label}</Tag>
              {machine.line && <Tag color="blue" style={{ fontSize: 14, padding: '4px 8px' }}>{machine.line.name}</Tag>}
              <Text type="secondary">Type: {machine.machine_type}</Text>
            </Space>
          </div>
          <Space>
            <Statistic title="Giờ chạy hiện tại" value={machine.current_running_hours} suffix="h" valueStyle={{ color: '#1677ff' }} />
          </Space>
        </div>
      </div>

      <Card>
        <Tabs activeKey={activeTab} onChange={setActiveTab} items={[
          {
            key: 'info',
            label: 'Thông tin chung',
            children: (
              <Row gutter={24}>
                <Col span={16}>
                  <Descriptions bordered column={2} size="small">
                    <Descriptions.Item label="Hãng sản xuất">{machine.manufacturer || '—'}</Descriptions.Item>
                    <Descriptions.Item label="Model">{machine.model || '—'}</Descriptions.Item>
                    <Descriptions.Item label="Serial Number">{machine.serial_number || '—'}</Descriptions.Item>
                    <Descriptions.Item label="Vị trí">{machine.location || '—'}</Descriptions.Item>
                    <Descriptions.Item label="Ngày lắp đặt">{machine.install_date || '—'}</Descriptions.Item>
                    <Descriptions.Item label="Hết hạn bảo hành">{machine.warranty_expiry || '—'}</Descriptions.Item>
                    <Descriptions.Item label="Chu kỳ bảo trì">{machine.maintenance_interval_hours ? `${machine.maintenance_interval_hours}h` : '—'}</Descriptions.Item>
                    <Descriptions.Item label="Bảo trì lần cuối">{machine.last_maintenance_date || '—'}</Descriptions.Item>
                  </Descriptions>
                  <div style={{ marginTop: 16 }}>
                    <Text strong>Mô tả:</Text> <Text>{machine.description || 'Chưa có thông tin'}</Text>
                  </div>
                </Col>
                <Col span={8}>
                  <Card size="small" title="Thống kê">
                    <Statistic title="Tổng lần sửa chữa" value={machine.total_maintenance_count} />
                    <Statistic title="Tổng downtime" value={machine.total_downtime_hours} suffix="h" style={{ marginTop: 16 }} />
                    <Statistic title="Linh kiện cảnh báo" value={machine.critical_parts_count} valueStyle={{ color: '#ff4d4f' }} style={{ marginTop: 16 }} />
                  </Card>
                </Col>
              </Row>
            ),
          },
          {
            key: 'parts',
            label: `Linh kiện (${parts.length})`,
            children: (
              <div>
                <Button type="primary" icon={<PlusOutlined />} onClick={() => setPartModalOpen(true)} style={{ marginBottom: 16 }}>
                  Lắp linh kiện mới
                </Button>
                <Table
                  columns={[
                    { title: 'Vị trí', dataIndex: 'position', key: 'pos', width: 150 },
                    { title: 'Mã VT', dataIndex: 'material_code', key: 'mcode', width: 120, render: t => <Text strong>{t}</Text> },
                    { title: 'Tên vật tư/Linh kiện', dataIndex: 'material_name', key: 'mname' },
                    { title: 'Trạng thái', dataIndex: 'status', key: 'status', width: 100, align: 'center', render: s => {
                      const st = PART_STATUS_MAP[s] || { label: s, color: 'default' };
                      return <Tag color={st.color}>{st.label}</Tag>;
                    }},
                    { title: 'Tuổi thọ (%)', dataIndex: 'lifetime_percentage', key: 'life', width: 250, render: (val, rec) => (
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <Progress percent={Number(val)} size="small" style={{ width: 120 }}
                          strokeColor={getLifetimeColor(Number(val))} />
                        <Text style={{ fontSize: 12 }} type="secondary">{formatNumber(rec.current_hours)}/{formatNumber(rec.lifetime_hours)}h</Text>
                      </div>
                    )},
                    { title: 'Hành động', key: 'action', width: 120, align: 'center', render: (_, rec) => (
                      <Button size="small" type="primary" ghost icon={<ToolOutlined />}
                        onClick={() => {
                          Modal.confirm({
                            title: 'Xác nhận thay linh kiện?',
                            content: `Bạn đang thay thế: ${rec.material_name} tại vị trí ${rec.position}. Giờ chạy sẽ được reset về 0.`,
                            onOk: () => handleReplacePart(rec.id)
                          });
                        }}>Thay mới</Button>
                    )}
                  ]}
                  dataSource={parts}
                  rowKey="id"
                  size="small"
                  pagination={false}
                />
              </div>
            ),
          },
          {
            key: 'history',
            label: 'Lịch sử sửa chữa',
            children: (
              <div>
                <Button type="primary" icon={<PlusOutlined />} onClick={() => setMaintModalOpen(true)} style={{ marginBottom: 16 }}>
                  Thêm log sửa chữa
                </Button>
                <div style={{ padding: '0 24px' }}>
                  <Timeline mode="left">
                    {timeline.map((item, idx) => {
                      const isMaint = item.type === 'maintenance';
                      return (
                        <Timeline.Item key={idx} color={isMaint ? 'blue' : 'green'} label={<Text strong>{dayjs(item.date).format('DD/MM/YYYY')}</Text>}>
                          {isMaint ? (
                            <Card size="small" title={<Space><ToolOutlined /> <Text strong>{item.log_number} - {MAINTENANCE_TYPE_MAP[item.maintenance_type]?.label}</Text></Space>}>
                              <p><b>Mô tả:</b> {item.description}</p>
                              {item.root_cause && <p><b>Nguyên nhân:</b> {item.root_cause}</p>}
                              {item.action_taken && <p><b>Khắc phục:</b> {item.action_taken}</p>}
                              <Space style={{ marginTop: 8 }}>
                                <Tag>Downtime: {item.downtime_hours || 0}h</Tag>
                                <Tag>Người xử lý: {item.performer}</Tag>
                              </Space>
                            </Card>
                          ) : (
                            <Card size="small" title={<Space><ToolOutlined style={{ color: '#52c41a'}} /> <Text strong style={{ color: '#52c41a'}}>Thay linh kiện</Text></Space>}>
                              <p>Thay thế <b>{item.material_code}</b> ({item.material_name}) tại vị trí <b>{item.position}</b>.</p>
                              <Text type="secondary" style={{ fontSize: 12 }}>Giờ chạy khi thay: {item.hours_at_replacement}h / {item.lifetime_hours}h</Text>
                            </Card>
                          )}
                        </Timeline.Item>
                      )
                    })}
                  </Timeline>
                  {timeline.length === 0 && <div style={{ textAlign: 'center', padding: 20 }}><Text type="secondary">Chưa có dữ liệu lịch sử</Text></div>}
                </div>
              </div>
            ),
          },
          {
            key: 'hours',
            label: 'Nhật ký giờ chạy',
            children: (
              <div>
                <Button type="primary" icon={<PlusOutlined />} onClick={() => setHoursModalOpen(true)} style={{ marginBottom: 16 }}>
                  Ghi nhận giờ chạy
                </Button>
                <Table
                  columns={[
                    { title: 'Ngày ghi nhận', dataIndex: 'record_date', key: 'date', width: 150, render: d => dayjs(d).format('DD/MM/YYYY') },
                    { title: 'Ca làm việc', dataIndex: 'shift', key: 'shift', width: 150 },
                    { title: 'Số giờ', dataIndex: 'running_hours', key: 'hours', width: 120, render: v => <Text strong>{v}h</Text> },
                    { title: 'Lũy kế', dataIndex: 'cumulative_hours', key: 'cum', width: 150, render: v => `${v}h` },
                    { title: 'Người ghi nhận', dataIndex: 'recorder_name', key: 'user' },
                  ]}
                  dataSource={runningHours}
                  rowKey="id"
                  size="small"
                  pagination={{ pageSize: 10 }}
                />
              </div>
            ),
          }
        ]} />
      </Card>

      {/* Parts Modal */}
      <Modal title="Lắp linh kiện mới" open={partModalOpen} onCancel={() => setPartModalOpen(false)} onOk={() => partForm.submit()} width={500}>
        <Form form={partForm} layout="vertical" onFinish={handleInstallPart}>
          <Form.Item name="material_id" label="Mã linh kiện (ID)" rules={[{ required: true }]}>
            <InputNumber style={{ width: '100%' }} placeholder="Nhập ID vật tư (tạm thời)" />
          </Form.Item>
          <Form.Item name="position" label="Vị trí lắp" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="lifetime_hours" label="Tuổi thọ dự kiến (giờ)" rules={[{ required: true }]}>
            <InputNumber style={{ width: '100%' }} min={1} />
          </Form.Item>
          <Form.Item name="installed_date" label="Ngày lắp" initialValue={dayjs()}>
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>

      {/* Maintenance Modal */}
      <Modal title="Thêm log sửa chữa" open={maintModalOpen} onCancel={() => setMaintModalOpen(false)} onOk={() => maintForm.submit()} width={600}>
        <Form form={maintForm} layout="vertical" onFinish={handleAddMaintenance}>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="maintenance_type" label="Loại bảo trì" rules={[{ required: true }]} initialValue="corrective">
                <Select>
                  {Object.entries(MAINTENANCE_TYPE_MAP).map(([k, v]) => <Select.Option key={k} value={k}>{v.label}</Select.Option>)}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="maintenance_date" label="Ngày thực hiện" rules={[{ required: true }]} initialValue={dayjs()}>
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="description" label="Mô tả sự cố/Nội dung" rules={[{ required: true }]}>
            <Input.TextArea rows={2} />
          </Form.Item>
          <Form.Item name="root_cause" label="Nguyên nhân">
            <Input.TextArea rows={2} />
          </Form.Item>
          <Form.Item name="action_taken" label="Biện pháp khắc phục">
            <Input.TextArea rows={2} />
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="downtime_hours" label="Downtime (giờ)">
                <InputNumber style={{ width: '100%' }} min={0} step={0.5} />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>

      {/* Running Hours Modal */}
      <Modal title="Ghi nhận giờ chạy" open={hoursModalOpen} onCancel={() => setHoursModalOpen(false)} onOk={() => hoursForm.submit()} width={400}>
        <Form form={hoursForm} layout="vertical" onFinish={handleAddHours}>
          <Form.Item name="record_date" label="Ngày chạy" rules={[{ required: true }]} initialValue={dayjs()}>
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="running_hours" label="Số giờ hoạt động" rules={[{ required: true }]}>
            <InputNumber style={{ width: '100%' }} min={0} max={24} step={0.5} />
          </Form.Item>
          <Form.Item name="note" label="Ghi chú">
            <Input />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
