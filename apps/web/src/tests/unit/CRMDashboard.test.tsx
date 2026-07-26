import { render, screen } from '@testing-library/react';
import { CRMDashboard } from '@/pages/crm/Dashboard';
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

test('renders CRMDashboard with title and seed action button', () => {
  render(
    <NotificationProvider>
      <CRMDashboard />
    </NotificationProvider>
  );

  expect(screen.getByText('CRM Intelligence Cockpit')).toBeInTheDocument();
  expect(screen.getByText('Reload Metrics')).toBeInTheDocument();
  expect(screen.getByText('Seed CRM Structure')).toBeInTheDocument();
});
