import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { LandingPage } from '@/pages/LandingPage';
import { expect, test, vi } from 'vitest';

// Mock the version service call
vi.mock('@/services/api', () => ({
  fetchVersion: vi.fn().mockResolvedValue({
    status: 'active',
    version: '1.3.0',
    environment: 'development',
    timestamp: '2026-07-24T22:38:00Z',
  }),
}));

test('renders landing page hero text and features grid', () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <LandingPage />
      </BrowserRouter>
    </QueryClientProvider>
  );

  // Assert Title is present
  expect(screen.getByText(/VertexERP/)).toBeInTheDocument();
  
  // Assert launching dashboard is present
  expect(screen.getByRole('link', { name: /Launch Core Console/i })).toBeInTheDocument();
});
