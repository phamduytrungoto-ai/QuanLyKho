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
