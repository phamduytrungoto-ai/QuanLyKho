export const ROLES = {
  ADMIN: 'admin',
  DIRECTOR: 'director',
  MANAGER: 'manager',
  WAREHOUSE: 'warehouse',
  PRODUCTION: 'production',
  ENGINEERING: 'engineering',
  MAINTENANCE: 'maintenance',
  PURCHASING: 'purchasing',
  QA: 'qa',
} as const;

export const ROLE_LABELS: Record<string, string> = {
  admin: 'Admin',
  director: 'Director',
  manager: 'Manager',
  warehouse: 'Warehouse',
  production: 'Production',
  engineering: 'Engineering',
  maintenance: 'Maintenance',
  purchasing: 'Purchasing',
  qa: 'QA',
};

export const MATERIAL_TYPES = [
  { value: 'spare_part', label: 'Spare Part', color: '#1677ff' },
  { value: 'consumable', label: 'Consumable', color: '#52c41a' },
  { value: 'tool', label: 'Tool', color: '#faad14' },
  { value: 'chemical', label: 'Chemical', color: '#ff4d4f' },
];

export const RECEIPT_TYPES = [
  { value: 'purchase', label: 'Mua mới' },
  { value: 'repair_return', label: 'Sửa chữa trả về' },
  { value: 'transfer', label: 'Chuyển kho' },
  { value: 'return', label: 'Hoàn trả' },
  { value: 'stocktake', label: 'Nhập kiểm kê' },
];

export const ISSUE_TYPES = [
  { value: 'repair', label: 'Xuất sửa máy' },
  { value: 'production', label: 'Xuất sản xuất' },
  { value: 'testing', label: 'Xuất thử nghiệm' },
  { value: 'scrap', label: 'Xuất hủy' },
  { value: 'transfer', label: 'Xuất chuyển kho' },
];

export const STATUS_COLORS: Record<string, string> = {
  draft: 'default',
  pending_approval: 'processing',
  approved: 'success',
  cancelled: 'error',
  active: 'success',
  inactive: 'default',
  below_min: 'error',
  at_reorder_point: 'warning',
  above_max: 'processing',
  critical: 'error',
  warning: 'warning',
  ok: 'success',
};

export const STATUS_LABELS: Record<string, string> = {
  draft: 'Nháp',
  pending_approval: 'Chờ duyệt',
  approved: 'Đã duyệt',
  cancelled: 'Đã hủy',
  active: 'Đang dùng',
  inactive: 'Ngừng',
  discontinued: 'Ngừng SX',
};

export const WAREHOUSE_TYPES = [
  { value: 'main', label: 'Kho chính' },
  { value: 'spare_part', label: 'Kho linh kiện' },
  { value: 'chemical', label: 'Kho hóa chất' },
  { value: 'inspection', label: 'Kho chờ kiểm tra' },
  { value: 'defective', label: 'Kho hàng lỗi' },
  { value: 'return_supplier', label: 'Kho trả NCC' },
];

export const SHIFTS = [
  { value: 'A', label: 'Ca A (06:00-14:00)' },
  { value: 'B', label: 'Ca B (14:00-22:00)' },
  { value: 'C', label: 'Ca C (22:00-06:00)' },
];

export const formatCurrency = (value?: number | string): string => {
  if (!value) return '0';
  const num = typeof value === 'string' ? parseFloat(value) : value;
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(num);
};

export const formatNumber = (value?: number | string): string => {
  if (!value) return '0';
  const num = typeof value === 'string' ? parseFloat(value) : value;
  return new Intl.NumberFormat('vi-VN').format(num);
};

// ==================== Phase 2 Constants ====================

export const MACHINE_STATUSES = [
  { value: 'running', label: 'Đang chạy', color: '#52c41a', icon: '🟢' },
  { value: 'idle', label: 'Chờ', color: '#faad14', icon: '🟡' },
  { value: 'broken', label: 'Hỏng', color: '#ff4d4f', icon: '🔴' },
  { value: 'maintenance', label: 'Bảo trì', color: '#1677ff', icon: '🔵' },
  { value: 'decommissioned', label: 'Ngừng sử dụng', color: '#8c8c8c', icon: '⚪' },
];

export const MACHINE_STATUS_MAP: Record<string, { label: string; color: string; icon: string }> = {
  running: { label: 'Đang chạy', color: '#52c41a', icon: '🟢' },
  idle: { label: 'Chờ', color: '#faad14', icon: '🟡' },
  broken: { label: 'Hỏng', color: '#ff4d4f', icon: '🔴' },
  maintenance: { label: 'Bảo trì', color: '#1677ff', icon: '🔵' },
  decommissioned: { label: 'Ngừng sử dụng', color: '#8c8c8c', icon: '⚪' },
};

export const MACHINE_TYPES = [
  { value: 'smt', label: 'SMT' },
  { value: 'assembly', label: 'Lắp ráp' },
  { value: 'testing', label: 'Kiểm tra' },
  { value: 'packaging', label: 'Đóng gói' },
  { value: 'welding', label: 'Hàn' },
  { value: 'press', label: 'Ép/Dập' },
  { value: 'injection', label: 'Ép phun' },
  { value: 'cnc', label: 'CNC' },
  { value: 'other', label: 'Khác' },
];

export const MAINTENANCE_TYPES = [
  { value: 'corrective', label: 'Sửa chữa', color: '#ff4d4f' },
  { value: 'preventive', label: 'Bảo trì định kỳ', color: '#1677ff' },
  { value: 'predictive', label: 'Bảo trì dự đoán', color: '#722ed1' },
  { value: 'emergency', label: 'Khẩn cấp', color: '#fa541c' },
];

export const MAINTENANCE_TYPE_MAP: Record<string, { label: string; color: string }> = {
  corrective: { label: 'Sửa chữa', color: '#ff4d4f' },
  preventive: { label: 'Bảo trì ĐK', color: '#1677ff' },
  predictive: { label: 'Dự đoán', color: '#722ed1' },
  emergency: { label: 'Khẩn cấp', color: '#fa541c' },
};

export const PART_STATUS_MAP: Record<string, { label: string; color: string }> = {
  active: { label: 'Tốt', color: '#52c41a' },
  warning: { label: 'Cảnh báo', color: '#faad14' },
  critical: { label: 'Nguy hiểm', color: '#ff4d4f' },
  expired: { label: 'Hết hạn', color: '#8c8c8c' },
  replaced: { label: 'Đã thay', color: '#1677ff' },
};

export const getLifetimeColor = (percentage: number): string => {
  if (percentage <= 0) return '#8c8c8c';
  if (percentage <= 10) return '#ff4d4f';
  if (percentage <= 30) return '#fa8c16';
  if (percentage <= 50) return '#faad14';
  return '#52c41a';
};

