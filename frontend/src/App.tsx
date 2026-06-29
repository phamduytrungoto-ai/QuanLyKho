import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, theme as antdTheme, App as AntdApp } from 'antd';
import viVN from 'antd/locale/vi_VN';
import { useAppStore, useAuthStore } from './store';
import { lightTheme, darkTheme } from './styles/theme';
import AppLayout from './components/Layout/AppLayout';
import LoginPage from './pages/Login';
import DashboardPage from './pages/Dashboard';
import MaterialsPage from './pages/Materials';
import WarehousesPage from './pages/Warehouses';
import InventoryPage from './pages/Inventory';
import ReceiptsPage from './pages/Receipts';
import IssuesPage from './pages/Issues';
import UsersPage from './pages/Users';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  const darkMode = useAppStore((s) => s.darkMode);

  return (
    <ConfigProvider
      theme={{
        ...(darkMode ? darkTheme : lightTheme),
        algorithm: darkMode ? antdTheme.darkAlgorithm : antdTheme.defaultAlgorithm,
      }}
      locale={viVN}
    >
      <AntdApp>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route
              path="/*"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <Routes>
                      <Route path="/" element={<Navigate to="/dashboard" replace />} />
                      <Route path="/dashboard" element={<DashboardPage />} />
                      <Route path="/materials" element={<MaterialsPage />} />
                      <Route path="/warehouses" element={<WarehousesPage />} />
                      <Route path="/inventory" element={<InventoryPage />} />
                      <Route path="/receipts" element={<ReceiptsPage />} />
                      <Route path="/issues" element={<IssuesPage />} />
                      <Route path="/users" element={<UsersPage />} />
                    </Routes>
                  </AppLayout>
                </ProtectedRoute>
              }
            />
          </Routes>
        </BrowserRouter>
      </AntdApp>
    </ConfigProvider>
  );
}
