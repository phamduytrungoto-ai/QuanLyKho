/* ========== Material Types ========== */
export interface MaterialCategory {
  id: number;
  code: string;
  name: string;
  name_en?: string;
  name_ja?: string;
  description?: string;
  parent_id?: number;
  is_active: boolean;
}

export interface Unit {
  id: number;
  code: string;
  name: string;
  name_en?: string;
  name_ja?: string;
}

export interface Supplier {
  id: number;
  code: string;
  name: string;
  name_en?: string;
  contact_person?: string;
  phone?: string;
  email?: string;
  address?: string;
  tax_code?: string;
  lead_time_days?: number;
  payment_terms?: string;
  is_active: boolean;
}

export interface MaterialImage {
  id: number;
  image_url: string;
  is_primary: boolean;
}

export interface Material {
  id: number;
  code: string;
  barcode?: string;
  qr_code?: string;
  name: string;
  name_ja?: string;
  name_en?: string;
  model?: string;
  manufacturer?: string;
  supplier_id?: number;
  category_id?: number;
  unit_id?: number;
  material_type: string;
  price?: number;
  currency: string;
  lifetime_hours?: number;
  lead_time_days?: number;
  moq?: number;
  specifications?: Record<string, any>;
  datasheet_url?: string;
  description?: string;
  consumption_rate?: number;
  consumption_unit?: string;
  status: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  category?: MaterialCategory;
  unit?: Unit;
  supplier?: Supplier;
  images: MaterialImage[];
}

/* ========== Warehouse Types ========== */
export interface Location {
  id: number;
  warehouse_id: number;
  code: string;
  rack?: string;
  level?: string;
  bin?: string;
  full_path?: string;
  description?: string;
  is_active: boolean;
}

export interface Warehouse {
  id: number;
  code: string;
  name: string;
  name_en?: string;
  description?: string;
  warehouse_type: string;
  address?: string;
  manager?: string;
  is_active: boolean;
  locations: Location[];
}

/* ========== Inventory Types ========== */
export interface InventoryRecord {
  id: number;
  material_id: number;
  location_id: number;
  quantity: number;
  reserved_quantity: number;
  last_updated: string;
  material?: Material;
  location?: Location;
}

export interface InventoryAlert {
  material_id: number;
  material_code: string;
  material_name: string;
  warehouse_id?: number;
  warehouse_name?: string;
  current_quantity: number;
  min_quantity: number;
  max_quantity: number;
  status: string;
  lead_time_days?: number;
  avg_daily_usage?: number;
  days_until_stockout?: number;
}

/* ========== Receipt Types ========== */
export interface ReceiptItem {
  id?: number;
  receipt_id?: number;
  material_id: number;
  location_id?: number;
  quantity: number;
  unit_price?: number;
  total_price?: number;
  lot_number?: string;
  serial_number?: string;
  expiry_date?: string;
  note?: string;
}

export interface Receipt {
  id: number;
  receipt_number: string;
  receipt_date: string;
  receipt_type: string;
  supplier_id?: number;
  po_number?: string;
  invoice_number?: string;
  note?: string;
  status: string;
  total_amount?: number;
  created_by: number;
  approved_by?: number;
  approved_at?: string;
  created_at: string;
  items: ReceiptItem[];
}

/* ========== Issue Types ========== */
export interface IssueItem {
  id?: number;
  issue_id?: number;
  material_id: number;
  location_id?: number;
  quantity: number;
  unit_price?: number;
  total_price?: number;
  lot_number?: string;
  serial_number?: string;
  note?: string;
}

export interface Issue {
  id: number;
  issue_number: string;
  issue_date: string;
  issue_type: string;
  machine?: string;
  line?: string;
  shift?: string;
  receiver?: string;
  department?: string;
  reason?: string;
  work_order?: string;
  remark?: string;
  status: string;
  total_amount?: number;
  created_by: number;
  approved_by?: number;
  approved_at?: string;
  created_at: string;
  items: IssueItem[];
}

/* ========== User Types ========== */
export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: string;
  department?: string;
  phone?: string;
  is_active: boolean;
  created_at: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

/* ========== Dashboard Types ========== */
export interface DashboardSummary {
  total_materials: number;
  total_spare_parts: number;
  total_consumables: number;
  total_inventory_value: number;
  low_stock_count: number;
  pending_receipts: number;
  pending_issues: number;
  today_receipts: number;
  today_issues: number;
}

export interface RecentActivity {
  id: number;
  type: string;
  number: string;
  date: string;
  status: string;
  created_by: string;
  item_count: number;
}

/* ========== Common Types ========== */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

/* ========== Phase 2: Production Line Types ========== */
export interface ProductionLine {
  id: number;
  code: string;
  name: string;
  name_en?: string;
  area?: string;
  description?: string;
  manager?: string;
  is_active: boolean;
  created_at: string;
}

/* ========== Phase 2: Machine Types ========== */
export interface Machine {
  id: number;
  code: string;
  name: string;
  name_en?: string;
  machine_type: string;
  model?: string;
  manufacturer?: string;
  serial_number?: string;
  line_id?: number;
  location?: string;
  install_date?: string;
  warranty_expiry?: string;
  status: string;
  current_running_hours: number;
  last_maintenance_date?: string;
  next_maintenance_date?: string;
  maintenance_interval_hours?: number;
  specifications?: Record<string, any>;
  image_url?: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  line?: ProductionLine;
  parts_count: number;
  critical_parts_count: number;
}

export interface MachineDetail extends Machine {
  total_maintenance_count: number;
  total_downtime_hours: number;
}

/* ========== Phase 2: Machine Part Types ========== */
export interface MachinePart {
  id: number;
  machine_id: number;
  material_id: number;
  position?: string;
  lifetime_hours?: number;
  current_hours: number;
  lifetime_percentage: number;
  installed_date?: string;
  expected_replace_date?: string;
  last_replaced_date?: string;
  status: string;
  serial_number?: string;
  lot_number?: string;
  note?: string;
  created_at: string;
  updated_at: string;
  material_code?: string;
  material_name?: string;
}

/* ========== Phase 2: Maintenance Log Types ========== */
export interface MaintenanceLogItem {
  id: number;
  log_id: number;
  material_id: number;
  old_part_id?: number;
  quantity: number;
  action_type: string;
  note?: string;
  material_name?: string;
  material_code?: string;
}

export interface MaintenanceLog {
  id: number;
  log_number: string;
  machine_id: number;
  maintenance_type: string;
  maintenance_date: string;
  shift?: string;
  running_hours_at_time?: number;
  description: string;
  root_cause?: string;
  action_taken?: string;
  downtime_hours?: number;
  issue_id?: number;
  performed_by: number;
  status: string;
  created_at: string;
  performer_name?: string;
  machine_name?: string;
  machine_code?: string;
  items: MaintenanceLogItem[];
}

/* ========== Phase 2: Running Hours Types ========== */
export interface MachineRunningHour {
  id: number;
  machine_id: number;
  record_date: string;
  running_hours: number;
  cumulative_hours: number;
  shift?: string;
  recorded_by?: number;
  recorder_name?: string;
  note?: string;
  created_at: string;
}

/* ========== Phase 2: Parts Tracking Alerts ========== */
export interface PartLifetimeAlert {
  part_id: number;
  machine_id: number;
  machine_code: string;
  machine_name: string;
  line_name?: string;
  material_id: number;
  material_code: string;
  material_name: string;
  position?: string;
  lifetime_hours?: number;
  current_hours: number;
  lifetime_percentage: number;
  installed_date?: string;
  expected_replace_date?: string;
  status: string;
}

export interface LeadTimeAlert {
  material_id: number;
  material_code: string;
  material_name: string;
  supplier_name?: string;
  current_stock: number;
  min_quantity: number;
  lead_time_days?: number;
  avg_daily_usage?: number;
  days_until_stockout?: number;
  reorder_recommended: boolean;
}

export interface PartsOverview {
  total_parts_installed: number;
  active_parts: number;
  warning_parts: number;
  critical_parts: number;
  expired_parts: number;
  total_machines: number;
  running_machines: number;
  maintenance_this_month: number;
  total_downtime_this_month: number;
}

export interface MachineDashboardSummary {
  total_machines: number;
  running_machines: number;
  broken_machines: number;
  parts_critical_count: number;
  maintenance_this_month: number;
  avg_downtime_this_month: number;
}

/* ========== Phase 3: Reporting Types ========== */

export interface InventoryValuationItem {
  material_id: number;
  material_code: string;
  material_name: string;
  unit: string;
  opening_stock: number;
  opening_value: number;
  inward_qty: number;
  inward_value: number;
  outward_qty: number;
  outward_value: number;
  closing_stock: number;
  closing_value: number;
}

export interface InventoryValuationReport {
  start_date: string;
  end_date: string;
  warehouse_id?: number;
  items: InventoryValuationItem[];
  total_opening_value: number;
  total_inward_value: number;
  total_outward_value: number;
  total_closing_value: number;
}

export interface StockCardItem {
  transaction_date: string;
  transaction_type: string;
  reference_number?: string;
  inward_qty: number;
  outward_qty: number;
  balance: number;
  note?: string;
}

export interface StockCardReport {
  material_id: number;
  material_code: string;
  material_name: string;
  unit: string;
  start_date: string;
  end_date: string;
  opening_balance: number;
  closing_balance: number;
  transactions: StockCardItem[];
}

export interface AbcAnalysisItem {
  material_id: number;
  material_code: string;
  material_name: string;
  unit: string;
  total_usage_qty: number;
  total_usage_value: number;
  cumulative_value: number;
  cumulative_percentage: number;
  abc_class: string;
}

export interface AbcAnalysisReport {
  start_date: string;
  end_date: string;
  items: AbcAnalysisItem[];
  summary_a: number;
  summary_b: number;
  summary_c: number;
}

export interface MaintenanceCostItem {
  machine_id: number;
  machine_code: string;
  machine_name: string;
  line_name?: string;
  maintenance_count: number;
  total_downtime: number;
  parts_replaced_count: number;
  total_cost: number;
}

export interface MaintenanceCostReport {
  start_date: string;
  end_date: string;
  items: MaintenanceCostItem[];
  total_overall_cost: number;
}

