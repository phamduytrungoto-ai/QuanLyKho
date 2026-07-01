import { useState, useEffect } from 'react';
import { Card, Table, Button, DatePicker, Select, Space, Row, Col, Typography, message, Statistic } from 'antd';
import { DownloadOutlined, ReloadOutlined, DatabaseOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import { reportsApi, warehousesApi } from '../../api';
import { formatNumber, formatCurrency } from '../../utils/constants';
import type { InventoryValuationReport, Warehouse } from '../../types';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;
const { Option } = Select;

export default function InventoryReportPage() {
  const [report, setReport] = useState<InventoryValuationReport | null>(null);
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [loading, setLoading] = useState(false);
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs]>([dayjs().startOf('month'), dayjs()]);
  const [warehouseId, setWarehouseId] = useState<number | undefined>();

  useEffect(() => {
    warehousesApi.list().then(res => setWarehouses(res.items.filter((w: any) => w.is_active)));
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const start_date = dateRange[0].format('YYYY-MM-DD');
      const end_date = dateRange[1].format('YYYY-MM-DD');
      const res = await reportsApi.getInventoryValuation({ start_date, end_date, warehouse_id: warehouseId });
      setReport(res);
    } catch { message.error('Lỗi tải báo cáo'); }
    setLoading(false);
  };

  const handleExport = () => {
    const start_date = dateRange[0].format('YYYY-MM-DD');
    const end_date = dateRange[1].format('YYYY-MM-DD');
    reportsApi.exportInventoryValuation({ start_date, end_date, warehouse_id: warehouseId });
  };

  const columns = [
    { title: 'Mã VT', dataIndex: 'material_code', width: 120, render: (t: string) => <Text strong>{t}</Text> },
    { title: 'Tên vật tư', dataIndex: 'material_name' },
    { title: 'ĐVT', dataIndex: 'unit', width: 80 },
    { title: 'Tồn đầu', dataIndex: 'opening_stock', align: 'right' as const, render: (v: number) => formatNumber(v) },
    { title: 'GT Tồn đầu', dataIndex: 'opening_value', align: 'right' as const, render: (v: number) => formatCurrency(v) },
    { title: 'Nhập', dataIndex: 'inward_qty', align: 'right' as const, render: (v: number) => <Text type="success">{formatNumber(v)}</Text> },
    { title: 'GT Nhập', dataIndex: 'inward_value', align: 'right' as const, render: (v: number) => formatCurrency(v) },
    { title: 'Xuất', dataIndex: 'outward_qty', align: 'right' as const, render: (v: number) => <Text type="danger">{formatNumber(v)}</Text> },
    { title: 'GT Xuất', dataIndex: 'outward_value', align: 'right' as const, render: (v: number) => formatCurrency(v) },
    { title: 'Tồn cuối', dataIndex: 'closing_stock', align: 'right' as const, render: (v: number) => <Text strong>{formatNumber(v)}</Text> },
    { title: 'GT Tồn cuối', dataIndex: 'closing_value', align: 'right' as const, render: (v: number) => <Text strong color="blue">{formatCurrency(v)}</Text> },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={3} style={{ margin: 0 }}>
          <DatabaseOutlined style={{ marginRight: 8 }} /> Báo cáo Nhập - Xuất - Tồn
        </Title>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={fetchData} loading={loading}>Làm mới</Button>
          <Button type="primary" icon={<DownloadOutlined />} onClick={handleExport}>Xuất Excel</Button>
        </Space>
      </div>

      <Card size="small" style={{ marginBottom: 16 }}>
        <Space size="large" wrap>
          <div>
            <Text strong>Kỳ báo cáo: </Text>
            <RangePicker value={dateRange} onChange={(dates) => dates && setDateRange([dates[0] as dayjs.Dayjs, dates[1] as dayjs.Dayjs])} allowClear={false} />
          </div>
          <div>
            <Text strong>Kho: </Text>
            <Select placeholder="Tất cả kho" value={warehouseId} onChange={setWarehouseId} allowClear style={{ width: 200 }}>
              {warehouses.map(w => <Option key={w.id} value={w.id}>{w.name}</Option>)}
            </Select>
          </div>
          <Button type="primary" onClick={fetchData}>Xem báo cáo</Button>
        </Space>
      </Card>

      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}><Card size="small"><Statistic title="Tổng GT Tồn Đầu" value={report?.total_opening_value || 0} precision={0} suffix="₫" /></Card></Col>
        <Col span={6}><Card size="small"><Statistic title="Tổng GT Nhập" value={report?.total_inward_value || 0} precision={0} valueStyle={{ color: '#52c41a' }} suffix="₫" /></Card></Col>
        <Col span={6}><Card size="small"><Statistic title="Tổng GT Xuất" value={report?.total_outward_value || 0} precision={0} valueStyle={{ color: '#ff4d4f' }} suffix="₫" /></Card></Col>
        <Col span={6}><Card size="small"><Statistic title="Tổng GT Tồn Cuối" value={report?.total_closing_value || 0} precision={0} valueStyle={{ color: '#1677ff' }} suffix="₫" /></Card></Col>
      </Row>

      <Card bodyStyle={{ padding: 0 }}>
        <Table
          columns={columns}
          dataSource={report?.items || []}
          rowKey="material_id"
          loading={loading}
          pagination={{ pageSize: 20 }}
          scroll={{ x: 'max-content' }}
          size="small"
        />
      </Card>
    </div>
  );
}
