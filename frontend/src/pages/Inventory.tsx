import { useEffect, useState } from 'react';
import { Card, Table, Tag, Space, Select, Input, Button, Typography, App, Row, Col, Alert } from 'antd';
import { SearchOutlined, WarningOutlined, ReloadOutlined, FilterOutlined } from '@ant-design/icons';
import { inventoryApi, warehousesApi } from '../api';
import { MATERIAL_TYPES, formatNumber, formatCurrency } from '../utils/constants';
import type { InventoryRecord, InventoryAlert, Warehouse, PaginatedResponse } from '../types';

const { Title, Text } = Typography;

export default function InventoryPage() {
  const [data, setData] = useState<PaginatedResponse<InventoryRecord>>({ items: [], total: 0, page: 1, page_size: 20 });
  const [alerts, setAlerts] = useState<InventoryAlert[]>([]);
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ search: '', warehouse_id: undefined as number | undefined, material_type: '' });
  const { message: msg } = App.useApp();

  useEffect(() => { loadData(); loadAlerts(); loadWarehouses(); }, []);

  const loadData = async (page = 1) => {
    setLoading(true);
    try {
      const result = await inventoryApi.list({
        page, page_size: 20,
        search: filters.search || undefined,
        warehouse_id: filters.warehouse_id,
        material_type: filters.material_type || undefined,
      });
      setData(result);
    } catch { msg.error('Lỗi tải tồn kho'); }
    finally { setLoading(false); }
  };

  const loadAlerts = async () => {
    try { setAlerts(await inventoryApi.getAlerts()); } catch {}
  };

  const loadWarehouses = async () => {
    try { setWarehouses(await warehousesApi.list()); } catch {}
  };

  const columns = [
    { title: 'Mã vật tư', key: 'code', width: 100,
      render: (_: any, r: InventoryRecord) => <Text strong style={{ color: 'var(--primary)' }}>{r.material?.code}</Text> },
    { title: 'Tên vật tư', key: 'name', width: 200, ellipsis: true,
      render: (_: any, r: InventoryRecord) => r.material?.name },
    { title: 'Loại', key: 'type', width: 100,
      render: (_: any, r: InventoryRecord) => {
        const t = MATERIAL_TYPES.find((m) => m.value === r.material?.material_type);
        return <Tag color={t?.color}>{t?.label}</Tag>;
      },
    },
    { title: 'Vị trí', key: 'location', width: 220,
      render: (_: any, r: InventoryRecord) => <Text type="secondary">{r.location?.full_path || r.location?.code}</Text> },
    { title: 'Số lượng', key: 'qty', width: 100, align: 'right' as const,
      render: (_: any, r: InventoryRecord) => <Text strong>{formatNumber(r.quantity)}</Text> },
    { title: 'ĐVT', key: 'unit', width: 60,
      render: (_: any, r: InventoryRecord) => r.material?.unit?.code || '-' },
    { title: 'Giá trị', key: 'value', width: 130, align: 'right' as const,
      render: (_: any, r: InventoryRecord) => {
        if (!r.material?.price) return '-';
        return formatCurrency(r.quantity * r.material.price);
      },
    },
    { title: 'Cập nhật', dataIndex: 'last_updated', key: 'updated', width: 140,
      render: (d: string) => d ? new Date(d).toLocaleString('vi-VN') : '-' },
  ];

  const alertColumns = [
    { title: 'Mã', dataIndex: 'material_code', key: 'code', width: 90 },
    { title: 'Tên vật tư', dataIndex: 'material_name', key: 'name', width: 200, ellipsis: true },
    { title: 'Kho', dataIndex: 'warehouse_name', key: 'wh', width: 130 },
    { title: 'Tồn', dataIndex: 'current_quantity', key: 'current', width: 80, align: 'right' as const,
      render: (v: number) => <Text type="danger" strong>{formatNumber(v)}</Text> },
    { title: 'Min', dataIndex: 'min_quantity', key: 'min', width: 70, align: 'right' as const,
      render: (v: number) => formatNumber(v) },
    { title: 'Max', dataIndex: 'max_quantity', key: 'max', width: 70, align: 'right' as const,
      render: (v: number) => formatNumber(v) },
    { title: 'Còn (ngày)', dataIndex: 'days_until_stockout', key: 'days', width: 90, align: 'center' as const,
      render: (d: number | null) => d !== null && d !== undefined
        ? <Tag color={d <= 7 ? 'red' : d <= 14 ? 'orange' : 'default'}>{d} ngày</Tag>
        : '-'
    },
    { title: 'Trạng thái', dataIndex: 'status', key: 'status', width: 120,
      render: (status: string) => (
        <Tag color={status === 'below_min' ? 'red' : status === 'at_reorder_point' ? 'orange' : 'blue'}>
          {status === 'below_min' ? '🔴 Dưới Min' : status === 'at_reorder_point' ? '🟡 Cần mua' : '🔵 Vượt Max'}
        </Tag>
      ),
    },
  ];

  return (
    <div className="page-container">
      <div className="page-header">
        <Title level={3} style={{ margin: 0 }}>📊 Tồn kho</Title>
      </div>

      {/* Alerts */}
      {alerts.length > 0 && (
        <Alert
          message={<span><WarningOutlined /> <strong>{alerts.length} vật tư</strong> cần chú ý!</span>}
          type="warning"
          showIcon
          style={{ marginBottom: 16, borderRadius: 12 }}
          action={
            <Button size="small" onClick={() => document.getElementById('alerts-table')?.scrollIntoView({ behavior: 'smooth' })}>
              Xem chi tiết
            </Button>
          }
        />
      )}

      {/* Filter Bar */}
      <div className="filter-bar">
        <Input placeholder="Tìm mã, tên..." prefix={<SearchOutlined />} style={{ width: 240 }}
          value={filters.search} onChange={(e) => setFilters((f) => ({ ...f, search: e.target.value }))}
          onPressEnter={() => loadData()} allowClear />
        <Select placeholder="Kho" style={{ width: 160 }} allowClear value={filters.warehouse_id}
          onChange={(v) => setFilters((f) => ({ ...f, warehouse_id: v }))}
          options={warehouses.map((w) => ({ value: w.id, label: w.name }))} />
        <Select placeholder="Loại" style={{ width: 140 }} allowClear value={filters.material_type || undefined}
          onChange={(v) => setFilters((f) => ({ ...f, material_type: v || '' }))}
          options={MATERIAL_TYPES} />
        <Button icon={<FilterOutlined />} onClick={() => loadData()}>Lọc</Button>
        <Button icon={<ReloadOutlined />} onClick={() => { setFilters({ search: '', warehouse_id: undefined, material_type: '' }); loadData(); }}>Reset</Button>
      </div>

      {/* Inventory Table */}
      <Card className="data-table-card" style={{ marginBottom: 16 }}>
        <Table columns={columns} dataSource={data.items} rowKey="id" loading={loading}
          scroll={{ x: 1100 }} size="middle"
          pagination={{
            current: data.page, pageSize: data.page_size, total: data.total,
            showTotal: (t) => `Tổng: ${t} dòng`, onChange: (p) => loadData(p),
          }}
        />
      </Card>

      {/* Alerts Table */}
      {alerts.length > 0 && (
        <Card className="chart-card" id="alerts-table"
          title={<Space><WarningOutlined style={{ color: 'var(--danger)' }} /> Cảnh báo Min-Max ({alerts.length})</Space>}>
          <Table columns={alertColumns} dataSource={alerts} rowKey="material_id"
            pagination={false} size="small" scroll={{ y: 300 }} />
        </Card>
      )}
    </div>
  );
}
