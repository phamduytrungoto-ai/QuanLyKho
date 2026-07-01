import apiClient from './client';
import type { LoginResponse, User } from '../types';

export const authApi = {
  login: async (username: string, password: string): Promise<LoginResponse> => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    const { data } = await apiClient.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return data;
  },

  getMe: async (): Promise<User> => {
    const { data } = await apiClient.get('/auth/me');
    return data;
  },
};

export const usersApi = {
  list: async (params?: { page?: number; search?: string; role?: string }) => {
    const { data } = await apiClient.get('/users', { params });
    return data;
  },
  create: async (userData: any) => {
    const { data } = await apiClient.post('/users', userData);
    return data;
  },
  update: async (id: number, userData: any) => {
    const { data } = await apiClient.put(`/users/${id}`, userData);
    return data;
  },
  delete: async (id: number) => {
    await apiClient.delete(`/users/${id}`);
  },
};

export const materialsApi = {
  list: async (params?: Record<string, any>) => {
    const { data } = await apiClient.get('/materials', { params });
    return data;
  },
  get: async (id: number) => {
    const { data } = await apiClient.get(`/materials/${id}`);
    return data;
  },
  create: async (materialData: any) => {
    const { data } = await apiClient.post('/materials', materialData);
    return data;
  },
  update: async (id: number, materialData: any) => {
    const { data } = await apiClient.put(`/materials/${id}`, materialData);
    return data;
  },
  delete: async (id: number) => {
    await apiClient.delete(`/materials/${id}`);
  },
  listCategories: async () => {
    const { data } = await apiClient.get('/materials/categories');
    return data;
  },
  createCategory: async (catData: any) => {
    const { data } = await apiClient.post('/materials/categories', catData);
    return data;
  },
  listUnits: async () => {
    const { data } = await apiClient.get('/materials/units');
    return data;
  },
  createUnit: async (unitData: any) => {
    const { data } = await apiClient.post('/materials/units', unitData);
    return data;
  },
  listSuppliers: async (params?: { search?: string }) => {
    const { data } = await apiClient.get('/materials/suppliers', { params });
    return data;
  },
  createSupplier: async (supplierData: any) => {
    const { data } = await apiClient.post('/materials/suppliers', supplierData);
    return data;
  },
  updateSupplier: async (id: number, supplierData: any) => {
    const { data } = await apiClient.put(`/materials/suppliers/${id}`, supplierData);
    return data;
  },
};

export const warehousesApi = {
  list: async () => {
    const { data } = await apiClient.get('/warehouses');
    return data;
  },
  get: async (id: number) => {
    const { data } = await apiClient.get(`/warehouses/${id}`);
    return data;
  },
  create: async (warehouseData: any) => {
    const { data } = await apiClient.post('/warehouses', warehouseData);
    return data;
  },
  update: async (id: number, warehouseData: any) => {
    const { data } = await apiClient.put(`/warehouses/${id}`, warehouseData);
    return data;
  },
  listLocations: async (warehouseId: number) => {
    const { data } = await apiClient.get(`/warehouses/${warehouseId}/locations`);
    return data;
  },
  createLocation: async (warehouseId: number, locationData: any) => {
    const { data } = await apiClient.post(`/warehouses/${warehouseId}/locations`, locationData);
    return data;
  },
};

export const inventoryApi = {
  list: async (params?: Record<string, any>) => {
    const { data } = await apiClient.get('/inventory', { params });
    return data;
  },
  getAlerts: async () => {
    const { data } = await apiClient.get('/inventory/alerts');
    return data;
  },
  getMinMax: async (params?: { material_id?: number }) => {
    const { data } = await apiClient.get('/inventory/min-max', { params });
    return data;
  },
  createMinMax: async (minMaxData: any) => {
    const { data } = await apiClient.post('/inventory/min-max', minMaxData);
    return data;
  },
  adjust: async (adjustData: any) => {
    const { data } = await apiClient.post('/inventory/adjust', adjustData);
    return data;
  },
  getTransactions: async (params?: Record<string, any>) => {
    const { data } = await apiClient.get('/inventory/transactions', { params });
    return data;
  },
};

export const receiptsApi = {
  list: async (params?: Record<string, any>) => {
    const { data } = await apiClient.get('/receipts', { params });
    return data;
  },
  get: async (id: number) => {
    const { data } = await apiClient.get(`/receipts/${id}`);
    return data;
  },
  create: async (receiptData: any) => {
    const { data } = await apiClient.post('/receipts', receiptData);
    return data;
  },
  update: async (id: number, receiptData: any) => {
    const { data } = await apiClient.put(`/receipts/${id}`, receiptData);
    return data;
  },
  approve: async (id: number) => {
    const { data } = await apiClient.post(`/receipts/${id}/approve`);
    return data;
  },
  cancel: async (id: number) => {
    const { data } = await apiClient.post(`/receipts/${id}/cancel`);
    return data;
  },
};

export const issuesApi = {
  list: async (params?: Record<string, any>) => {
    const { data } = await apiClient.get('/issues', { params });
    return data;
  },
  get: async (id: number) => {
    const { data } = await apiClient.get(`/issues/${id}`);
    return data;
  },
  create: async (issueData: any) => {
    const { data } = await apiClient.post('/issues', issueData);
    return data;
  },
  update: async (id: number, issueData: any) => {
    const { data } = await apiClient.put(`/issues/${id}`, issueData);
    return data;
  },
  approve: async (id: number) => {
    const { data } = await apiClient.post(`/issues/${id}/approve`);
    return data;
  },
  cancel: async (id: number) => {
    const { data } = await apiClient.post(`/issues/${id}/cancel`);
    return data;
  },
};

export const dashboardApi = {
  getSummary: async () => {
    const { data } = await apiClient.get('/dashboard/summary');
    return data;
  },
  getInventoryValue: async () => {
    const { data } = await apiClient.get('/dashboard/inventory-value');
    return data;
  },
  getLowStock: async () => {
    const { data } = await apiClient.get('/dashboard/low-stock');
    return data;
  },
  getRecentActivities: async (limit = 10) => {
    const { data } = await apiClient.get('/dashboard/recent-activities', { params: { limit } });
    return data;
  },
};

// ==================== Phase 2 APIs ====================

export const linesApi = {
  list: async () => {
    const { data } = await apiClient.get('/machines/lines');
    return data;
  },
  create: async (lineData: any) => {
    const { data } = await apiClient.post('/machines/lines', lineData);
    return data;
  },
  update: async (id: number, lineData: any) => {
    const { data } = await apiClient.put(`/machines/lines/${id}`, lineData);
    return data;
  },
};

export const machinesApi = {
  list: async (params?: Record<string, any>) => {
    const { data } = await apiClient.get('/machines', { params });
    return data;
  },
  get: async (id: number) => {
    const { data } = await apiClient.get(`/machines/${id}`);
    return data;
  },
  create: async (machineData: any) => {
    const { data } = await apiClient.post('/machines', machineData);
    return data;
  },
  update: async (id: number, machineData: any) => {
    const { data } = await apiClient.put(`/machines/${id}`, machineData);
    return data;
  },
  // Parts
  listParts: async (machineId: number) => {
    const { data } = await apiClient.get(`/machines/${machineId}/parts`);
    return data;
  },
  installPart: async (machineId: number, partData: any) => {
    const { data } = await apiClient.post(`/machines/${machineId}/parts`, partData);
    return data;
  },
  updatePart: async (machineId: number, partId: number, partData: any) => {
    const { data } = await apiClient.put(`/machines/${machineId}/parts/${partId}`, partData);
    return data;
  },
  replacePart: async (machineId: number, partId: number, replaceData: any) => {
    const { data } = await apiClient.post(`/machines/${machineId}/parts/${partId}/replace`, replaceData);
    return data;
  },
  // Maintenance
  listMaintenance: async (machineId: number, params?: Record<string, any>) => {
    const { data } = await apiClient.get(`/machines/${machineId}/maintenance`, { params });
    return data;
  },
  createMaintenance: async (machineId: number, logData: any) => {
    const { data } = await apiClient.post(`/machines/${machineId}/maintenance`, logData);
    return data;
  },
  // Running Hours
  listRunningHours: async (machineId: number, days = 30) => {
    const { data } = await apiClient.get(`/machines/${machineId}/running-hours`, { params: { days } });
    return data;
  },
  recordRunningHours: async (machineId: number, hourData: any) => {
    const { data } = await apiClient.post(`/machines/${machineId}/running-hours`, hourData);
    return data;
  },
  // Timeline
  getTimeline: async (machineId: number, limit = 50) => {
    const { data } = await apiClient.get(`/machines/${machineId}/timeline`, { params: { limit } });
    return data;
  },
};

export const partsTrackingApi = {
  getLifetimeAlerts: async (params?: { threshold?: number; line_id?: number; machine_id?: number }) => {
    const { data } = await apiClient.get('/parts/lifetime-alerts', { params });
    return data;
  },
  getLeadTimeAlerts: async () => {
    const { data } = await apiClient.get('/parts/lead-time-alerts');
    return data;
  },
  getOverview: async () => {
    const { data } = await apiClient.get('/parts/overview');
    return data;
  },
  getDashboardSummary: async () => {
    const { data } = await apiClient.get('/parts/dashboard-summary');
    return data;
  },
};

// ==================== Phase 3 APIs ====================

export const reportsApi = {
  getInventoryValuation: async (params?: { start_date?: string; end_date?: string; warehouse_id?: number }) => {
    const { data } = await apiClient.get('/reports/inventory-valuation', { params });
    return data;
  },
  exportInventoryValuation: (params?: { start_date?: string; end_date?: string; warehouse_id?: number }) => {
    const qs = new URLSearchParams(params as any).toString();
    window.open(`http://localhost:8000/api/v1/reports/inventory-valuation?export=true&${qs}`);
  },

  getStockCard: async (params: { material_id: number; start_date?: string; end_date?: string }) => {
    const { data } = await apiClient.get('/reports/stock-card', { params });
    return data;
  },
  exportStockCard: (params: { material_id: number; start_date?: string; end_date?: string }) => {
    const qs = new URLSearchParams(params as any).toString();
    window.open(`http://localhost:8000/api/v1/reports/stock-card?export=true&${qs}`);
  },

  getAbcAnalysis: async (params?: { start_date?: string; end_date?: string }) => {
    const { data } = await apiClient.get('/reports/abc-analysis', { params });
    return data;
  },
  exportAbcAnalysis: (params?: { start_date?: string; end_date?: string }) => {
    const qs = new URLSearchParams(params as any).toString();
    window.open(`http://localhost:8000/api/v1/reports/abc-analysis?export=true&${qs}`);
  },

  getMaintenanceCost: async (params?: { start_date?: string; end_date?: string }) => {
    const { data } = await apiClient.get('/reports/maintenance-cost', { params });
    return data;
  },
  exportMaintenanceCost: (params?: { start_date?: string; end_date?: string }) => {
    const qs = new URLSearchParams(params as any).toString();
    window.open(`http://localhost:8000/api/v1/reports/maintenance-cost?export=true&${qs}`);
  },
};

