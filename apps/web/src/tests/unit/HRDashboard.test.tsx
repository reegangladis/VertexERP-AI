import { render, screen } from '@testing-library/react';
import { HRDashboard } from '@/pages/hr/Dashboard';
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
  AreaChart: ({ children }: any) => <div>{children}</div>,
  Area: () => <div />,
  XAxis: () => <div />,
  YAxis: () => <div />,
  Tooltip: () => <div />,
  CartesianGrid: () => <div />,
}));

test('renders HRDashboard with title and seed action button', () => {
  render(
    <NotificationProvider>
      <HRDashboard />
    </NotificationProvider>
  );

  expect(screen.getByText('HR Intelligence Cockpit')).toBeInTheDocument();
  expect(screen.getByText('Reload Metrics')).toBeInTheDocument();
  expect(screen.getByText('Seed HR Structure')).toBeInTheDocument();
});
