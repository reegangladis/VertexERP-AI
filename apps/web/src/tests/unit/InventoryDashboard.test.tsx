import { render, screen } from '@testing-library/react';
import { InventoryDashboard } from '@/pages/inventory/Dashboard';
import { NotificationProvider } from '@/store/NotificationContext';
import { expect, test, vi } from 'vitest';

vi.mock('@/services/apiClient', () => ({
  apiClient: {
    get: vi.fn().mockResolvedValue({ data: { data: [] } }),
    post: vi.fn().mockResolvedValue({ data: { data: [] } }),
  },
}));

vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: any) => <div>{children}</div>,
  BarChart: ({ children }: any) => <div>{children}</div>,
  Bar: () => <div />,
  XAxis: () => <div />,
  YAxis: () => <div />,
  Tooltip: () => <div />,
  CartesianGrid: () => <div />,
}));

test('renders InventoryDashboard with title and seed action button', () => {
  render(
    <NotificationProvider>
      <InventoryDashboard />
    </NotificationProvider>
  );

  expect(screen.getByText('Inventory & Warehouse Intelligence')).toBeInTheDocument();
  expect(screen.getByText('Reload Metrics')).toBeInTheDocument();
  expect(screen.getByText('Seed Inventory Structure')).toBeInTheDocument();
});
