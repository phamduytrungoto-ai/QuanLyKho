import { useState, useEffect } from 'react';
import { Card, Table, Button, DatePicker, Select, Space, Row, Col, Typography, message, Tag, Descriptions } from 'antd';
import { DownloadOutlined, ReloadOutlined, FileTextOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import { reportsApi, materialsApi } from '../../api';
import { formatNumber } from '../../utils/constants';
import type { StockCardReport } from '../../types';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;
const { Option } = Select;

export default function StockCardPage() {
  const [report, setReport] = useState<StockCardReport | null>(null);
  const [materials, setMaterials] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs]>([dayjs().startOf('month'), dayjs()]);
  const [materialId, setMaterialId] = useState<number | undefined>();

  useEffect(() => {
    materialsApi.list({ page_size: 1000 }).then(res => setMaterials(res.items));
  }, []);

  const fetchData = async () => {
    if (!materialId) {
      message.warning('Vui lòng chọn mã vật tư!');
      return;
    }
    setLoading(true);
    try {
      const start_date = dateRange[0].format('YYYY-MM-DD');
      const end_date = dateRange[1].format('YYYY-MM-DD');
      const res = await reportsApi.getStockCard({ material_id: materialId, start_date, end_date });
      setReport(res);
    } catch { message.error('Lỗi tải báo cáo'); }
    setLoading(false);
  };

  const handleExport = () => {
    if (!materialId) return;
    const start_date = dateRange[0].format('YYYY-MM-DD');
    const end_date = dateRange[1].format('YYYY-MM-DD');
    reportsApi.exportStockCard({ material_id: materialId, start_date, end_date });
  };

  const columns = [
    { title: 'Ngày giao dịch', dataIndex: 'transaction_date', width: 150 },
    { title: 'Loại nghiệp vụ', dataIndex: 'transaction_type', width: 150, render: (t: string) => {
      const typeMap: any = { 'receipt': { c: 'green', l: 'Nhập kho' }, 'issue': { c: 'blue', l: 'Xuất kho' } };
      return <Tag color={typeMap[t]?.c || 'default'}>{typeMap[t]?.l || t}</Tag>;
    }},
    { title: 'Mã tham chiếu', dataIndex: 'reference_number', width: 150 },
    { title: 'Nhập', dataIndex: 'inward_qty', align: 'right' as const, render: (v: number) => v > 0 ? <Text type="success">+{formatNumber(v)}</Text> : '-' },
    { title: 'Xuất', dataIndex: 'outward_qty', align: 'right' as const, render: (v: number) => v > 0 ? <Text type="danger">-{formatNumber(v)}</Text> : '-' },
    { title: 'Tồn sau GD', dataIndex: 'balance', align: 'right' as const, render: (v: number) => <Text strong>{formatNumber(v)}</Text> },
    { title: 'Ghi chú', dataIndex: 'note' },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={3} style={{ margin: 0 }}>
          <FileTextOutlined style={{ marginRight: 8 }} /> Thẻ Kho
        </Title>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={fetchData} loading={loading}>Làm mới</Button>
          <Button type="primary" icon={<DownloadOutlined />} onClick={handleExport} disabled={!report}>Xuất Excel</Button>
        </Space>
      </div>

      <Card size="small" style={{ marginBottom: 16 }}>
        <Space size="large" wrap>
          <div>
            <Text strong>Vật tư: </Text>
            <Select showSearch placeholder="Chọn vật tư" value={materialId} onChange={setMaterialId} style={{ width: 250 }}
              filterOption={(inp, opt: any) => opt.children.toLowerCase().includes(inp.toLowerCase())}>
              {materials.map(m => <Option key={m.id} value={m.id}>{m.code} - {m.name}</Option>)}
            </Select>
          </div>
          <div>
            <Text strong>Kỳ báo cáo: </Text>
            <RangePicker value={dateRange} onChange={(dates) => dates && setDateRange([dates[0] as dayjs.Dayjs, dates[1] as dayjs.Dayjs])} allowClear={false} />
          </div>
          <Button type="primary" onClick={fetchData}>Xem thẻ kho</Button>
        </Space>
      </Card>

      {report && (
        <Card style={{ marginBottom: 16 }} size="small">
          <Descriptions column={4} size="small" bordered>
            <Descriptions.Item label="Mã vật tư"><Text strong>{report.material_code}</Text></Descriptions.Item>
            <Descriptions.Item label="Tên vật tư" span={2}>{report.material_name}</Descriptions.Item>
            <Descriptions.Item label="Đơn vị tính">{report.unit}</Descriptions.Item>
            <Descriptions.Item label="Tồn đầu kỳ"><Text strong>{formatNumber(report.opening_balance)}</Text></Descriptions.Item>
            <Descriptions.Item label="Tồn cuối kỳ"><Text strong color="blue">{formatNumber(report.closing_balance)}</Text></Descriptions.Item>
          </Descriptions>
        </Card>
      )}

      <Card bodyStyle={{ padding: 0 }}>
        <Table
          columns={columns}
          dataSource={report?.transactions || []}
          rowKey={(r, i) => `${r.transaction_date}-${i}`}
          loading={loading}
          pagination={{ pageSize: 50 }}
          size="middle"
        />
      </Card>
    </div>
  );
}
