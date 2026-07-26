import { render, screen, act } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { MonitoringDashboard } from '@/pages/observability/MonitoringDashboard';
import { NotificationProvider } from '@/store/NotificationContext';
import { expect, test, vi } from 'vitest';

vi.mock('@/services/observabilityService', () => ({
  observabilityService: {
    getSystemHealth: vi.fn().mockResolvedValue({
      status: 'healthy',
      version: '1.2.0',
      timestamp: '2026-07-26T12:00:00Z',
      uptime_ratio_percent: 99.98,
      services: []
    }),
    getAlerts: vi.fn().mockResolvedValue([]),
    getMetrics: vi.fn().mockResolvedValue([]),
    getBusinessMetrics: vi.fn().mockResolvedValue({}),
    getAiMetrics: vi.fn().mockResolvedValue({}),
    getLogs: vi.fn().mockResolvedValue({ logs: [], total_count: 0 }),
    getTraces: vi.fn().mockResolvedValue([]),
    getDependencyMap: vi.fn().mockResolvedValue([]),
    getEvents: vi.fn().mockResolvedValue([]),
  }
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

test('renders MonitoringDashboard and checks elements', async () => {
  await act(async () => {
    render(
      <BrowserRouter>
        <NotificationProvider>
          <MonitoringDashboard />
        </NotificationProvider>
      </BrowserRouter>
    );
  });

  expect(screen.getByText('Enterprise Monitoring Platform')).toBeInTheDocument();
  expect(screen.getByText('Refresh Telemetry')).toBeInTheDocument();
  expect(screen.getByText('Real-time Performance Latency')).toBeInTheDocument();
  expect(screen.getByText('Active Incidents')).toBeInTheDocument();
});
