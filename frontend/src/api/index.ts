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
