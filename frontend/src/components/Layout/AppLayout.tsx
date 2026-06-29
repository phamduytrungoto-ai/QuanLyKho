import { useState } from 'react';
import { Layout, Menu, Avatar, Dropdown, Space, Switch, Badge, Typography } from 'antd';
import {
  DashboardOutlined,
  AppstoreOutlined,
  DatabaseOutlined,
  InboxOutlined,
  ExportOutlined,
  ImportOutlined,
  UserOutlined,
  SettingOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  BellOutlined,
  MoonOutlined,
  SunOutlined,
  SafetyCertificateOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore, useAppStore } from '../../store';
import { ROLE_LABELS } from '../../utils/constants';
import type { MenuProps } from 'antd';

const { Sider, Header, Content } = Layout;
const { Text } = Typography;

interface AppLayoutProps {
  children: React.ReactNode;
}

export default function AppLayout({ children }: AppLayoutProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const { sidebarCollapsed, toggleSidebar, darkMode, toggleDarkMode } = useAppStore();

  const menuItems: MenuProps['items'] = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
    },
    {
      key: 'catalog',
      icon: <AppstoreOutlined />,
      label: 'Danh mục',
      children: [
        { key: '/materials', label: 'Vật tư' },
        { key: '/warehouses', label: 'Kho & Vị trí' },
      ],
    },
    {
      key: '/inventory',
      icon: <DatabaseOutlined />,
      label: 'Tồn kho',
    },
    {
      key: '/receipts',
      icon: <ImportOutlined />,
      label: 'Nhập kho',
    },
    {
      key: '/issues',
      icon: <ExportOutlined />,
      label: 'Xuất kho',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: 'Cài đặt',
      children: [
        { key: '/users', icon: <UserOutlined />, label: 'Người dùng' },
      ],
    },
  ];

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: `${user?.full_name}`,
      disabled: true,
    },
    {
      key: 'role',
      icon: <SafetyCertificateOutlined />,
      label: `Vai trò: ${ROLE_LABELS[user?.role || ''] || user?.role}`,
      disabled: true,
    },
    { type: 'divider' },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Đăng xuất',
      danger: true,
    },
  ];

  const handleMenuClick = (e: { key: string }) => {
    if (e.key === 'logout') {
      logout();
      navigate('/login');
    }
  };

  return (
    <Layout className="app-layout" style={{ minHeight: '100vh' }}>
      <Sider
        trigger={null}
        collapsible
        collapsed={sidebarCollapsed}
        width={260}
        collapsedWidth={80}
        style={{
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
        }}
      >
        <div className="sidebar-logo">
          <span className="logo-icon">🏭</span>
          {!sidebarCollapsed && <h2>Factory WMS</h2>}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          defaultOpenKeys={['catalog', 'settings']}
          items={menuItems}
          onClick={({ key }) => {
            if (key.startsWith('/')) navigate(key);
          }}
          style={{ borderRight: 0, marginTop: 8 }}
        />
      </Sider>

      <Layout style={{ marginLeft: sidebarCollapsed ? 80 : 260, transition: 'margin-left 0.2s' }}>
        <Header className="app-header">
          <div className="header-left">
            <span className="header-trigger" onClick={toggleSidebar}>
              {sidebarCollapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            </span>
          </div>

          <div className="header-right">
            <Switch
              checkedChildren={<MoonOutlined />}
              unCheckedChildren={<SunOutlined />}
              checked={darkMode}
              onChange={toggleDarkMode}
              style={{ marginRight: 4 }}
            />

            <Badge count={0} size="small">
              <BellOutlined style={{ fontSize: 18, cursor: 'pointer', color: 'var(--text-secondary)' }} />
            </Badge>

            <Dropdown menu={{ items: userMenuItems, onClick: handleMenuClick }} placement="bottomRight">
              <Space style={{ cursor: 'pointer', padding: '0 8px' }}>
                <Avatar
                  style={{ background: 'var(--gradient-primary)', cursor: 'pointer' }}
                  icon={<UserOutlined />}
                  size={32}
                />
                {!sidebarCollapsed && (
                  <Text strong style={{ fontSize: 13 }}>
                    {user?.full_name}
                  </Text>
                )}
              </Space>
            </Dropdown>
          </div>
        </Header>

        <Content className="app-content">{children}</Content>
      </Layout>
    </Layout>
  );
}
