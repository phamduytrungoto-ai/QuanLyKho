import { useEffect, useState } from 'react';
import { Row, Col, Card, Statistic, Table, Tag, Space, Typography, Skeleton } from 'antd';
import {
  AppstoreOutlined,
  InboxOutlined,
  ExportOutlined,
  ImportOutlined,
  WarningOutlined,
  DollarOutlined,
  ToolOutlined,
  ExperimentOutlined,
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import { dashboardApi } from '../../api';
import { formatCurrency, formatNumber, STATUS_COLORS, STATUS_LABELS } from '../../utils/constants';
import type { DashboardSummary, RecentActivity } from '../../types';

const { Title, Text } = Typography;

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [activities, setActivities] = useState<RecentActivity[]>([]);
  const [lowStock, setLowStock] = useState<any[]>([]);
  const [inventoryValue, setInventoryValue] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [summaryData, activitiesData, lowStockData, valueData] = await Promise.all([
        dashboardApi.getSummary(),
        dashboardApi.getRecentActivities(8),
        dashboardApi.getLowStock(),
        dashboardApi.getInventoryValue(),
      ]);
      setSummary(summaryData);
      setActivities(activitiesData);
      setLowStock(lowStockData);
      setInventoryValue(valueData);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const kpiCards = [
    {
      title: 'Tổng vật tư',
      value: summary?.total_materials || 0,
      icon: <AppstoreOutlined />,
      gradient: 'var(--gradient-primary)',
      suffix: 'mã',
    },
    {
      title: 'Linh kiện',
      value: summary?.total_spare_parts || 0,
      icon: <ToolOutlined />,
      gradient: 'var(--gradient-success)',
      suffix: 'mã',
    },
    {
      title: 'Tiêu hao',
      value: summary?.total_consumables || 0,
      icon: <ExperimentOutlined />,
      gradient: 'var(--gradient-warning)',
      suffix: 'mã',
    },
    {
      title: 'Giá trị tồn kho',
      value: summary?.total_inventory_value || 0,
      icon: <DollarOutlined />,
      gradient: 'var(--gradient-dark)',
      formatter: true,
    },
    {
      title: 'Sắp hết hàng',
      value: summary?.low_stock_count || 0,
      icon: <WarningOutlined />,
      gradient: 'var(--gradient-danger)',
      suffix: 'mã',
    },
    {
      title: 'Phiếu nhập chờ duyệt',
      value: summary?.pending_receipts || 0,
      icon: <ImportOutlined />,
      gradient: 'linear-gradient(135deg, #722ed1 0%, #531dab 100%)',
      suffix: 'phiếu',
    },
    {
      title: 'Phiếu xuất chờ duyệt',
      value: summary?.pending_issues || 0,
      icon: <ExportOutlined />,
      gradient: 'linear-gradient(135deg, #13c2c2 0%, #08979c 100%)',
      suffix: 'phiếu',
    },
    {
      title: 'Nhập/Xuất hôm nay',
      value: `${summary?.today_receipts || 0} / ${summary?.today_issues || 0}`,
      icon: <InboxOutlined />,
      gradient: 'linear-gradient(135deg, #eb2f96 0%, #c41d7f 100%)',
      suffix: 'phiếu',
      rawValue: true,
    },
  ];

  // Inventory value pie chart
  const pieOption = {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0, textStyle: { fontSize: 12 } },
    series: [
      {
        type: 'pie',
        radius: ['45%', '70%'],
        avoidLabelOverlap: false,
        padAngle: 2,
        itemStyle: { borderRadius: 6 },
        label: { show: false },
        emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
        data: inventoryValue.map((v: any) => ({
          name: v.warehouse_name,
          value: parseFloat(v.total_value),
        })),
      },
    ],
  };

  const activityColumns = [
    {
      title: 'Loại',
      dataIndex: 'type',
      key: 'type',
      width: 80,
      render: (type: string) => (
        <Tag color={type === 'receipt' ? 'green' : 'blue'}>
          {type === 'receipt' ? 'Nhập' : 'Xuất'}
        </Tag>
      ),
    },
    { title: 'Số phiếu', dataIndex: 'number', key: 'number', width: 160 },
    { title: 'Ngày', dataIndex: 'date', key: 'date', width: 100 },
    {
      title: 'Trạng thái',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Tag color={STATUS_COLORS[status]}>{STATUS_LABELS[status] || status}</Tag>
      ),
    },
    { title: 'Người tạo', dataIndex: 'created_by', key: 'created_by' },
    { title: 'SL dòng', dataIndex: 'item_count', key: 'item_count', width: 80, align: 'center' as const },
  ];

  const lowStockColumns = [
    { title: 'Mã', dataIndex: 'material_code', key: 'code', width: 100 },
    { title: 'Tên vật tư', dataIndex: 'material_name', key: 'name' },
    {
      title: 'Tồn hiện tại',
      dataIndex: 'current_quantity',
      key: 'current',
      width: 100,
      render: (qty: number) => <Text type="danger" strong>{formatNumber(qty)}</Text>,
    },
    {
      title: 'Min',
      dataIndex: 'min_quantity',
      key: 'min',
      width: 80,
      render: (qty: number) => formatNumber(qty),
    },
    {
      title: 'Trạng thái',
      key: 'status',
      width: 100,
      render: (_: any, record: any) => (
        <Tag color={record.status === 'critical' ? 'red' : 'orange'}>
          {record.status === 'critical' ? 'Hết hàng' : 'Sắp hết'}
        </Tag>
      ),
    },
  ];

  if (loading) {
    return (
      <div className="dashboard-page">
        <Title level={3} className="page-title">Dashboard</Title>
        <Row gutter={[16, 16]}>
          {Array(8).fill(null).map((_, i) => (
            <Col xs={24} sm={12} md={8} lg={6} key={i}>
              <Card><Skeleton active paragraph={{ rows: 2 }} /></Card>
            </Col>
          ))}
        </Row>
      </div>
    );
  }

  return (
    <div className="dashboard-page">
      <Title level={3} className="page-title">📊 Dashboard</Title>

      {/* KPI Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        {kpiCards.map((kpi, index) => (
          <Col xs={24} sm={12} md={8} lg={6} key={index}>
            <Card className="kpi-card" hoverable>
              <div className="kpi-icon" style={{ background: kpi.gradient }}>
                {kpi.icon}
              </div>
              <div className="kpi-value">
                {kpi.rawValue
                  ? kpi.value
                  : kpi.formatter
                    ? formatCurrency(kpi.value as number)
                    : formatNumber(kpi.value as number)}
              </div>
              <div className="kpi-label">{kpi.title}</div>
            </Card>
          </Col>
        ))}
      </Row>

      {/* Charts & Tables */}
      <Row gutter={[16, 16]}>
        {/* Inventory Value */}
        <Col xs={24} lg={8}>
          <Card className="chart-card" title="💰 Giá trị tồn kho theo kho">
            {inventoryValue.length > 0 ? (
              <ReactECharts option={pieOption} style={{ height: 320 }} />
            ) : (
              <div style={{ textAlign: 'center', padding: 40, color: 'var(--text-tertiary)' }}>
                Chưa có dữ liệu
              </div>
            )}
          </Card>
        </Col>

        {/* Low Stock Alert */}
        <Col xs={24} lg={16}>
          <Card
            className="chart-card"
            title={
              <Space>
                <WarningOutlined style={{ color: 'var(--danger)' }} />
                <span>⚠️ Vật tư sắp hết hàng ({lowStock.length})</span>
              </Space>
            }
          >
            <Table
              columns={lowStockColumns}
              dataSource={lowStock}
              rowKey="material_id"
              pagination={false}
              size="small"
              scroll={{ y: 260 }}
              locale={{ emptyText: '✅ Tất cả vật tư đều đủ hàng' }}
            />
          </Card>
        </Col>

        {/* Recent Activities */}
        <Col xs={24}>
          <Card className="chart-card" title="📋 Hoạt động gần đây">
            <Table
              columns={activityColumns}
              dataSource={activities}
              rowKey={(r) => `${r.type}-${r.id}`}
              pagination={false}
              size="small"
              locale={{ emptyText: 'Chưa có hoạt động' }}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
}
