import { useState, useEffect } from 'react';
import { Card, Table, Button, DatePicker, Space, Row, Col, Typography, message, Statistic } from 'antd';
import { DownloadOutlined, ReloadOutlined, ToolOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import { reportsApi } from '../../api';
import { formatNumber, formatCurrency } from '../../utils/constants';
import type { MaintenanceCostReport } from '../../types';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;

export default function MaintenanceCostPage() {
  const [report, setReport] = useState<MaintenanceCostReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs]>([dayjs().startOf('month'), dayjs()]);

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const start_date = dateRange[0].format('YYYY-MM-DD');
      const end_date = dateRange[1].format('YYYY-MM-DD');
      const res = await reportsApi.getMaintenanceCost({ start_date, end_date });
      setReport(res);
    } catch { message.error('Lỗi tải báo cáo chi phí bảo trì'); }
    setLoading(false);
  };

  const handleExport = () => {
    const start_date = dateRange[0].format('YYYY-MM-DD');
    const end_date = dateRange[1].format('YYYY-MM-DD');
    reportsApi.exportMaintenanceCost({ start_date, end_date });
  };

  const columns = [
    { title: 'Line / Khu vực', dataIndex: 'line_name', width: 150, render: (t: string) => t || '—' },
    { title: 'Mã máy', dataIndex: 'machine_code', width: 120, render: (t: string) => <Text strong>{t}</Text> },
    { title: 'Tên máy', dataIndex: 'machine_name' },
    { title: 'Số lần bảo trì', dataIndex: 'maintenance_count', align: 'center' as const, render: (v: number) => formatNumber(v) },
    { title: 'Thời gian dừng máy', dataIndex: 'total_downtime', align: 'center' as const, render: (v: number) => <Text type="danger">{v}h</Text> },
    { title: 'LK đã thay thế', dataIndex: 'parts_replaced_count', align: 'center' as const, render: (v: number) => formatNumber(v) },
    { title: 'Tổng chi phí (VND)', dataIndex: 'total_cost', align: 'right' as const, render: (v: number) => <Text strong color="red">{formatCurrency(v)}</Text> },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={3} style={{ margin: 0 }}>
          <ToolOutlined style={{ marginRight: 8 }} /> Báo cáo Chi phí Bảo trì
        </Title>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={fetchData} loading={loading}>Làm mới</Button>
          <Button type="primary" icon={<DownloadOutlined />} onClick={handleExport}>Xuất Excel</Button>
        </Space>
      </div>

      <Card size="small" style={{ marginBottom: 16 }}>
        <Space size="large" wrap>
          <div>
            <Text strong>Thời gian: </Text>
            <RangePicker value={dateRange} onChange={(dates) => dates && setDateRange([dates[0] as dayjs.Dayjs, dates[1] as dayjs.Dayjs])} allowClear={false} />
          </div>
          <Button type="primary" onClick={fetchData}>Xem báo cáo</Button>
        </Space>
      </Card>

      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={8}>
          <Card size="small">
            <Statistic title="Tổng chi phí thay linh kiện (toàn nhà máy)" value={report?.total_overall_cost || 0} precision={0} suffix="₫" valueStyle={{ color: '#ff4d4f' }} />
          </Card>
        </Col>
      </Row>

      <Card bodyStyle={{ padding: 0 }}>
        <Table
          columns={columns}
          dataSource={report?.items || []}
          rowKey="machine_id"
          loading={loading}
          pagination={{ pageSize: 20 }}
          size="middle"
        />
      </Card>
    </div>
  );
}
