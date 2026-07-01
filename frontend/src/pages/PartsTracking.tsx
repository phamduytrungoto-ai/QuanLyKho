import { useState, useEffect, useCallback } from 'react';
import {
  Card, Table, Button, Tag, Space, Row, Col, Typography, Statistic, Progress, Alert
} from 'antd';
import {
  ReloadOutlined, WarningOutlined, ShoppingCartOutlined, ExclamationCircleOutlined,
  CheckCircleOutlined
} from '@ant-design/icons';
import { partsTrackingApi } from '../api';
import type { PartLifetimeAlert, LeadTimeAlert, PartsOverview } from '../types';
import { getLifetimeColor, formatNumber } from '../utils/constants';

const { Title, Text } = Typography;

export default function PartsTrackingPage() {
  const [overview, setOverview] = useState<PartsOverview | null>(null);
  const [lifetimeAlerts, setLifetimeAlerts] = useState<PartLifetimeAlert[]>([]);
  const [leadTimeAlerts, setLeadTimeAlerts] = useState<LeadTimeAlert[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [ov, la, lta] = await Promise.all([
        partsTrackingApi.getOverview(),
        partsTrackingApi.getLifetimeAlerts({ threshold: 30 }),
        partsTrackingApi.getLeadTimeAlerts(),
      ]);
      setOverview(ov);
      setLifetimeAlerts(la);
      setLeadTimeAlerts(lta);
    } catch {
      // ignore
    }
    setLoading(false);
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const lifetimeColumns = [
    { title: 'Máy', key: 'machine', width: 200, render: (_: any, r: PartLifetimeAlert) => (
      <div>
        <Text strong>{r.machine_code}</Text>
        <div style={{ fontSize: 12, color: 'gray' }}>{r.machine_name}</div>
      </div>
    )},
    { title: 'Vị trí', dataIndex: 'position', key: 'pos', width: 150 },
    { title: 'Linh kiện', key: 'part', width: 250, render: (_: any, r: PartLifetimeAlert) => (
      <div>
        <Text strong>{r.material_code}</Text>
        <div style={{ fontSize: 12, color: 'gray' }}>{r.material_name}</div>
      </div>
    )},
    { title: 'Tuổi thọ còn lại', dataIndex: 'lifetime_percentage', key: 'life', width: 200, render: (val: number, r: PartLifetimeAlert) => (
      <div>
        <Progress percent={Number(val)} size="small" strokeColor={getLifetimeColor(val)} />
        <Text style={{ fontSize: 12 }} type="secondary">
          {formatNumber(r.lifetime_hours ? r.lifetime_hours - r.current_hours : 0)}h / {formatNumber(r.lifetime_hours)}h
        </Text>
      </div>
    )},
    { title: 'Trạng thái', key: 'status', width: 120, render: (_: any, r: PartLifetimeAlert) => {
      if (r.status === 'expired') return <Tag color="default">Hết hạn</Tag>;
      if (r.status === 'critical') return <Tag color="error" icon={<ExclamationCircleOutlined />}>Nguy hiểm</Tag>;
      if (r.status === 'warning') return <Tag color="warning" icon={<WarningOutlined />}>Cảnh báo</Tag>;
      return <Tag color="success">Tốt</Tag>;
    }},
    { title: 'Hành động', key: 'action', render: () => (
      <Button type="primary" size="small">Tạo phiếu xuất</Button>
    )}
  ];

  const leadTimeColumns = [
    { title: 'Vật tư', key: 'mat', width: 250, render: (_: any, r: LeadTimeAlert) => (
      <div>
        <Text strong>{r.material_code}</Text>
        <div style={{ fontSize: 12, color: 'gray' }}>{r.material_name}</div>
      </div>
    )},
    { title: 'Nhà cung cấp', dataIndex: 'supplier_name', key: 'sup', width: 150 },
    { title: 'Tồn kho', dataIndex: 'current_stock', key: 'stock', width: 100, render: (v: number) => <Text strong color="red">{formatNumber(v)}</Text> },
    { title: 'Mức Min', dataIndex: 'min_quantity', key: 'min', width: 100, render: (v: number) => formatNumber(v) },
    { title: 'Lead Time', dataIndex: 'lead_time_days', key: 'lead', width: 120, render: (v: number) => `${v} ngày` },
    { title: 'Ước tính Stockout', dataIndex: 'days_until_stockout', key: 'stockout', width: 150, render: (v: number, r: LeadTimeAlert) => (
      v !== null ? (
        <Text type={v <= (r.lead_time_days || 0) ? 'danger' : 'warning'} strong>
          Còn {v} ngày
        </Text>
      ) : 'Không rõ'
    )},
    { title: 'Hành động', key: 'action', render: () => (
      <Button type="primary" danger ghost size="small" icon={<ShoppingCartOutlined />}>Lên đơn PR</Button>
    )}
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={3} style={{ margin: 0 }}>
          <WarningOutlined style={{ marginRight: 8, color: '#faad14' }} />
          Theo dõi Cảnh báo Linh kiện
        </Title>
        <Button icon={<ReloadOutlined />} onClick={fetchData} loading={loading}>Làm mới</Button>
      </div>

      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={12} sm={8} md={4}>
          <Card size="small" bordered={false} style={{ background: '#f6ffed' }}>
            <Statistic title="Tổng linh kiện đang lắp" value={overview?.total_parts_installed || 0} prefix={<CheckCircleOutlined />} valueStyle={{ color: '#52c41a' }} />
          </Card>
        </Col>
        <Col xs={12} sm={8} md={5}>
          <Card size="small" bordered={false} style={{ background: '#fffbe6' }}>
            <Statistic title="Cảnh báo (< 30%)" value={overview?.warning_parts || 0} prefix={<WarningOutlined />} valueStyle={{ color: '#faad14' }} />
          </Card>
        </Col>
        <Col xs={12} sm={8} md={5}>
          <Card size="small" bordered={false} style={{ background: '#fff2f0' }}>
            <Statistic title="Nguy hiểm (< 10%)" value={overview?.critical_parts || 0} prefix={<ExclamationCircleOutlined />} valueStyle={{ color: '#ff4d4f' }} />
          </Card>
        </Col>
        <Col xs={12} sm={8} md={5}>
          <Card size="small" bordered={false} style={{ background: '#f5f5f5' }}>
            <Statistic title="Đã quá hạn (0%)" value={overview?.expired_parts || 0} valueStyle={{ color: '#8c8c8c' }} />
          </Card>
        </Col>
        <Col xs={12} sm={8} md={5}>
          <Card size="small" bordered={false}>
            <Statistic title="Máy đang chạy" value={overview?.running_machines || 0} suffix={`/ ${overview?.total_machines || 0}`} />
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={24}>
          <Card title="⚠️ Cảnh báo tuổi thọ linh kiện (Sắp hỏng)" style={{ marginBottom: 16 }} bodyStyle={{ padding: 0 }}>
            {lifetimeAlerts.length > 0 ? (
              <Table
                columns={lifetimeColumns}
                dataSource={lifetimeAlerts}
                rowKey="part_id"
                pagination={{ pageSize: 10 }}
                size="middle"
                loading={loading}
              />
            ) : (
              <div style={{ padding: 40, textAlign: 'center' }}>
                <Alert message="Không có linh kiện nào ở trạng thái cảnh báo" type="success" showIcon />
              </div>
            )}
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={24}>
          <Card title="🛒 Cảnh báo Lead Time (Cần đặt hàng ngay)" bodyStyle={{ padding: 0 }}>
            {leadTimeAlerts.length > 0 ? (
              <Table
                columns={leadTimeColumns}
                dataSource={leadTimeAlerts}
                rowKey="material_id"
                pagination={{ pageSize: 10 }}
                size="middle"
                loading={loading}
              />
            ) : (
              <div style={{ padding: 40, textAlign: 'center' }}>
                <Alert message="Không có vật tư nào cần đặt khẩn cấp" type="success" showIcon />
              </div>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
}
