import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { KnowledgeDashboard, DocumentLibrary, CollectionsPage, UploadCenter, KnowledgeSearch, AIChat, ConversationHistoryPage } from '@/pages/rag';
import { expect, test, vi } from 'vitest';

vi.mock('@/services/ragService', () => ({
  ragService: {
    listCollections: vi.fn().mockResolvedValue([
      { id: 'c1', name: 'HR Policies', category: 'POLICY', description: 'HR Rules', tags: ['hr'] },
    ]),
    listDocuments: vi.fn().mockResolvedValue([
      { id: 'd1', title: 'Employee Guide', document_type: 'POLICY', format: 'PDF', file_size: 200000, approval_status: 'Indexed' },
    ]),
    search: vi.fn().mockResolvedValue({ results: [], total_found: 0 }),
    listSessions: vi.fn().mockResolvedValue([]),
    createSession: vi.fn().mockResolvedValue({ id: 's1', title: 'New Session', created_at: new Date().toISOString() }),
    sendMessage: vi.fn().mockResolvedValue({
      assistant_message: { id: 'm1', role: 'assistant', content: 'RAG Answer', citations: [] },
    }),
  },
}));

test('renders RAG Knowledge Dashboard cleanly', async () => {
  const queryClient = new QueryClient();
  render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <KnowledgeDashboard />
      </BrowserRouter>
    </QueryClientProvider>
  );

  expect(screen.getByText(/Enterprise RAG & Knowledge Intelligence/i)).toBeInTheDocument();
});

test('renders RAG Document Library Vault', async () => {
  const queryClient = new QueryClient();
  render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <DocumentLibrary />
      </BrowserRouter>
    </QueryClientProvider>
  );

  expect(screen.getByText(/Document Library Vault/i)).toBeInTheDocument();
});
