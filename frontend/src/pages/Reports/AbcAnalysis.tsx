import { useState, useEffect } from 'react';
import { Card, Table, Button, DatePicker, Space, Row, Col, Typography, message, Tag, Statistic } from 'antd';
import { DownloadOutlined, ReloadOutlined, PieChartOutlined } from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import dayjs from 'dayjs';
import { reportsApi } from '../../api';
import { formatNumber, formatCurrency } from '../../utils/constants';
import type { AbcAnalysisReport } from '../../types';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;

export default function AbcAnalysisPage() {
  const [report, setReport] = useState<AbcAnalysisReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs]>([dayjs().subtract(3, 'month'), dayjs()]);

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const start_date = dateRange[0].format('YYYY-MM-DD');
      const end_date = dateRange[1].format('YYYY-MM-DD');
      const res = await reportsApi.getAbcAnalysis({ start_date, end_date });
      setReport(res);
    } catch { message.error('Lỗi tải báo cáo ABC'); }
    setLoading(false);
  };

  const handleExport = () => {
    const start_date = dateRange[0].format('YYYY-MM-DD');
    const end_date = dateRange[1].format('YYYY-MM-DD');
    reportsApi.exportAbcAnalysis({ start_date, end_date });
  };

  const pieOption = {
    tooltip: { trigger: 'item', formatter: '{b}: {c} mã ({d}%)' },
    legend: { bottom: 0 },
    color: ['#52c41a', '#faad14', '#ff4d4f'],
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        itemStyle: { borderRadius: 5, borderColor: '#fff', borderWidth: 2 },
        data: [
          { value: report?.summary_a || 0, name: 'Nhóm A (Giá trị cao)' },
          { value: report?.summary_b || 0, name: 'Nhóm B (Trung bình)' },
          { value: report?.summary_c || 0, name: 'Nhóm C (Giá trị thấp)' }
        ]
      }
    ]
  };

  const columns = [
    { title: 'Nhóm', dataIndex: 'abc_class', width: 80, align: 'center' as const, render: (t: string) => {
      const colors: any = { 'A': 'green', 'B': 'orange', 'C': 'red' };
      return <Tag color={colors[t]} style={{ margin: 0, width: '100%', textAlign: 'center' }}>{t}</Tag>;
    }},
    { title: 'Mã VT', dataIndex: 'material_code', width: 120, render: (t: string) => <Text strong>{t}</Text> },
    { title: 'Tên vật tư', dataIndex: 'material_name' },
    { title: 'ĐVT', dataIndex: 'unit', width: 80 },
    { title: 'Tổng SL Xuất', dataIndex: 'total_usage_qty', align: 'right' as const, render: (v: number) => formatNumber(v) },
    { title: 'Tổng GT Xuất', dataIndex: 'total_usage_value', align: 'right' as const, render: (v: number) => formatCurrency(v) },
    { title: '% GT Tích luỹ', dataIndex: 'cumulative_percentage', align: 'right' as const, render: (v: number) => <Text strong color="blue">{v.toFixed(2)}%</Text> },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={3} style={{ margin: 0 }}>
          <PieChartOutlined style={{ marginRight: 8 }} /> Phân tích ABC
        </Title>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={fetchData} loading={loading}>Làm mới</Button>
          <Button type="primary" icon={<DownloadOutlined />} onClick={handleExport}>Xuất Excel</Button>
        </Space>
      </div>

      <Card size="small" style={{ marginBottom: 16 }}>
        <Space size="large" wrap>
          <div>
            <Text strong>Kỳ phân tích: </Text>
            <RangePicker value={dateRange} onChange={(dates) => dates && setDateRange([dates[0] as dayjs.Dayjs, dates[1] as dayjs.Dayjs])} allowClear={false} />
          </div>
          <Button type="primary" onClick={fetchData}>Chạy phân tích</Button>
        </Space>
      </Card>

      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={8}>
          <Card title="Phân bổ số lượng mã" size="small" style={{ height: '100%' }}>
            <ReactECharts option={pieOption} style={{ height: 250 }} />
          </Card>
        </Col>
        <Col span={16}>
          <Row gutter={[16, 16]}>
            <Col span={8}>
              <Card size="small" style={{ height: '100%', borderColor: '#52c41a' }}>
                <Statistic title="Lớp A (Giá trị cao)" value={report?.summary_a || 0} suffix="mã" valueStyle={{ color: '#52c41a' }} />
                <Text type="secondary" style={{ fontSize: 12 }}>~70% Tổng giá trị xuất kho</Text>
              </Card>
            </Col>
            <Col span={8}>
              <Card size="small" style={{ height: '100%', borderColor: '#faad14' }}>
                <Statistic title="Lớp B (Trung bình)" value={report?.summary_b || 0} suffix="mã" valueStyle={{ color: '#faad14' }} />
                <Text type="secondary" style={{ fontSize: 12 }}>~20% Tổng giá trị xuất kho</Text>
              </Card>
            </Col>
            <Col span={8}>
              <Card size="small" style={{ height: '100%', borderColor: '#ff4d4f' }}>
                <Statistic title="Lớp C (Giá trị thấp)" value={report?.summary_c || 0} suffix="mã" valueStyle={{ color: '#ff4d4f' }} />
                <Text type="secondary" style={{ fontSize: 12 }}>~10% Tổng giá trị xuất kho</Text>
              </Card>
            </Col>
          </Row>
        </Col>
      </Row>

      <Card bodyStyle={{ padding: 0 }}>
        <Table
          columns={columns}
          dataSource={report?.items || []}
          rowKey="material_id"
          loading={loading}
          pagination={{ pageSize: 20 }}
          size="small"
        />
      </Card>
    </div>
  );
}
