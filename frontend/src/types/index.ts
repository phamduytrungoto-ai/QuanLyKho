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
