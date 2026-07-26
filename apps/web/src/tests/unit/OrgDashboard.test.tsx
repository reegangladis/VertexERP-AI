import { render, screen } from '@testing-library/react';
import { OrgDashboard } from '@/pages/org/Dashboard';
import { NotificationProvider } from '@/store/NotificationContext';
import { expect, test, vi } from 'vitest';

vi.mock('@/services/apiClient', () => ({
  apiClient: {
    get: vi.fn().mockResolvedValue({ data: { data: [] } }),
    post: vi.fn().mockResolvedValue({ data: { data: [] } }),
  },
}));

// Mock recharts to avoid responsive container rendering warnings in test environment
vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: any) => <div>{children}</div>,
  AreaChart: ({ children }: any) => <div>{children}</div>,
  Area: () => <div />,
  XAxis: () => <div />,
  YAxis: () => <div />,
  Tooltip: () => <div />,
  CartesianGrid: () => <div />,
}));

test('renders OrgDashboard with title and seed action button', () => {
  render(
    <NotificationProvider>
      <OrgDashboard />
    </NotificationProvider>
  );

  expect(screen.getByText('Organization Console')).toBeInTheDocument();
  expect(screen.getByText('Reload Metrics')).toBeInTheDocument();
  expect(screen.getByText('Seed Enterprise Structure')).toBeInTheDocument();
});
